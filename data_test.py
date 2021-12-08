import subprocess
import re


def data_test(topology_graph, debug=False):
    servers = [
        (node, data)
        for (node, data) in topology_graph.nodes(data=True)
        if node.startswith("server")
    ]
    connectivity_data = {}
    has_total_connectivity = True
    for server_a, _ in servers:
        for server_b, data_b in servers:
            if server_a == server_b:
                continue
            server_b_interfaces = data_b["interfaces"]
            [server_b_leaf_interface] = [
                interface
                for interface in server_b_interfaces
                if interface["collision_domain"] != "lo"
            ]
            if debug:
                print(
                    f"Checking connectivity between {server_a} and {server_b} ({server_b_leaf_interface['ip_address']})"
                )
            output = subprocess.run(
                [
                    "kathara",
                    "exec",
                    server_a,
                    "--",
                    "ping",
                    server_b_leaf_interface["ip_address"],
                    "-c",
                    "2",
                ],
                text=True,
                capture_output=True,
            )
            parsed_ping_output = re.findall(
                r"(\d) received", output.stdout, re.MULTILINE
            )
            if parsed_ping_output is None:
                raise RuntimeError("Error parsing ping output.")

            received_packets = int(parsed_ping_output[0])
            if debug:
                print(f"Target server has receveid {received_packets} packets.")
            connectivity_data[(server_a, server_b)] = received_packets > 0
            if received_packets == 0:
                has_total_connectivity = False
    return (has_total_connectivity, connectivity_data)
