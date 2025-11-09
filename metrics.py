from sequence.topology.router_net_topo import RouterNetTopo
import random
def generate_sd_pairs(n):
    sources=sorted(list(map(lambda n: f"s{n}", range(1, n+1))),key=random.random())
    dests=sorted(list(map(lambda n: f"d{n}", range(1, n+1))),key=random.random())
    return zip(sources,dests)

def blocking_probability(topology: RouterNetTopo, n=5):
    tl = topology.get_timeline()
    pairs=generate_sd_pairs(n)
    requesting_nodes=[]
    for (sname,dname) in pairs:
        s=n=None
        for router in network_topo.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
            if router.name == start_node_name:
                node1 = router
            elif router.name == end_node_name:
                node2 = router
        pass


def measure_fidelity(topology: RouterNetTopo, start_node, end_node):
    pass

def fairness(topology: RouterNetTopo):
    tl = topology.get_timeline()
    pass
