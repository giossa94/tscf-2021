from argument_parser import get_argument_parser
from fat_tree_generator.src.utils import create_fat_tree
from build_table import build_forwarding_table, create_graph_from_json
from utils import index_list_by_key, build_config
import os
import json
import socket
import selectors
import types
from shutil import copy
import subprocess
from threading import Thread

HOST = "0.0.0.0"
PORT = 65432


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
            return None
        else:
            print("data:", data.outb.decode())
            print("closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()
            return data.outb.decode()


def run_topology():
    # Start the Fat Tree emulation with Kathara
    print("Running lab...")
    subprocess.run(["kathara", "lstart", "--noterminals"])


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

# Build tables and persist them into shared directory, so containers can access them.
non_server_nodes = set(
    [node_id for node_id in topology_graph.nodes() if not node_id.startswith("server")]
)
for node_id in non_server_nodes:
    print(f"Building forwarding table for node {node_id}...")
    expected_table = index_list_by_key(
        list=build_forwarding_table(node_id, topology_graph, include_dc=True), key="dst"
    )
    with open(
        os.path.join(lab_dir, "shared", node_id, "expected_table.json"), mode="w"
    ) as f:
        json.dump(expected_table, f, indent=4, sort_keys=True)

# Copy daemon code and dependencies into shared directory.
copy("./node_daemon_exp1.py", os.path.join(lab_dir, "shared"))
copy("./table_diff.py", os.path.join(lab_dir, "shared"))
copy("./utils.py", os.path.join(lab_dir, "shared"))

os.chdir(lab_dir)

for node in non_server_nodes:
    with (open(node + ".startup", "a+")) as startup:
        line = "python3.7 /shared/node_daemon_exp1.py %s\n" % node
        if line not in startup.readlines():
            startup.write(line)

with (open("lab.conf", "a+")) as labconf:
    for node in non_server_nodes:
        line = '%s[bridged]="true"\n' % node
        if line not in labconf.readlines():
            labconf.write(line)

sel = selectors.DefaultSelector()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print("listening on", (HOST, PORT))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

thread = Thread(target=run_topology)
thread.start()

converged_nodes_ids = set()
has_converged = False
try:
    while not has_converged:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                node_id = service_connection(key, mask)
                if node_id:
                    converged_nodes_ids.add(node_id)
                    if converged_nodes_ids == non_server_nodes:
                        has_converged = True
                        print("Topology has converged")
                        break
                    else:
                        print(
                            "Topology has not converged, remaining nodes:",
                            non_server_nodes.difference(converged_nodes_ids),
                        )

except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    # Stop emulation
    subprocess.run(["kathara", "lclean"])
    sel.close()
