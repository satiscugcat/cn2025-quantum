import json
from graph_builder import *
from network_generator import *
from metrics import *
from sequence.topology.router_net_topo import RouterNetTopo

with open("regular_topo.json", "w") as f:
    json.dump(regular_gen(3), f, indent=4)

with open("waxman_topo.json", "w") as f:
    json.dump(waxman_gen(3), f, indent=4)

nw1 = RouterNetTopo("regular_topo.json")
nw2 = RouterNetTopo("waxman_topo.json")

set_parameters_eta(nw1, 0.9)

clear_forwarding_tables(nw1)
gen_tables_shortest_path(nw1)
# the start and end nodes may be edited as desired 
start_node_name = "s1"
end_node_name = "d1"
node1 = node2 = None

for router in nw1.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
    if router.name == start_node_name:
        node1 = router
    elif router.name == end_node_name:
        node2 = router
for router in nw1.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        print(router.name, router.network_manager.protocol_stack[0].forwarding_table)
nm = node1.network_manager
nm.request(end_node_name, start_time=1e12, end_time=10e12, memory_size=25, target_fidelity=0.53)
tl = nw1.get_timeline()
tl.init()
tl.run()

print(node1, "memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
for info in node1.resource_manager.memory_manager:
		print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index),
                                         str(info.remote_node),
                                         str(info.fidelity),
                                         str(info.entangle_time * 1e-12)))

# blocking_probability(nw1)


# clear_forwarding_tables(nw1)
# gen_tables_efficiency_cost(nw1)

# clear_forwarding_tables(nw1)
# gen_tables_kshortest_path(nw1)

# clear_forwarding_tables(nw1)
# gen_tables_kxshortest_path(nw1)

# set_parameters_eta(nw2, 0.9)

# clear_forwarding_tables(nw2)
# gen_tables_shortest_path(nw2)

# clear_forwarding_tables(nw2)
# gen_tables_efficiency_cost(nw2)

# clear_forwarding_tables(nw2)
# gen_tables_kshortest_path(nw2)

# clear_forwarding_tables(nw2)
# gen_tables_kxshortest_path(nw2)

