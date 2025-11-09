from sequence.topology.router_net_topo import RouterNetTopo
# from sequence.topology.node import Node, BSMNode, QuantumRouter
from sequence.topology.topology import Topology as Topo
import random
import math
from networkx import Graph, all_shortest_paths, shortest_simple_paths

def set_parameters_eta(topology: RouterNetTopo, eta: float):
    # set memory parameters
    MEMO_FREQ = 2e3
    MEMO_EXPIRE = 0
    
    MEMO_FIDELITY = 0.975
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        MEMO_EFFICIENCY = 0.999 if random.random() < eta else 0.8
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

def set_parameters_alpha(topology: RouterNetTopo, alpha: float):
    # set memory parameters
    MEMO_FREQ = 2e3
    MEMO_EXPIRE = 0
    
    MEMO_FIDELITY = 0.975
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        MEMO_EFFICIENCY = math.log(random.uniform(math.e**(0.8*alpha), math.e**(0.999*alpha)))/alpha
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

def clear_forwarding_tables(topology: RouterNetTopo):
    for src in topology.nodes[topology.QUANTUM_ROUTER]:
        routing_protocol = src.network_manager.protocol_stack[0]
        routing_protocol.forwarding_table = {}

from networkx import Graph, all_shortest_paths

def gen_tables_shortest_path(topology: RouterNetTopo):
    graph = Graph()

    # === 1️⃣ Build node list safely ===
    for node in topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER):
        # Safely convert generator to list
        mem_arrays = list(node.get_components_by_type("MemoryArray"))
        if not mem_arrays or not mem_arrays[0]:
            print(f"[WARN] Node {node.name} has no MemoryArray — skipping.")
            continue

        mem = mem_arrays[0][0]
        fidelity = getattr(mem, "raw_fidelity", 0.95)
        efficiency = getattr(mem, "efficiency", 0.9)

        graph.add_node(node.name, fidelity=fidelity, efficiency=efficiency)

    # === 2️⃣ Build weighted edges safely ===
    costs = {}
    for qc in getattr(topology, "qchannels", []):
        try:
            router = qc.sender.name
            bsm = qc.receiver.name if hasattr(qc.receiver, "name") else str(qc.receiver)
            dist = getattr(qc, "distance", 0)

            if bsm not in costs:
                costs[bsm] = [router, dist]
            else:
                # Append and accumulate
                costs[bsm] = [router] + costs[bsm]
                costs[bsm][-1] += dist
        except Exception as e:
            print(f"[WARN] Could not process qchannel: {e}")
            continue

    # Convert all cost entries to weighted edges
    try:
        weighted_edges = []
        for value in costs.values():
            if len(value) >= 2:
                u, v, *rest = value
                w = rest[-1] if rest else 1
                weighted_edges.append((u, v, w))
        graph.add_weighted_edges_from(weighted_edges)
    except Exception as e:
        print(f"[WARN] Failed to add weighted edges: {e}")

    # === 3️⃣ Build routing tables ===
    routers = list(topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER))
    for src in routers:
        for dst in graph.nodes:
            if src.name == dst:
                continue

            try:
                # Shortest paths (ensure iterable)
                if dst > src.name:
                    paths = list(all_shortest_paths(graph, src.name, dst))
                else:
                    paths = [p[::-1] for p in all_shortest_paths(graph, dst, src.name)]

                for path in paths:
                    if len(path) < 2:
                        continue
                    resulting_fidelity = 0.975
                    for node_name in path[1:-1]:
                        node_data = graph.nodes[node_name]
                        eff = node_data.get("efficiency", 0.9)
                        fid = node_data.get("fidelity", 0.95)
                        resulting_fidelity = (resulting_fidelity - 0.25) * ((4 * eff**2 - 1)/3) * ((4 * fid - 1)/3) + 0.25

                    if resulting_fidelity > 0.53:
                        next_hop = path[1]
                        routing_protocol = src.network_manager.protocol_stack[0]
                        routing_protocol.add_forwarding_rule(dst, next_hop)
                        break

            except Exception as e:
                print(f"[ERR] Path building failed for {src.name}->{dst}: {e}")
                continue
