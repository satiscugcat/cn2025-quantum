import networkx as nx
import random
def regular_gen(n: int, frac=0.3) -> dict:
    '''
    Returns a network topology following a regular graph structure in the form of a dict.
    
    A "regular" graph is a graph with n sources, n destinations,
    and n**2 repeaters. Connected in such a fasion that there are n layers
    of n repeaters placed between the source and the destination.

    For eg. n = 2, a regular graph looks like this.

    s1 -- n11 -- n12 -- d1
          |      |
    s2 -- n21 -- n22 -- d2

    For n = 3,

       s1-n11----n13----n13-d1   
          | \\    | \\    | \\   
       s3-|--n31-|--n32-|--n33-d3
          | /    | /    | /   
       s2-n23----n23----n23-d2   

    '''

    # Dictionary structure referenced from: https://sequence-rtd-tutorial.readthedocs.io/en/latest/tutorial/chapter5/network_manager.html#step-1-create-the-network-configuration-file
    seed = 0
    graph = {
        "is_parallel": False,
        "stop_time": 2000000000000,
        "nodes": [],
        "qconnections": [],
        "cconnections": []
    }

    high_quality=random.sample(range(1, n+1), round(n*frac))
    
    # Generating all nodes.
    for i in range(1, n+1):
        src_dict = {
            "name": ("s"+str(i)),
            "type": "QuantumRouter",
            "seed": seed,
            "memo_size": 50
        }
        graph["nodes"].append(src_dict)
        seed+=1
        
        dest_dict = {
            "name": (("hd" if i in high_quality else "d") +str(i)),
            "type": "QuantumRouter",
            "seed": seed,
            "memo_size": 50
        }
        graph["nodes"].append(dest_dict)
        seed+=1
        
        for j in range(1, n+1):
            node_dict = {
                "name": ("n"+str(i)+"_"+str(j)),
                "type": "QuantumRouter",
                "seed": seed,
                "memo_size": 50
            }
            graph["nodes"].append(node_dict)
            seed+=1

    # Generating all edges.
    for i in range(1,n+1):
        q_edge_src = {
            "node1": "s"+str(i),
            "node2": "n"+str(i)+"_1",
            "attenuation": 0.0002,
            "distance": 500,
            "type": "meet_in_the_middle"
        }
        
        c_edge_src = {
            "node1": "s"+str(i),
            "node2": "n"+str(i)+"_1",
            "delay": 500000000
        }
        graph["qconnections"].append(q_edge_src)
        graph["cconnections"].append(c_edge_src)
        q_edge_dest = {
            "node1": ("hd" if i in high_quality else "d")+str(i),
            "node2": "n"+str(i)+"_"+str(n),
            "attenuation": 0.0002,
            "distance": 500,
            "type": "meet_in_the_middle"
        }
        c_edge_dest = {
            "node1": ("hd" if i in high_quality else "d")+str(i),
            "node2": "n"+str(i)+"_"+str(n),
            "delay": 500000000
        }
        graph["qconnections"].append(q_edge_dest)
        graph["cconnections"].append(c_edge_dest)
        
        for j in range(1, n+1):
            # Intralayer connection
            if n!=2 or i!=2:
                q_edge_intra = {
                    "node1": "n"+str(i)+"_"+str(j),
                    "node2": "n"+str(1 if i==n else i+1)+"_"+str(j),
                    "attenuation": 0.0002,
                    "distance": 500,
                    "type": "meet_in_the_middle"
                }
                c_edge_intra = {
                    "node1": "n"+str(i)+"_"+str(j),
                    "node2": "n"+str(1 if i==n else i+1)+"_"+str(j),
                    "delay": 500000000
                }
                graph["qconnections"].append(q_edge_intra)
                graph["cconnections"].append(c_edge_intra)
            # Interlayer connection
            if j != n:
                q_edge_inter = {
                    "node1": "n"+str(i)+"_"+str(j),
                    "node2": "n"+str(1)+"_"+str(j+1),
                    "attenuation": 0.0002,
                    "distance": 500,
                    "type": "meet_in_the_middle"
                }
                c_edge_inter = {
                    "node1": "n"+str(i)+"_"+str(j),
                    "node2": "n"+str(1)+"_"+str(j+1),
                    "delay": 500000000
                }
                graph["qconnections"].append(q_edge_inter)
                graph["cconnections"].append(c_edge_inter)
                
    return graph    
def waxman_gen(n: int, alpha = 0.85, beta=0.275, frac=0.3) -> dict:
    G = nx.waxman_graph(n**2, alpha = alpha, beta = beta)
    seed = 0
    graph = {
        "is_parallel": False,
        "stop_time": 2000000000000,
        "nodes": [],
        "qconnections": [],
        "cconnections": []
    }
    high_quality=random.sample(range(1, n+1), round(n*frac))
    for i in range(1, n**2+1):
        node_dict =  {
                "name": ("n"+str(i)),
                "type": "QuantumRouter",
                "seed": seed,
                "memo_size": 50
        }
        graph["nodes"].append(node_dict)
        seed +=1
        

    for k in range(1, n+1):
        src_dict =  {
                "name": ("s"+str(k)),
                "type": "QuantumRouter",
                "seed": seed,
                "memo_size": 50
        }
        seed+=1
        dest_dict =  {
                "name": (("hd" if k in high_quality else "d")+str(k)),
                "type": "QuantumRouter",
                "seed": seed,
                "memo_size": 50
        }
        
        seed +=1
        graph["nodes"].append(src_dict)
        graph["nodes"].append(dest_dict)
        
    for (u, v, _) in G.edges.data():
        pos1 = G.nodes[u]["pos"]
        pos2 = G.nodes[v]["pos"]
        q_edge_dict = {
            "node1": "n"+str(u+1),
            "node2": "n"+str(v+1),
            "attenuation": 0.0002,
            "distance": round(1000*((pos2[1]-pos1[1])**2 +  (pos2[0]-pos1[0])**2)**0.5 ) ,
            "type": "meet_in_the_middle"
        }
        c_edge_dict = {
            "node1": "n"+str(u+1),
            "node2": "n"+str(v+1),
            "delay": 500000000
        }
        graph["qconnections"].append(q_edge_dict)
        graph["cconnections"].append(c_edge_dict)

    src_nodes = random.sample(range(1, n**2+1), n)
    dest_nodes = random.sample(range(1, n**2+1), n)

    for i in range(1, n+1):
        q_edge_dict_src = {
            "node1": "s"+str(i),
            "node2": "n"+str(src_nodes[i-1]),
            "attenuation": 0.0002,
            "distance": 500,
            "type": "meet_in_the_middle"
        }
        c_edge_dict_src = {
            "node1": "s"+str(i),
            "node2": "n"+str(src_nodes[i-1]),
            "delay": 500000000
        }
        graph["qconnections"].append(q_edge_dict_src)
        graph["cconnections"].append(c_edge_dict_src)

        q_edge_dict_dest = {
            "node1": ("hd" if i in high_quality else "d")+str(i),
            "node2": "n"+str(dest_nodes[i-1]),
            "attenuation": 0.0002,
            "distance": 500,
            "type": "meet_in_the_middle"
        }
        c_edge_dict_dest = {
            "node1": ("hd" if i in high_quality else "d")+str(i),
            "node2": "n"+str(dest_nodes[i-1]),
            "delay": 500000000
        }
        graph["qconnections"].append(q_edge_dict_dest)
        graph["cconnections"].append(c_edge_dict_dest)
    return graph

def is_high(string: str) -> bool:
    if len(string) > 0:
        return string[0]=='h'
    else:
        return False
