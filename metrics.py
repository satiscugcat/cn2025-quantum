from sequence.topology.router_net_topo import RouterNetTopo
import random
def generate_sd_pairs(n):
    sources=sorted(list(map(lambda n: f"s{n}", range(1, n+1))),key= lambda _:random.random())
    dests=sorted(list(map(lambda n: f"d{n}", range(1, n+1))),key= lambda _:random.random())
    return zip(sources,dests)

def blocking_probability(topology: RouterNetTopo, n=5):
    tl = topology.get_timeline()
    pairs=generate_sd_pairs(n)
    requesting_nodes=[]
    for router in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        print(router.network_manager.protocol_stack[0].forwarding_table)
    for (sname,dname) in pairs:
        node1=node2=None
        for router in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
            if router.name == sname:
                node1 = router
            elif router.name == dname:
                node2 = router
        nm = node1.network_manager
        nm.request(dname, start_time=1e12, end_time=10e12, memory_size=25, target_fidelity=0.9)
        requesting_nodes.append(node1)
    
    tl.init()
    tl.run()

    for node in requesting_nodes():
        print(node, "memories")
        print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
        for info in node.resource_manager.memory_manager:
            print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node), str(info.fidelity), str(info.entangle_time * 1e-12)))


def measure_fidelity(topology: RouterNetTopo, start_node, end_node):
    pass

def fairness(topology: RouterNetTopo):
    tl = topology.get_timeline()
    pass
