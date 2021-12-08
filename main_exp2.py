from argument_parser import get_argument_parser
from data_test import data_test
from fat_tree_generator.src.utils import create_fat_tree
from build_table import get_nodes_and_interfaces_from_json, build_forwarding_table, create_graph_from_json
from table_diff import are_tables_equal
from utils import index_list_by_key, build_config
from sliding_window import sliding_window
import subprocess, nest_asyncio, os, json, time

MAXIMUM_FAILED_ATTEMPTS = 30

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


# Get nodes and interfaces of the tokens
with open(os.path.join(output_dir, "lab.json")) as json_file:
    lab_json = json.load(json_file)
nodes_and_interfaces = get_nodes_and_interfaces_from_json(lab_json)

# Create lists of nodes
tof_nodes = [node_id for node_id in nodes_and_interfaces if node_id.startswith("tof")]
spine_nodes = [node_id for node_id in nodes_and_interfaces if node_id.startswith("spine")]
leaf_nodes = [node_id for node_id in nodes_and_interfaces if node_id.startswith("leaf")]

# Set path for saving the calculated tables
tables_dir = os.path.join(
    os.getcwd(),
    output_dir,
    "tables",
)
os.makedirs(tables_dir, exist_ok=True)

# Change to lab directory
os.chdir(lab_dir)
if args.clean: 
    print('Cleaning lab before starting emulation...')
    subprocess.run(["kathara", "lclean"])

# Start the Fat Tree emulation with Kathara
print("Running lab...")
subprocess.run(["kathara", "lstart", "--noterminals"])

# Create sliding window object
sw = sliding_window(args.w,args.t)
nest_asyncio.apply()

print(f"Starting sliding window check\n\t- k={args.k}\n\t- planes={args.p}\n\t- window_size={args.w}\n\t- threshold={args.t}\n\t- A node's convergence is assumed after {MAXIMUM_FAILED_ATTEMPTS} checks")
# Start a timer and create two node_ids dicts  
sw_start = time.time()
output_tables_by_node = {} 
number_of_failed_attempts_by_node = {node_id: 0 for node_id in tof_nodes+spine_nodes+leaf_nodes}
number_of_tshark_errors = 0
# Check leaf nodes convergence at first
converged_leaves_ids = []
node_index = 0
while len(converged_leaves_ids) < len(leaf_nodes):
    node_id = leaf_nodes[node_index % len(leaf_nodes)]
    if node_id in converged_leaves_ids:
        node_index += 1
        continue

    # If node_id did not converge, call the sliding window to check every .pcap file
    pcap_paths = [os.path.join('shared',node_id, interface + '.pcap') for interface in nodes_and_interfaces[node_id]]
    try:
        result = sw.sliding_window_check(pcap_paths)
        if result['code']==1 or number_of_failed_attempts_by_node[node_id]>= MAXIMUM_FAILED_ATTEMPTS:
            if result['code']==1:
                print(f"Node {node_id} converged (average={result['average']})")
            else:
                print(f"Node {node_id} has not yet converged but reached maximum attempts. Convergence is assumed.")
                
            # Add node_id to the list of converged leaf nodes
            converged_leaves_ids.append(node_id) 

            # Save the forwarding table of node_id 
            output = subprocess.run(["kathara", "exec", node_id, "--", "ip", "-json", "route"],text=True,capture_output=True,)
            actual_table = index_list_by_key(list=json.loads(output.stdout), key="dst")
            with open(os.path.join(tables_dir, f"{node_id}_table.json"), mode="w") as file:
                json.dump(actual_table, file, indent=4, sort_keys=True)
            
            # Save the ouput in memory for using it in the final check
            output_tables_by_node[node_id] = output

        else:
            number_of_failed_attempts_by_node[node_id]+=1
            print(f"Node {node_id} has not yet converged on its {number_of_failed_attempts_by_node[node_id]} failed attempt (code: {result['code']}, {result['status']})")
    except Exception as e:
        print(f'Error ({node_id}): {e}')
        number_of_tshark_errors+=1

    node_index += 1

time.sleep(1)
non_server_or_leaf_nodes = tof_nodes + spine_nodes
converged_nodes_ids = []
node_index = 0

while len(converged_nodes_ids) < len(non_server_or_leaf_nodes):
    node_id = non_server_or_leaf_nodes[node_index % len(non_server_or_leaf_nodes)]
    if node_id in converged_nodes_ids:
        node_index += 1
        continue

    # If node_id did not converge, call the sliding window to check every .pcap file
    pcap_paths = [os.path.join('shared',node_id, interface + '.pcap') for interface in nodes_and_interfaces[node_id]]
    try:
        result = sw.sliding_window_check(pcap_paths)
        if result['code']==1 or number_of_failed_attempts_by_node[node_id]>= MAXIMUM_FAILED_ATTEMPTS:
            if result['code']==1:
                print(f"Node {node_id} converged (average={result['average']})")
            else:
                print(f"Node {node_id} has not yet converged but reached maximum attempts. Convergence is assumed.")
            
            # Add node_id to the list of converged leaf nodes
            converged_nodes_ids.append(node_id) 
            
            # Save the forwarding table of node_id
            output = subprocess.run(["kathara", "exec", node_id, "--", "ip", "-json", "route"],text=True,capture_output=True,)
            actual_table = index_list_by_key(list=json.loads(output.stdout), key="dst")
            with open(os.path.join(tables_dir, f"{node_id}_table.json"), mode="w") as file:
                json.dump(actual_table, file, indent=4, sort_keys=True)
            
            # Save the ouput in memory for using it in the final check
            output_tables_by_node[node_id] = output
        else:
            number_of_failed_attempts_by_node[node_id]+=1
            print(f"Node {node_id} has not yet converged on its {number_of_failed_attempts_by_node[node_id]} failed attempt ({result['status']})")

    except Exception as e:
        print(f'Error ({node_id}): {e}')
        number_of_tshark_errors+=1

    node_index += 1

# Every node has converged according to the sliding window check
print(f"The topology has converged in {time.strftime('%H:%M:%S', time.gmtime(time.time()-sw_start))} hours according to the centralized sliding window criteria.")
if number_of_tshark_errors>0:
    print(f'{number_of_tshark_errors} tshark errors were found.')

# Build a graph representing the desired Fat Tree.
with open(os.path.join("..", "lab.json")) as json_file:
    lab_json = json.load(json_file)
topology_graph = create_graph_from_json(lab_json)

if args.ping:
    (data_test_result, data_test_info) = data_test(topology_graph, args.d)

    if data_test_result:
        print("The topology has converged according to the data test. ✅")
    else:
        print("The topology has not converged according to the data test. ❌")
        if args.d:
            print(data_test_info)

# Stop emulation
subprocess.run(["kathara", "lclean"])

# Now we are going to check if the expected tables match the calculated tables

# Build the forwarding table for each node in the topology
# using Dijkstra's algorithm (ECMP version) on the built graph.
node_tables = {}
non_server_nodes = leaf_nodes + non_server_or_leaf_nodes

matching_tables = 0
for node_id in non_server_nodes:
    node_tables[node_id] = index_list_by_key(
        list=build_forwarding_table(node_id, topology_graph, include_dc=True), key="dst"
    )
    output = output_tables_by_node[node_id]
    actual_table = index_list_by_key(list=json.loads(output.stdout), key="dst")
    if are_tables_equal(expected_table=node_tables[node_id], actual_table=actual_table, silent=True):
        matching_tables+=1
if matching_tables==len(non_server_nodes):
    print("\n[OK] Tables also match.")
else:
    print('\n[Warning] The convergence criteria do not match.')