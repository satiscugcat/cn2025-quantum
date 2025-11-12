from sequence.topology.router_net_topo import RouterNetTopo
from graph_builder import is_high
import random
from network_generator import *

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
        return 0
    resulting_fidelity=0.975
    for node in path[1:-1]:
        fidelity= node.get_components_by_type("MemoryArray")[0][0].raw_fidelity
        efficiency= node.get_components_by_type("MemoryArray")[0][0].efficiency
        resulting_fidelity = (resulting_fidelity-0.25)*((4*efficiency**2-1)/3)*((4*fidelity-1)/3) + 0.25
    return resulting_fidelity
def print_forwarding_tables(topology: RouterNetTopo):
    for node in topology.nodes[topology.QUANTUM_ROUTER]:
        print(node.name, node.network_manager.protocol_stack[0].forwarding_table)
        
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

def evaluate_shortest_path(topology: RouterNetTopo, is_high=is_high, get_source_nodes=get_source_nodes, get_dest_nodes=get_dest_nodes):
    clear_forwarding_tables(topology)
    gen_tables_shortest_path(topology)
    source_nodes = get_source_nodes(topology)
    dest_nodes = get_dest_nodes(topology)
    hp_nodes = list(filter(lambda x: is_high(x.name), dest_nodes))
    lp_nodes = list(filter(lambda x: not is_high(x.name), dest_nodes))
    hp_fidelities = []
    lp_fidelities = []
    for source in source_nodes:
        for destination in hp_nodes:
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            hp_fidelities.append(fidelity)
        for destination in lp_nodes:
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            lp_fidelities.append(fidelity)


    return (find_mean(hp_fidelities), find_stddev(hp_fidelities), find_mean(lp_fidelities), find_stddev(lp_fidelities))


def evaluate_efficiency_cost(topology: RouterNetTopo, is_high=is_high, get_source_nodes=get_source_nodes, get_dest_nodes=get_dest_nodes):
    clear_forwarding_tables(topology)
    gen_tables_efficiency_cost(topology)
    source_nodes = get_source_nodes(topology)
    dest_nodes = get_dest_nodes(topology)
    hp_nodes = list(filter(lambda x: is_high(x.name), dest_nodes))
    lp_nodes = list(filter(lambda x: not is_high(x.name), dest_nodes))
    hp_fidelities = []
    lp_fidelities = []
    for source in source_nodes:
        for destination in hp_nodes:
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            hp_fidelities.append(fidelity)
        for destination in lp_nodes:
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            lp_fidelities.append(fidelity)


    return (find_mean(hp_fidelities), find_stddev(hp_fidelities), find_mean(lp_fidelities), find_stddev(lp_fidelities))

def evaluate_kshortest_path(topology: RouterNetTopo, is_high=is_high, get_source_nodes=get_source_nodes, get_dest_nodes=get_dest_nodes):
    clear_forwarding_tables(topology)
    source_nodes = get_source_nodes(topology)
    dest_nodes = get_dest_nodes(topology)
    hp_nodes = list(filter(lambda x: is_high(x.name), dest_nodes))
    lp_nodes = list(filter(lambda x: not is_high(x.name), dest_nodes))
    hp_fidelities = []
    lp_fidelities = []
    for source in source_nodes:
        for destination in hp_nodes:
            gen_tables_kshortest_path(topology, source.name, destination.name)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            hp_fidelities.append(fidelity)
        for destination in lp_nodes:
            gen_tables_kshortest_path(topology, source.name, destination.name)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            lp_fidelities.append(fidelity)


    return (find_mean(hp_fidelities), find_stddev(hp_fidelities), find_mean(lp_fidelities), find_stddev(lp_fidelities))

def evaluate_kxshortest_path(topology: RouterNetTopo, is_high=is_high, get_source_nodes=get_source_nodes, get_dest_nodes=get_dest_nodes):
    clear_forwarding_tables(topology)
    source_nodes = get_source_nodes(topology)
    dest_nodes = get_dest_nodes(topology)
    hp_nodes = list(filter(lambda x: is_high(x.name), dest_nodes))
    lp_nodes = list(filter(lambda x: not is_high(x.name), dest_nodes))
    hp_fidelities = []
    lp_fidelities = []
    for source in source_nodes:
        for destination in hp_nodes:
            gen_tables_kxshortest_path(topology, source.name, destination.name)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            hp_fidelities.append(fidelity)
        for destination in lp_nodes:
            gen_tables_kxshortest_path(topology, source.name, destination.name)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            lp_fidelities.append(fidelity)


    return (find_mean(hp_fidelities), find_stddev(hp_fidelities), find_mean(lp_fidelities), find_stddev(lp_fidelities))

