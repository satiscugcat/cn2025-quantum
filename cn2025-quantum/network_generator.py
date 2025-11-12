from sequence.topology.router_net_topo import RouterNetTopo
# from sequence.topology.node import Node, BSMNode, QuantumRouter
from sequence.topology.topology import Topology as Topo
import random
import math
from networkx import Graph, all_shortest_paths, shortest_simple_paths, exception, shortest_path_length
from graph_builder import is_high
import json
import os
def dict_to_topo(dictionary) -> RouterNetTopo:
    with open("stuff.json", "w") as f:
        json.dump(dictionary, f)
    nw=RouterNetTopo("stuff.json")
    os.remove("stuff.json")
    return nw
        
def set_parameters(topology: RouterNetTopo):
    # set memory parameters
    MEMO_FREQ = 2e3
    MEMO_EXPIRE = 0
    MEMO_EFFICIENCY = 1
    MEMO_FIDELITY = 0.975
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        memory_array = node.get_components_by_type("MemoryArray")[0] 
        memory_array.update_memory_params("frequency", MEMO_FREQ)
        memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)

    # set detector parameters
    DETECTOR_EFFICIENCY = 0.9
    DETECTOR_COUNT_RATE = 5e7
    DETECTOR_RESOLUTION = 100
    for node in topology.get_nodes_by_type(RouterNetTopo.BSM_NODE):
        bsm = node.get_components_by_type("SingleAtomBSM")[0]
        bsm.update_detectors_params("efficiency", DETECTOR_EFFICIENCY)
        bsm.update_detectors_params("count_rate", DETECTOR_COUNT_RATE)
        bsm.update_detectors_params("time_resolution", DETECTOR_RESOLUTION)
    # set entanglement swapping parameters
    SWAP_SUCC_PROB = 0.90
    SWAP_DEGRADATION = 0.99
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
    # set quantum channel parameters
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.get_qchannels():
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ


def set_efficiency_xi(topology: RouterNetTopo, xi: float):
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        MEMO_EFFICIENCY = 0.999 if random.random() < xi else 0.8
        memory_array = node.get_components_by_type("MemoryArray")[0]
        memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
def set_efficiency_alpha(topology: RouterNetTopo, alpha: float):
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        MEMO_EFFICIENCY = math.log(random.uniform(math.e**(0.8*alpha), math.e**(0.999*alpha)))/alpha
        memory_array = node.get_components_by_type("MemoryArray")[0]
        memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)


def clear_forwarding_tables(topology: RouterNetTopo):
    for src in topology.nodes[topology.QUANTUM_ROUTER]:
        routing_protocol = src.network_manager.protocol_stack[0]
        routing_protocol.forwarding_table = {}


def gen_tables_shortest_path(topology: RouterNetTopo):
    graph = Graph()
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):     
        fidelity= node.get_components_by_type("MemoryArray")[0][0].raw_fidelity
        efficiency= node.get_components_by_type("MemoryArray")[0][0].efficiency
        graph.add_node(node.name, fidelity=fidelity, efficiency=efficiency)
    costs = {}
    for qc in topology.qchannels:
        router, bsm = qc.sender.name, qc.receiver
        if bsm not in costs:
            costs[bsm] = [router, qc.distance]
        else:
            costs[bsm] = [router] + costs[bsm]
            costs[bsm][-1] += qc.distance
    graph.add_weighted_edges_from(costs.values()) 
    for src in topology.nodes[topology.QUANTUM_ROUTER]:
        for dst_name in graph.nodes:
            if src.name == dst_name:
                continue
            try:
                if dst_name > src.name:
                    paths = all_shortest_paths(graph, src.name, dst_name, weight=None)
                else:
                    paths = list(map(lambda l: l[::-1], all_shortest_paths(graph, dst_name, src.name, weight=None)))
                for path in paths:
                    resulting_fidelity = 0.975
                    for node in path[1:-1]:
                        resulting_fidelity = (resulting_fidelity-0.25)* ((4*graph.nodes[node]["efficiency"]**2 - 1)/3) * ((4*graph.nodes[node]["fidelity"] - 1)/3) + 0.25
                    if resulting_fidelity > 0.53:
                        next_hop = path[1]
                        # routing protocol locates at the bottom of the stack
                        routing_protocol = src.network_manager.protocol_stack[0]  # guarantee that [0] is the routing protocol?
                        routing_protocol.add_forwarding_rule(dst_name, next_hop)
                        break
            except exception.NetworkXNoPath:
                pass

