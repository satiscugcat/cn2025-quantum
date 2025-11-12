from graph_builder import *
from network_generator import *
from metrics import *

higher_better=0
lower_better=0
for i in range(1,101):
    nw1=dict_to_topo(regular_gen(6, frac=0.5))
    set_parameters(nw1)
    set_efficiency_xi(nw1, 0.9)
    mean_hp, stddev_hp, mean_lp, stddev_lp = evaluate_kx0shortest_path_qos(nw1)
    if mean_hp > mean_lp:
        higher_better+=1
    else:
        lower_better+=1

print(higher_better, lower_better)