import math
import itertools
import networkx as nx
from networkx import Graph, all_shortest_paths, shortest_simple_paths
from networkx.exception import NetworkXNoPath
from sequence.topology.router_net_topo import RouterNetTopo

def _build_graph_from_topology(topology: RouterNetTopo):
    """Helper: build a networkx Graph with node attrs fidelity/efficiency and weighted edges."""
    G = Graph()
    # add nodes
    for node in list(topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)):
        mem_arrays = list(node.get_components_by_type("MemoryArray"))
        if not mem_arrays or not mem_arrays[0]:
            # skip nodes without memory arrays
            continue
        mem = mem_arrays[0][0]
        fidelity = getattr(mem, "raw_fidelity", 0.95)
        efficiency = getattr(mem, "efficiency", 0.9)
        G.add_node(node.name, fidelity=fidelity, efficiency=efficiency)

    # build weighted edges safely
    weighted_edges = []
    for qc in getattr(topology, "qchannels", []):
        try:
            u = qc.sender.name
            # qc.receiver may be a node object or name (ensure name)
            v = qc.receiver.name if hasattr(qc.receiver, "name") else str(qc.receiver)
            w = getattr(qc, "distance", None)
            if w is None:
                # fallback to 1 if distance missing
                w = 1.0
            # ensure nodes exist in graph (skip otherwise)
            if u in G.nodes and v in G.nodes:
                weighted_edges.append((u, v, w))
        except Exception:
            # ignore malformed qchannel entry
            continue

    if weighted_edges:
        G.add_weighted_edges_from(weighted_edges)

    return G


def gen_tables_efficiency_cost(topology: RouterNetTopo):
    """Generate forwarding tables using an efficiency-based cost function for edges."""
    graph = _build_graph_from_topology(topology)

    # define cost function compatible with networkx weight callbacks: (u, v, attr) -> weight
    def eff_cost(u, v, attr):
        # attr is edge attribute dict in nx; we prefer to use node efficiency (v node)
        # avoid division by zero; map efficiency in [0.8, 0.999] to a cost
        eff_v = graph.nodes[v].get("efficiency", 0.9)
        # map efficiency to cost: higher efficiency -> lower cost.
        # use exponential mapping so slight changes make larger weight differences
        # clamp to [0.8, 0.999] to avoid extreme values
        eff_clamped = max(0.8, min(0.999, eff_v))
        # cost ~ exp(10*(0.999 - eff)/(0.999 - 0.8))
        exponent = 10.0 * (0.999 - eff_clamped) / (0.999 - 0.8)
        return math.exp(exponent)

    routers = list(topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER))
    for src in routers:
        routing_protocol = src.network_manager.protocol_stack[0]
        # ensure forwarding_table exists
        if not hasattr(routing_protocol, "forwarding_table"):
            routing_protocol.forwarding_table = {}
        for dst_name in graph.nodes:
            if src.name == dst_name:
                continue
            try:
                # all_shortest_paths accepts weight function if provided as "weight" parameter (NetworkX >= 2.6)
                # pass the eff_cost function as weight
                paths_gen = all_shortest_paths(graph, src.name, dst_name, weight=eff_cost)
                paths = list(paths_gen)
                for path in paths:
                    if len(path) < 2:
                        continue
                    resulting_fidelity = 0.975
                    for node_name in path[1:-1]:
                        node_data = graph.nodes[node_name]
                        eff = node_data.get("efficiency", 0.9)
                        fid = node_data.get("fidelity", 0.95)
                        resulting_fidelity = (resulting_fidelity - 0.25) * ((4 * eff**2 - 1) / 3) * ((4 * fid - 1) / 3) + 0.25

                    if resulting_fidelity > 0.53:
                        next_hop = path[1]
                        routing_protocol.add_forwarding_rule(dst_name, next_hop)
                        break
            except NetworkXNoPath:
                # no path between src and dst
                continue
            except Exception as e:
                # debug-friendly message but continue
                print(f"[ERR] gen_tables_efficiency_cost {src.name}->{dst_name}: {e}")
                continue