def evaluate_kx0shortest_path(topology: RouterNetTopo, is_high=is_high, get_source_nodes=get_source_nodes, get_dest_nodes=get_dest_nodes):
    clear_forwarding_tables(topology)
    source_nodes = get_source_nodes(topology)
    dest_nodes = get_dest_nodes(topology)
    hp_nodes = list(filter(lambda x: is_high(x.name), dest_nodes))
    lp_nodes = list(filter(lambda x: not is_high(x.name), dest_nodes))
    hp_fidelities = []
    lp_fidelities = []
    for source in source_nodes:
        for destination in hp_nodes:
            gen_tables_kxshortest_path(topology, source.name, destination.name, x=0)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            hp_fidelities.append(fidelity)
        for destination in lp_nodes:
            gen_tables_kxshortest_path(topology, source.name, destination.name, x=0)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            lp_fidelities.append(fidelity)


    return (find_mean(hp_fidelities), find_stddev(hp_fidelities), find_mean(lp_fidelities), find_stddev(lp_fidelities))


def evaluate_kshortest_path_qos(topology: RouterNetTopo, is_high=is_high, get_source_nodes=get_source_nodes, get_dest_nodes=get_dest_nodes):
    clear_forwarding_tables(topology)
    source_nodes = get_source_nodes(topology)
    dest_nodes = get_dest_nodes(topology)
    hp_nodes = list(filter(lambda x: is_high(x.name), dest_nodes))
    lp_nodes = list(filter(lambda x: not is_high(x.name), dest_nodes))
    hp_fidelities = []
    lp_fidelities = []
    for source in source_nodes:
        for destination in hp_nodes:
            gen_tables_kshortest_path_qos(topology, source.name, destination.name)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            hp_fidelities.append(fidelity)
        for destination in lp_nodes:
            gen_tables_kshortest_path_qos(topology, source.name, destination.name)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            lp_fidelities.append(fidelity)


    return (find_mean(hp_fidelities), find_stddev(hp_fidelities), find_mean(lp_fidelities), find_stddev(lp_fidelities))

def evaluate_kxshortest_path_qos(topology: RouterNetTopo, is_high=is_high, get_source_nodes=get_source_nodes, get_dest_nodes=get_dest_nodes):
    clear_forwarding_tables(topology)
    source_nodes = get_source_nodes(topology)
    dest_nodes = get_dest_nodes(topology)
    hp_nodes = list(filter(lambda x: is_high(x.name), dest_nodes))
    lp_nodes = list(filter(lambda x: not is_high(x.name), dest_nodes))
    hp_fidelities = []
    lp_fidelities = []
    for source in source_nodes:
        for destination in hp_nodes:
            gen_tables_kxshortest_path_qos(topology, source.name, destination.name)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            hp_fidelities.append(fidelity)
        for destination in lp_nodes:
            gen_tables_kxshortest_path_qos(topology, source.name, destination.name)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            lp_fidelities.append(fidelity)


    return (find_mean(hp_fidelities), find_stddev(hp_fidelities), find_mean(lp_fidelities), find_stddev(lp_fidelities))


def evaluate_kx0shortest_path_qos(topology: RouterNetTopo, is_high=is_high, get_source_nodes=get_source_nodes, get_dest_nodes=get_dest_nodes):
    clear_forwarding_tables(topology)
    source_nodes = get_source_nodes(topology)
    dest_nodes = get_dest_nodes(topology)
    hp_nodes = list(filter(lambda x: is_high(x.name), dest_nodes))
    lp_nodes = list(filter(lambda x: not is_high(x.name), dest_nodes))
    hp_fidelities = []
    lp_fidelities = []
    for source in source_nodes:
        for destination in hp_nodes:
            gen_tables_kxshortest_path_qos(topology, source.name, destination.name, x=0)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            hp_fidelities.append(fidelity)
        for destination in lp_nodes:
            gen_tables_kxshortest_path_qos(topology, source.name, destination.name, x=0)
            fidelity = calculate_fidelity(topology, source.name, destination.name)
            lp_fidelities.append(fidelity)


    return (find_mean(hp_fidelities), find_stddev(hp_fidelities), find_mean(lp_fidelities), find_stddev(lp_fidelities))
