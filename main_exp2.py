from fat_tree_generator.src.utils import create_fat_tree
from build_table import get_nodes_and_interfaces_from_json
from table_diff import are_tables_equal
from utils import index_list_by_key, build_config
from sliding_window import sliding_window_check
import subprocess, nest_asyncio, os, json, argparse, time
from shutil import copyfile

WINDOW_SIZE = 20
THRESHOLD = 0.2

# Build argument parser
parser = argparse.ArgumentParser(description="Read topology configuration")
parser.add_argument(
    "-k",
    action="store",
    type=int,
    default=4,
    required=False,
    help="K that defines the Fat Tree.",
)
parser.add_argument(
    "-p",
    "-number_of_planes",
    action="store",
    type=int,
    default=2,
    required=False,
    help="Number of planes in the Fat Tree.",
)
parser.add_argument(
    '-c',
    "-clean_lab",
    action="store",
    type=bool,
    default=True,
    required=False,
    help="Run kathara lclean before starting emulation",
)
args = parser.parse_args()

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

# Get nodes and interfaces of the tokens
with open(os.path.join(output_dir, "lab.json")) as json_file:
    lab_json = json.load(json_file)
nodes_and_interfaces = get_nodes_and_interfaces_from_json(lab_json)
non_server_nodes = [node_id for node_id in nodes_and_interfaces if not node_id.startswith("server")]

# Change to lab directory
os.chdir(lab_dir)
if args.c: 
    print('Cleaning lab before starting emulation...')
    subprocess.run(["kathara", "lclean"])

# Start the Fat Tree emulation with Kathara
print("Running lab...")
subprocess.run(["kathara", "lstart", "--noterminals"])

converged_nodes_ids = []
node_index = 0
nest_asyncio.apply()
time.sleep(0.2)

try:
    # While the emulated topology doesn't converge, keep running
    while len(converged_nodes_ids) < len(non_server_nodes):
        node_id = non_server_nodes[node_index % len(non_server_nodes)]
        if node_id in converged_nodes_ids:
            node_index += 1
            continue

        # Call the sliding window to check every .pcap file of the current node_id
        pcap_paths = [os.path.join('shared',node_id, interface + '.pcap') for interface in nodes_and_interfaces[node_id]]
        converged, average = sliding_window_check(WINDOW_SIZE,THRESHOLD,pcap_paths)

        if converged:
            converged_nodes_ids.append(node_id) 
            print(f"Node {node_id} converged (average={average})")
        else:
            print(f"Node {node_id} has not yet converged (average={average})")

        node_index += 1
    
    # Every node has converged according to the sliding window check
    print(f"Topology has converged ({converged_nodes_ids})")

except Exception as e:
    print('Error: ',e)

# Stop emulation
subprocess.run(["kathara", "lclean"])
