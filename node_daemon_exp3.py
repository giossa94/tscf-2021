from time import sleep
import daemon
import socket
import subprocess
import os
import json
import sys
from utils import index_list_by_key
from sliding_window import sliding_window
import glob
import nest_asyncio

MAXIMUM_FAILED_ATTEMPTS = 5

HOST = "172.17.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server


def write_actual_table(node_id):
    output = subprocess.run(["ip", "-json", "route"], stdout=subprocess.PIPE)
    with open(os.path.join("/shared", node_id, "actual_table.json"), "w") as f:
        json.dump(
            index_list_by_key(
                list=json.loads(output.stdout.decode("utf-8")), key="dst"
            ),
            f,
            indent=4,
            sort_keys=True,
        )


def log(msg, node_id):
    print(msg)
    with (open(os.path.join("/shared", node_id, "log.txt"), "a+")) as f:
        f.write(msg + " \n")


def run(node_id, window_size, threshold):
    with daemon.DaemonContext():
        try:
            sw = sliding_window(window_size, threshold)
            nest_asyncio.apply()
            pcap_paths = glob.glob(os.path.join("shared", node_id, "eth*.pcap"))
            number_of_failed_attempts = 0
            did_converge = False

            while not did_converge:
                try:
                    result = sw.sliding_window_check(pcap_paths)
                    if (
                        result["code"] == 1
                        or number_of_failed_attempts >= MAXIMUM_FAILED_ATTEMPTS
                    ):
                        did_converge = True
                        if result["code"] == 1:
                            log(
                                "Node converged (average="
                                + str(result["average"])
                                + ")",
                                node_id,
                            )
                        if number_of_failed_attempts >= MAXIMUM_FAILED_ATTEMPTS:
                            log(
                                "Node has not yet converged but reached maximum attemps. Convergence is assumed.",
                                node_id,
                            )
                    else:
                        number_of_failed_attempts += 1
                        log(
                            f"Node has not yet converged on its {number_of_failed_attempts} failed attempt ({result['status']})",
                            node_id,
                        )
                        sleep(3)
                except Exception as e:
                    log("Tshark error: " + str(e), node_id)
            log("Writing actual table into shared folder...", node_id)
            write_actual_table(node_id)
            log("Connecting to server...", node_id)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                log("Sending message...", node_id)
                s.sendall(node_id.encode())
            log("Disconnected from TCP server. Process finished successfully.", node_id)
        except Exception as error:
            log("Unexpected error" + str(error), node_id)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3])
