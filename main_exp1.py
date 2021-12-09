from argument_parser import get_argument_parser
from data_test import data_test
from build_table import build_forwarding_table, create_graph_from_json
from fat_tree import build_fat_tree, build_config
from utils import index_list_by_key, update_node_config_file
import os
import json
import socket
import selectors
import types
import time
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
if args.debug == True and args.ping == False:
    args.ping = True

print(f"Creating Fat Tree with k={args.k} and {args.p} planes.")

# Build the config JSON that VFTGen uses fro creating the Fat Tree.
params = build_config(args.k, args.p)

output_dir, lab_dir = build_fat_tree(params, "exp1")

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
if args.clean:
    print("Cleaning lab before starting emulation...")
    subprocess.run(["kathara", "lclean"])

update_node_config_file(
    non_server_nodes,
    "python3.7 /shared/node_daemon_exp1.py %s\n",
    lambda node: f"{node}.startup",
)
update_node_config_file(non_server_nodes, '%s[bridged]="true"\n', lambda _: "lab.conf")

sel = selectors.DefaultSelector()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print("listening on", (HOST, PORT))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

thread = Thread(target=run_topology)
thread.start()
time_start = time.time()

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
                        print(
                            f"The topology has converged in {time.strftime('%H:%M:%S', time.gmtime(time.time()-time_start))} hours according to the decentralized table criteria."
                        )
                        break
                    else:
                        print(
                            "Topology has not converged, remaining nodes:",
                            non_server_nodes.difference(converged_nodes_ids),
                        )

    sel.close()

    if args.ping:
        (data_test_result, data_test_info) = data_test(topology_graph, args.debug)

        if data_test_result:
            print("The topology has converged according to the data test. ✅")
        else:
            print("The topology has not converged according to the data test. ❌")
            if args.debug:
                error_pairs = [
                    x for x in data_test_info.keys() if data_test_info[x] == False
                ]
                print(error_pairs)

except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    # Stop emulation
    subprocess.run(["kathara", "lclean"])
