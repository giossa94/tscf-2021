import json, sys, os
import networkx as nx


def create_graph_from_json(path_to_lab):

    # https://networkx.org/documentation/stable/reference/classes/graph.html
    G = nx.Graph()

    # Get every node's name from lab.json and the name of their neighbours as well
    with open(os.path.join(path_to_lab, "lab.json")) as json_file:
        lab_json = json.load(json_file)
        for tof_node in lab_json["aggregation_layer"]:
            interfaces = lab_json["aggregation_layer"][tof_node]["interfaces"]
            G.add_node(tof_node, interfaces=interfaces)
            for interface in interfaces:
                if interface["collision_domain"] != "lo":
                    for neighbour in interface["neighbours"]:
                        G.add_edge(tof_node, neighbour[0])

        for pod in lab_json["pod"]:
            for node in lab_json["pod"][pod]:
                interfaces = lab_json["pod"][pod][node]["interfaces"]
                G.add_node(node, interfaces=interfaces)
                for interface in interfaces:
                    if interface["collision_domain"] != "lo":
                        for neighbour in interface["neighbours"]:
                            G.add_edge(node, neighbour[0])

    return G


if __name__ == "__main__":
    G = create_graph_from_json("fat_tree_2_2_1+1_1_1+bgp")

    source = "leaf_1_0_1"
    target = "leaf_4_0_2"

    print(G.number_of_edges())
    print(G.number_of_nodes())

    print(nx.get_node_attributes(G, "interfaces")["spine_1_1_1"])

    print(f"ECMP from {source} to {target}:")
    for p in nx.all_shortest_paths(G, source=source, target=target):
        print(p)