def gen_tables_efficiency_cost(topology: RouterNetTopo, e_max=0.999, e_min=0.8):
    graph = Graph()
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):     
        fidelity= node.get_components_by_type("MemoryArray")[0][0].raw_fidelity
        efficiency= node.get_components_by_type("MemoryArray")[0][0].efficiency
        graph.add_node(node.name, fidelity=fidelity, efficiency=efficiency)
    costs = {}
    for qc in topology.qchannels:
        router, bsm = qc.sender.name, qc.receiver
        if bsm not in costs:
            costs[bsm] = [router, qc.distance]
        else:
            costs[bsm] = [router] + costs[bsm]
            costs[bsm][-1] += qc.distance
    graph.add_weighted_edges_from(costs.values()) 
    for src in topology.nodes[topology.QUANTUM_ROUTER]:
        for dst_name in graph.nodes:
            if src.name == dst_name:
                continue
            try:
                def cost(x, y, edge_dict):
                        math.e**(10*(graph.nodes[y]["efficiency"] - e_min)/(e_max-e_min))
                paths=None
                if dst_name > src.name:
                    paths = all_shortest_paths(graph, src.name, dst_name, weight=cost)
                else:
                    paths = list(map(lambda l: l[::-1], all_shortest_paths(graph, dst_name, src.name, weight=cost)))
                for path in paths:
                    resulting_fidelity = 0.975
                    for node in path[1:-1]:
                        resulting_fidelity = (resulting_fidelity-0.25)* ((4*graph.nodes[node]["efficiency"]**2 - 1)/3) * ((4*graph.nodes[node]["fidelity"] - 1)/3) + 0.25
                    if resulting_fidelity > 0.53:
                        next_hop = path[1]
                        # routing protocol locates at the bottom of the stack
                        routing_protocol = src.network_manager.protocol_stack[0]  # guarantee that [0] is the routing protocol?
                        routing_protocol.add_forwarding_rule(dst_name, next_hop)
                        break
            except exception.NetworkXNoPath:
                pass


def gen_tables_kshortest_path(topology: RouterNetTopo, source, destination, k = 10):
    graph = Graph()
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):     
        fidelity= node.get_components_by_type("MemoryArray")[0][0].raw_fidelity
        efficiency= node.get_components_by_type("MemoryArray")[0][0].efficiency
        graph.add_node(node.name, fidelity=fidelity, efficiency=efficiency)
    costs = {}
    for qc in topology.qchannels:
        router, bsm = qc.sender.name, qc.receiver
        if bsm not in costs:
            costs[bsm] = [router, qc.distance]
        else:
            costs[bsm] = [router] + costs[bsm]
            costs[bsm][-1] += qc.distance
    graph.add_weighted_edges_from(costs.values())
    if source==destination:
        return None
    try:
        paths=None
        if destination > source:
            paths=shortest_simple_paths(graph, source, destination, weight = None)
        else:
            paths=map(lambda l: l[::-1], shortest_simple_paths(graph, destination, source, weight = None))
        final_path = None
        min_fidelity = 10
        for (i, p) in enumerate(paths):
            if i>=k:
                break
            resulting_fidelity = 0.975
            for node in p[1:-1]:
                resulting_fidelity = (resulting_fidelity-0.25)* ((4*graph.nodes[node]["efficiency"]**2 - 1)/3) * ((4*graph.nodes[node]["fidelity"] - 1)/3) + 0.25
            if resulting_fidelity < min_fidelity  and resulting_fidelity > 0.53:
                min_fidelity = resulting_fidelity
                final_path = p
        if final_path == None:
            raise exception.NetworkXNoPath
        for (i, node_name) in enumerate(final_path[:-1]):
            for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
                if node.name == node_name:
                    node.network_manager.protocol_stack[0].update_forwarding_rule(destination, final_path[i+1])
    except exception.NetworkXNoPath:
        pass

