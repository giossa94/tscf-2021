from data_test import data_test
from fat_tree_generator.src.utils import create_fat_tree
from build_table import build_forwarding_table, create_graph_from_json
from table_diff import are_tables_equal
from utils import index_list_by_key, build_config
import subprocess
import os
import json
import time
from argument_parser import get_argument_parser

# Build argument parser
parser = get_argument_parser()
args = parser.parse_args()

if args.p is None:
    args.p = int(args.k / 2)

print(f"Creating Fat Tree with k={args.k} and {args.p} planes.")

# Build the config JSON that VFTGen uses fro creating the Fat Tree.
params = build_config(args.k, args.p)

# Check if the requested topology already exists.
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
    _, output_dir, lab_dir = create_fat_tree(params, os.path.abspath("."))

# Build a graph representing the desired Fat Tree.
with open(os.path.join(output_dir, "lab.json")) as json_file:
    lab_json = json.load(json_file)
topology_graph = create_graph_from_json(lab_json)

# Build the forwarding table for each node in the topology
# using Dijkstra's algorithm (ECMP version) on the built graph.
node_tables = {}
non_server_nodes = [
    node_id for node_id in topology_graph.nodes() if not node_id.startswith("server")
]
for node_id in non_server_nodes:
    print(f"Building forwarding table for node {node_id}...")
    node_tables[node_id] = index_list_by_key(
        list=build_forwarding_table(node_id, topology_graph, include_dc=True), key="dst"
    )

# Set path for saving the calculated tables
tables_dir = os.path.join(
    os.getcwd(),
    output_dir,
    "tables",
)
os.makedirs(tables_dir, exist_ok=True)
os.chdir(lab_dir)
if args.c:
    print("Cleaning lab before starting emulation...")
    subprocess.run(["kathara", "lclean"])

# Start the Fat Tree emulation with Kathara
print("Running lab...")
subprocess.run(["kathara", "lstart", "--noterminals"])

time_start = time.time()
converged_nodes_ids = []
node_index = 0

try:
    # While the emulated topology doesn't converge, keep running
    while len(converged_nodes_ids) < len(non_server_nodes):
        node_id = non_server_nodes[node_index % len(non_server_nodes)]
        if node_id in converged_nodes_ids:
            continue
        output = subprocess.run(
            ["kathara", "exec", node_id, "--", "ip", "-json", "route"],
            text=True,
            capture_output=True,
        )
        print(f"Parsing actual table for node {node_id}", output.stdout)
        actual_table = index_list_by_key(list=json.loads(output.stdout), key="dst")
        expected_table = node_tables[node_id]

        # Check which nodes have already converged
        if are_tables_equal(expected_table=expected_table, actual_table=actual_table):
            converged_nodes_ids.append(node_id)
            print(f"Node {node_id} converged, writing table...")
            with open(
                os.path.join(tables_dir, f"{node_id}_table.json"), mode="w"
            ) as file:
                json.dump(actual_table, file, indent=4, sort_keys=True)

        node_index += 1

    # The calculated forwarding tables match the ones in the emulation
    print(
        f"The topology has converged in {time.strftime('%H:%M:%S', time.gmtime(time.time()-time_start))} hours according to the centralized table criteria."
    )

    (data_test_result, data_test_info) = data_test(topology_graph, args.d)

    if data_test_result:
        print("The topology has converged according to the data test. ✅")
    else:
        print("The topology has not converged according to the data test. ❌")
        if args.d:
            print(data_test_info)

except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    # Stop emulation
    subprocess.run(["kathara", "lclean"])
