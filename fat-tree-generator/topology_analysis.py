import json, sys, os
import networkx as nx

def create_graph_from_json(path_to_lab):
    
    # https://networkx.org/documentation/stable/reference/classes/graph.html    
    node_neighbours = {}
    
    # Get every node's name from lab.json and the name of their neighbours as well
    with open(os.path.join(path_to_lab,'lab.json')) as json_file:
        lab_json = json.load(json_file)
        for tof_node in lab_json['aggregation_layer']:
            node_neighbours[tof_node] = []
            interfaces = lab_json['aggregation_layer'][tof_node]['interfaces']
            for interface in interfaces:
                if interface['collision_domain'] != 'lo':
                    for neighbour in interface['neighbours']:
                        node_neighbours[tof_node] += [(neighbour[0],neighbour[1])]
        for pod in lab_json['pod']:
            for node in lab_json['pod'][pod]:
                node_neighbours[node] = []
                interfaces = lab_json['pod'][pod][node]['interfaces']
                for interface in interfaces:
                    if interface['collision_domain'] != 'lo':
                        for neighbour in interface['neighbours']:
                            node_neighbours[node] += [(neighbour[0],neighbour[1])]

    G = nx.Graph()
    G.add_nodes_from(node_neighbours.keys())
    G.add_edges_from([(x,y[0]) for x in node_neighbours.keys() for y in node_neighbours[x]])

    return G

if __name__ == '__main__':
    G = create_graph_from_json('fat_tree_2_2_1+1_1_1+bgp')

    source = 'leaf_1_0_1'
    target = 'leaf_4_0_2'

    print(f'ECMP from {source} to {target}:')
    for p in nx.all_shortest_paths(G, source=source, target=target):
        print(p)
    