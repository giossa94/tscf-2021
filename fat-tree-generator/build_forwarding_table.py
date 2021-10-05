import json
import networkx as nx
from topology_analysis import create_graph_from_json


def get_next_hop(next_hop_id, neighbours):
    for neighbour in neighbours:
        [neighbour_id, _] = neighbour
        if neighbour_id == next_hop_id:
            return neighbour
    return None


def build_forwarding_table(node_id, topology_graph):
    servers = [
        (node, data)
        for (node, data) in topology_graph.nodes(data=True)
        if node.startswith("server")
    ]
    node_interfaces = topology_graph.nodes()[node_id]["interfaces"]

    forwarding_table = []
    for server, data in servers:
        entry = {}
        server_interfaces = data["interfaces"]
        [server_leaf_subnetwork] = [
            interface
            for interface in server_interfaces
            if interface["collision_domain"] != "lo"
        ]
        entry["dst"] = server_leaf_subnetwork["network"]
        entry["nexthops"] = []
        shortest_paths = nx.all_shortest_paths(
            topology_graph, source=node_id, target=server
        )
        for shortest_path in shortest_paths:
            next_hop = shortest_path[1]
            for interface in node_interfaces:
                if "neighbours" in interface:
                    neighbour = get_next_hop(next_hop, interface["neighbours"])
                    if neighbour is not None:
                        entry["nexthops"].append(
                            {
                                "gateway": neighbour[1],
                                "dev": f"eth{interface['number']}",
                            }
                        )
            forwarding_table.append(entry)
    return forwarding_table


if __name__ == "__main__":
    topology_graph = create_graph_from_json("fat_tree_2_2_1+1_1_1+bgp")
    forwarding_table = build_forwarding_table("leaf_1_0_1", topology_graph)
    print(json.dumps(forwarding_table, indent=4, sort_keys=True))