def gen_tables_kxshortest_path(topology: RouterNetTopo, source, destination, k = 10, x=1):
    graph = Graph()
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):     
        fidelity= node.get_components_by_type("MemoryArray")[0][0].raw_fidelity
        efficiency= node.get_components_by_type("MemoryArray")[0][0].efficiency
        graph.add_node(node.name, fidelity=fidelity, efficiency=efficiency)
    costs = {}
    for qc in topology.qchannels:
        router, bsm = qc.sender.name, qc.receiver
        if bsm not in costs:
            costs[bsm] = [router, qc.distance]
        else:
            costs[bsm] = [router] + costs[bsm]
            costs[bsm][-1] += qc.distance
    graph.add_weighted_edges_from(costs.values())
    if source==destination:
        return None
    try:
        paths=None
        min_length=None
        if destination > source:
            paths=shortest_simple_paths(graph, source, destination, weight = None)
            min_length=shortest_path_length(graph, source, destination, weight = None)
        else:
            paths=map(lambda l: l[::-1], shortest_simple_paths(graph, destination, source, weight = None))
            min_length=shortest_path_length(graph, destination, source, weight = None)
        final_path = None
        min_fidelity = 10
        for (i, p) in enumerate(paths):
            if i>=k or abs(len(p) - (min_length+1)) > x:
                break
            resulting_fidelity = 0.975
            for node in p[1:-1]:
                resulting_fidelity = (resulting_fidelity-0.25)* ((4*graph.nodes[node]["efficiency"]**2 - 1)/3) * ((4*graph.nodes[node]["fidelity"] - 1)/3) + 0.25
            if resulting_fidelity < min_fidelity  and resulting_fidelity > 0.53:
                min_fidelity = resulting_fidelity
                final_path = p
        if final_path == None:
            raise exception.NetworkXNoPath
        for (i, node_name) in enumerate(final_path[:-1]):
            for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
                if node.name == node_name:
                    node.network_manager.protocol_stack[0].update_forwarding_rule(destination, final_path[i+1])
    except exception.NetworkXNoPath:
        pass

def gen_tables_kshortest_path_qos(topology: RouterNetTopo, source, destination, k = 10, is_high=is_high):
    graph = Graph()
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):     
        fidelity= node.get_components_by_type("MemoryArray")[0][0].raw_fidelity
        efficiency= node.get_components_by_type("MemoryArray")[0][0].efficiency
        graph.add_node(node.name, fidelity=fidelity, efficiency=efficiency)
    costs = {}
    for qc in topology.qchannels:
        router, bsm = qc.sender.name, qc.receiver
        if bsm not in costs:
            costs[bsm] = [router, qc.distance]
        else:
            costs[bsm] = [router] + costs[bsm]
            costs[bsm][-1] += qc.distance
    graph.add_weighted_edges_from(costs.values())
    if source==destination:
        return None
    try:
        paths=None
        if destination > source:
            paths=shortest_simple_paths(graph, source, destination, weight = None)
        else:
            paths=map(lambda l: l[::-1], shortest_simple_paths(graph, destination, source, weight = None))
        final_path=None
        if is_high(destination):
            min_fidelity = 10
            for (i, p) in enumerate(paths):
                if i>=k:
                    break
                resulting_fidelity = 0.975
                for node in p[1:-1]:
                    resulting_fidelity = (resulting_fidelity-0.25)* ((4*graph.nodes[node]["efficiency"]**2 - 1)/3) * ((4*graph.nodes[node]["fidelity"] - 1)/3) + 0.25
                if resulting_fidelity < min_fidelity  and resulting_fidelity > 0.53:
                    min_fidelity = resulting_fidelity
                    final_path = p
        else:
            max_fidelity = -1
            for (i, p) in enumerate(paths):
                if i>=k:
                    break
                resulting_fidelity = 0.975
                for node in p[1:-1]:
                    resulting_fidelity = (resulting_fidelity-0.25)* ((4*graph.nodes[node]["efficiency"]**2 - 1)/3) * ((4*graph.nodes[node]["fidelity"] - 1)/3) + 0.25
                if resulting_fidelity > max_fidelity  and resulting_fidelity > 0.53:
                    max_fidelity = resulting_fidelity
                    final_path = p
                
        if final_path == None:
            raise exception.NetworkXNoPath
        for (i, node_name) in enumerate(final_path[:-1]):
            for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
                if node.name == node_name:
                    node.network_manager.protocol_stack[0].update_forwarding_rule(destination, final_path[i+1])
    except exception.NetworkXNoPath:
        pass

