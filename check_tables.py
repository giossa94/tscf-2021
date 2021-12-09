import sys
import os
import json
from build_table import build_forwarding_table, create_graph_from_json
from table_diff import are_tables_equal
from utils import index_list_by_key


if __name__ == "__main__":
    dir_name = sys.argv[1]
    with open(os.path.join(dir_name, "lab.json")) as json_file:
        lab_json = json.load(json_file)
    topology_graph = create_graph_from_json(lab_json)
    non_server_nodes = [
        node_id
        for node_id in topology_graph.nodes()
        if not node_id.startswith("server")
    ]
    matching_tables = 0
    for node_id in non_server_nodes:
        print(f"Building forwarding table for node {node_id}...")
        expected_table = index_list_by_key(
            list=build_forwarding_table(node_id, topology_graph, include_dc=True),
            key="dst",
        )
        with open(
            os.path.join(dir_name, "lab", "shared", node_id, "actual_table.json"), "r"
        ) as f:
            actual_table = json.load(f)
        if are_tables_equal(expected_table, actual_table, silent=True):
            matching_tables += 1
    if matching_tables == len(non_server_nodes):
        print("All tables match! ✅")
    else:
        print(f"{matching_tables} of {len(non_server_nodes)} tables match! ❌")
