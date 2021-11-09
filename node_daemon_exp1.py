from time import sleep
import daemon
import socket
import subprocess
import os
import json
from table_diff import are_tables_equal
import sys
from utils import index_list_by_key

HOST = "172.17.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server


# TODO:
# [X] Research how to connect container to the host network
# [X] Research how to run a python daemon in Linux
# [X] Implement node daemon
# [X] Set [bridged]="true" to all non-server containers
# [X] Implement exp1 controller (create and run topoogy, run TCP server until convergence)
# [X] Generate and write expected table on startup
# [X] Setup python dev env in containers
# [X] Deploy daemon to containers (automate if possible)
# [X] Run daemon on startup


def get_expected_table(node_id):
    with open(os.path.join("/shared", node_id, "expected_table.json"), "r") as f:
        expected_table = json.load(f)
    return expected_table


def get_actual_table():
    output = subprocess.run(["ip", "-json", "route"], stdout=subprocess.PIPE)
    return index_list_by_key(list=json.loads(output.stdout.decode("utf-8")), key="dst")


def log(msg, node_id):
    with (open(os.path.join("/shared", node_id, "log.txt"), "a+")) as f:
        f.write(msg + " \n")


def log_json(data, node_id):
    with (open(os.path.join("/shared", node_id, "log.txt"), "a+")) as f:
        json.dump(data, f, indent=4)


def run(node_id):
    with daemon.DaemonContext():
        try:
            expected_table = get_expected_table(node_id)
            actual_table = get_actual_table()

            while not are_tables_equal(
                expected_table=expected_table, actual_table=actual_table
            ):
                sleep(3)
                actual_table = get_actual_table()
            log("Node converged, connecting to server...", node_id)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(node_id.encode())
        except Exception as error:
            log(str(error), node_id)
            log("actual table:", node_id)
            log_json(actual_table, node_id)
            log("expected table:", node_id)
            log_json(expected_table, node_id)
            log("-" * 20, node_id)


if __name__ == "__main__":
    run(sys.argv[1])