def gen_tables_kxshortest_path_qos(topology: RouterNetTopo, source, destination, k = 10, x=1, is_high=is_high):
    graph = Graph()
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):     
        fidelity= node.get_components_by_type("MemoryArray")[0][0].raw_fidelity
        efficiency= node.get_components_by_type("MemoryArray")[0][0].efficiency
        graph.add_node(node.name, fidelity=fidelity, efficiency=efficiency)
    costs = {}
    for qc in topology.qchannels:
        router, bsm = qc.sender.name, qc.receiver
        if bsm not in costs:
            costs[bsm] = [router, qc.distance]
        else:
            costs[bsm] = [router] + costs[bsm]
            costs[bsm][-1] += qc.distance
    graph.add_weighted_edges_from(costs.values())
    if source==destination:
        return None
    try:
        paths=None
        min_length=None
        if destination > source:
            paths=shortest_simple_paths(graph, source, destination, weight = None)
            min_length=shortest_path_length(graph, source, destination, weight = None)
        else:
            paths=map(lambda l: l[::-1], shortest_simple_paths(graph, destination, source, weight = None))
            min_length=shortest_path_length(graph, destination, source, weight = None)
        final_path=None
        if is_high(destination):
            min_fidelity = 10
            for (i, p) in enumerate(paths):
                if i>=k or abs(len(p) - (min_length+1)) > x:
                    break
                resulting_fidelity = 0.975
                for node in p[1:-1]:
                    resulting_fidelity = (resulting_fidelity-0.25)* ((4*graph.nodes[node]["efficiency"]**2 - 1)/3) * ((4*graph.nodes[node]["fidelity"] - 1)/3) + 0.25
                if resulting_fidelity < min_fidelity  and resulting_fidelity > 0.53:
                    min_fidelity = resulting_fidelity
                    final_path = p
        else:
            max_fidelity = -1
            for (i, p) in enumerate(paths):
                if i>=k or abs(len(p) - (min_length+1)) > x:
                    break
                resulting_fidelity = 0.975
                for node in p[1:-1]:
                    resulting_fidelity = (resulting_fidelity-0.25)* ((4*graph.nodes[node]["efficiency"]**2 - 1)/3) * ((4*graph.nodes[node]["fidelity"] - 1)/3) + 0.25
                if resulting_fidelity > max_fidelity  and resulting_fidelity > 0.53:
                    max_fidelity = resulting_fidelity
                    final_path = p
                
        if final_path == None:
            raise exception.NetworkXNoPath
        for (i, node_name) in enumerate(final_path[:-1]):
            for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
                if node.name == node_name:
                    node.network_manager.protocol_stack[0].update_forwarding_rule(destination, final_path[i+1])
    except exception.NetworkXNoPath:
        pass