def gen_tables_kshortest_path(topology: RouterNetTopo, k=10):
    """Generate forwarding tables by inspecting up to k shortest simple paths and picking best fidelity."""
    graph = _build_graph_from_topology(topology)

    routers = list(topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER))
    for src in routers:
        routing_protocol = src.network_manager.protocol_stack[0]
        if not hasattr(routing_protocol, "forwarding_table"):
            routing_protocol.forwarding_table = {}
        for dst_name in graph.nodes:
            if src.name == dst_name:
                continue
            try:
                # shortest_simple_paths returns a generator; take first k
                paths_gen = shortest_simple_paths(graph, src.name, dst_name, weight=None)
                best_path = None
                best_fidelity = -1.0
                for i, path in enumerate(itertools.islice(paths_gen, k)):
                    if len(path) < 2:
                        continue
                    resulting_fidelity = 0.975
                    for node_name in path[1:-1]:
                        node_data = graph.nodes[node_name]
                        eff = node_data.get("efficiency", 0.9)
                        fid = node_data.get("fidelity", 0.95)
                        resulting_fidelity = (resulting_fidelity - 0.25) * ((4 * eff**2 - 1) / 3) * ((4 * fid - 1) / 3) + 0.25

                    # we want the *highest* resulting fidelity
                    if resulting_fidelity > best_fidelity:
                        best_fidelity = resulting_fidelity
                        best_path = path

                if best_path and best_fidelity > 0.53:
                    next_hop = best_path[1]
                    routing_protocol.add_forwarding_rule(dst_name, next_hop)
            except NetworkXNoPath:
                continue
            except Exception as e:
                print(f"[ERR] gen_tables_kshortest_path {src.name}->{dst_name}: {e}")
                continue


def gen_tables_kxshortest_path(topology: RouterNetTopo, k=10, x=1):
    """Pick among k-shortest paths whose length is within x of the minimum length, then choose best fidelity."""
    graph = _build_graph_from_topology(topology)

    routers = list(topology.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER))
    for src in routers:
        routing_protocol = src.network_manager.protocol_stack[0]
        if not hasattr(routing_protocol, "forwarding_table"):
            routing_protocol.forwarding_table = {}
        for dst_name in graph.nodes:
            if src.name == dst_name:
                continue
            try:
                # compute minimum path length first (unweighted)
                try:
                    min_length = nx.shortest_path_length(graph, src.name, dst_name, weight=None)
                except nx.NetworkXNoPath:
                    continue

                paths_gen = shortest_simple_paths(graph, src.name, dst_name, weight=None)
                final_path = None
                best_fidelity = -1.0
                for i, path in enumerate(itertools.islice(paths_gen, k)):
                    length = len(path) - 1  # number of edges
                    if abs(length - min_length) > x:
                        continue
                    resulting_fidelity = 0.975
                    for node_name in path[1:-1]:
                        node_data = graph.nodes[node_name]
                        eff = node_data.get("efficiency", 0.9)
                        fid = node_data.get("fidelity", 0.95)
                        resulting_fidelity = (resulting_fidelity - 0.25) * ((4 * eff**2 - 1) / 3) * ((4 * fid - 1) / 3) + 0.25

                    if resulting_fidelity > best_fidelity:
                        best_fidelity = resulting_fidelity
                        final_path = path

                if final_path and best_fidelity > 0.53:
                    next_hop = final_path[1]
                    routing_protocol.add_forwarding_rule(dst_name, next_hop)

            except NetworkXNoPath:
                continue
            except Exception as e:
                print(f"[ERR] gen_tables_kxshortest_path {src.name}->{dst_name}: {e}")
                continue
