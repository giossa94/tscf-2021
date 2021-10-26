import json
import networkx as nx
from topology_analysis import create_graph_from_json


def get_next_hop_ip(next_hop_id, node_interfaces):
    for interface in node_interfaces:
        for neighbour in interface["neighbours"]:
            [neighbour_id, neighbour_ip] = neighbour
            if neighbour_id == next_hop_id:
                return neighbour_ip
    raise RuntimeError("next_hop_id is not present in any of the node interfaces")


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
        shortest_paths = nx.all_shortest_paths(
            topology_graph, source=node_id, target=server
        )
        # Get next hops (second node of each path) and remove duplicates
        next_hops_ids = set([path[1] for path in list(shortest_paths)])

        next_hops_entries = []
        for next_hop_id in next_hops_ids:
            next_hop_ip = get_next_hop_ip(next_hop_id, node_interfaces)
            next_hops_entries.append(
                {
                    "gateway": next_hop_ip,
                    "dev": f"eth{interface['number']}",
                }
            )

        if len(next_hops_entries) > 1:
            entry["nexthops"] = next_hops_entries
        elif len(next_hops_entries) == 1:
            next_hop = next_hops_entries[0]
            entry["gateway"] = next_hop["gateway"]
            entry["dev"] = next_hop["dev"]
        else:
            raise RuntimeError(
                f"No next hop to reach server {server} from node {node_id}"
            )

        forwarding_table.append(entry)
    return forwarding_table


if __name__ == "__main__":
    topology_graph = create_graph_from_json("fat_tree_2_2_1+1_1_1+bgp")
    forwarding_table = build_forwarding_table(
        "leaf_1_0_1", topology_graph, include_dc=True
    )
    print(json.dumps(forwarding_table, indent=4, sort_keys=True))
