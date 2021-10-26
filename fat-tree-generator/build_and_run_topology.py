from src.utils import create_fat_tree
from topology_analysis import create_graph_from_json
from build_forwarding_table import build_forwarding_table
from table_diff import are_tables_equal
from utils import index_list_by_key
import subprocess
import os
import json
from build_config_json import build_config
import sys


print(f"Creating Fat Tree with K={sys.argv[1]}. The number of planes is 2 by default.")

params = build_config(int(sys.argv[1]))

default_directory_name = "fat_tree_%d_%d_%d+%d_%d_%d+%s" % (
    params["k_leaf"],
    params["k_top"],
    params["redundancy_factor"],
    params["leaf_spine_parallel_links"],
    params["spine_tof_parallel_links"],
    params["ring_parallel_links"],
    params["protocol"],
)

if os.path.exists(default_directory_name):
    print("Topology already exists")
    output_dir = default_directory_name
    lab_dir = os.path.join(default_directory_name, "lab")
else:
    _, output_dir, lab_dir = create_fat_tree(
        params, os.path.abspath(".")
    )  # , args.dir, args.name, args.kube_net)

node_tables = {}
topology_graph = create_graph_from_json(output_dir)
non_server_nodes = [
    node_id for node_id in topology_graph.nodes() if not node_id.startswith("server")
]
for node_id in non_server_nodes:
    print(f"Building forwarding table for node {node_id}...")
    node_tables[node_id] = index_list_by_key(
        list=build_forwarding_table(node_id, topology_graph, include_dc=True), key="dst"
    )

tables_dir = os.path.join(
    os.getcwd(),
    output_dir,
    "tables",
)
os.makedirs(tables_dir, exist_ok=True)
os.chdir(lab_dir)
print("Running lab...")
subprocess.run(["kathara", "lstart", "--noterminals"])

converged_nodes_ids = []
node_index = 0


while len(converged_nodes_ids) < len(non_server_nodes):
    node_id = non_server_nodes[node_index % len(non_server_nodes)]
    if node_id in converged_nodes_ids:
        continue
    output = subprocess.run(
        ["kathara", "exec", node_id, "--", "ip", "-json", "route"],
        text=True,
        capture_output=True,
    )
    actual_table = index_list_by_key(list=json.loads(output.stdout), key="dst")
    expected_table = node_tables[node_id]

    if are_tables_equal(expected_table=expected_table, actual_table=actual_table):
        converged_nodes_ids.append(node_id)
        print(f"Node {node_id} converged, writing table...")
        with open(os.path.join(tables_dir, f"{node_id}_table.txt"), mode="w") as file:
            json.dump(actual_table, file, indent=4, sort_keys=True)

    node_index += 1

print("Topology has converged")

subprocess.run(["kathara", "lclean"])
