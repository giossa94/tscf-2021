import json
import networkx as nx
from topology_analysis import create_graph_from_json


def get_next_hop(next_hop_id, neighbours):
    for neighbour in neighbours:
        [neighbour_id, _] = neighbour
        if neighbour_id == next_hop_id:
            return neighbour
    return None


def is_dc(subnetwork_dst, interfaces):
    return any(interface["network"] == subnetwork_dst for interface in interfaces)


def build_forwarding_table(node_id, topology_graph, include_dc=False):
    servers = [
        (node, data)
        for (node, data) in topology_graph.nodes(data=True)
        if node.startswith("server")
    ]
    node_interfaces = [
        interface
        for interface in topology_graph.nodes()[node_id]["interfaces"]
        if interface["collision_domain"] != "lo"
    ]

    forwarding_table = []

    if include_dc:
        for interface in node_interfaces:
            forwarding_table.append(
                {
                    "dst": interface["network"],
                    "prefsrc": interface["ip_address"],
                    "dev": f"eth{interface['number']}",
                }
            )

    for server, data in servers:
        entry = {}
        server_interfaces = data["interfaces"]
        [server_leaf_subnetwork] = [
            interface
            for interface in server_interfaces
            if interface["collision_domain"] != "lo"
        ]

        if is_dc(server_leaf_subnetwork["network"], node_interfaces):
            continue  # discard DC subnetworks

        entry["dst"] = server_leaf_subnetwork["network"]
        entry["nexthops"] = []
        shortest_paths = nx.all_shortest_paths(
            topology_graph, source=node_id, target=server
        )
        # Get next hops (second node of each path) and remove duplicates
        next_hops = set([path[1] for path in list(shortest_paths)])

        for next_hop in next_hops:
            for interface in node_interfaces:
                neighbour = get_next_hop(next_hop, interface["neighbours"])

                if neighbour is not None:
                    [_, neighbour_ip] = neighbour

                    entry["nexthops"].append(
                        {
                            "gateway": neighbour_ip,
                            "dev": f"eth{interface['number']}",
                        }
                    )
        forwarding_table.append(entry)
    return forwarding_table


if __name__ == "__main__":
    topology_graph = create_graph_from_json("fat_tree_2_2_1+1_1_1+bgp")
    forwarding_table = build_forwarding_table(
        "leaf_1_0_1", topology_graph, include_dc=True
    )
    print(json.dumps(forwarding_table, indent=4, sort_keys=True))
