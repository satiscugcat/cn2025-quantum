from sequence.topology.router_net_topo import RouterNetTopo
from graph_builder import is_high
import random


def get_node_path(topology: RouterNetTopo, source, destination):
    src_node = None
    dst_node = None
    for node in topology.nodes[topology.QUANTUM_ROUTER]:
        if source == node.name:
            src_node = node
        elif destination == node.name:
            dst_node = node

    if src_node is None or dst_node is None:
        return None

    path = []
    current_node = src_node
    while current_node.name != destination:
        path.append(current_node)
        table = current_node.network_manager.protocol_stack[0].forwarding_table
        if destination not in table.keys():
            return None
        else:
            next_hop = table[destination]
            for node in topology.nodes[topology.QUANTUM_ROUTER]:
                if next_hop == node.name:
                    current_node = node
                    break
    path.append(current_node)
    return path
    
def calculate_fidelity(topology: RouterNetTopo, source, destination):
    path = get_node_path(topology, source, destination)
    if path is None:
        return None
    resulting_fidelity=0.975
    for node in path[1:-1]:
        fidelity= node.get_components_by_type("MemoryArray")[0][0].raw_fidelity
        efficiency= node.get_components_by_type("MemoryArray")[0][0].efficiency
        resulting_fidelity = (resulting_fidelity-0.25)*((4*efficiency**2-1)/3)*((4*fidelity-1)/3) + 0.25
    return resulting_fidelity

def get_source_nodes(topology: RouterNetTopo):
    nodes=[]
    for node in topology.nodes[topology.QUANTUM_ROUTER]:
        if 's' in node.name:
            nodes.append(node)
    return nodes

def get_dest_nodes(topology: RouterNetTopo):
    nodes=[]
    for node in topology.nodes[topology.QUANTUM_ROUTER]:
        if 'd' in node.name:
            nodes.append(node)
    return nodes

def find_mean(num_list):
    n = len(num_list)
    if n == 0:
        return -1
    sum = 0
    for i in num_list:
        sum+=i
    return sum/n
def find_stddev(num_list):
    n = len(num_list)
    if n == 0:
        return -1
    mean = find_mean(num_list)
    sum = 0
    for i in num_list:
        sum+= (i-mean)**2
    return (sum/n)**0.5
def compare_fidelities(topology: RouterNetTopo):
    source_nodes = get_source_nodes(topology)
    dest_nodes = get_dest_nodes(topology)
    hp_nodes = list(filter(lambda x: is_high(x.name), dest_nodes))
    lp_nodes = list(filter(lambda x: not is_high(x.name), dest_nodes))
    print(f"High nodes:{list(map(lambda n: n.name, hp_nodes))}")
    print(f"Low nodes:{list(map(lambda n: n.name, hp_nodes))}")
    hp_fidelities = []
    lp_fidelities = []
    for source in source_nodes:
        for destination in hp_nodes:
            fidelity = calculate_fidelity(topology, source.name, destination.name)

            if fidelity is None:
                hp_fidelities.append(0)
            else:
                hp_fidelities.append(fidelity)
        for destination in lp_nodes:
            fidelity = calculate_fidelity(topology, source.name, destination.name)

            if fidelity is None:
                lp_fidelities.append(0)
            else:
                lp_fidelities.append(fidelity)

    print(f"Average high priority fidelity is: {find_mean(hp_fidelities)}")
    print(f"High priority fidelity standard deviation is: {find_stddev(hp_fidelities)}")

    print(f"Average low priority fidelity is: {find_mean(lp_fidelities)}")
    print(f"Low priority fidelity standard deviation is: {find_stddev(lp_fidelities)}")
