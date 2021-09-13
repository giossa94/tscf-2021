from src.utils import create_fat_tree, read_config
import subprocess
import os

params = read_config('config.json')

config, output_dir, lab_dir = create_fat_tree(params, os.path.abspath('.')) #, args.dir, args.name, args.kube_net)


os.chdir(lab_dir)
subprocess.run(["kathara", "lstart", "--noterminals"])

output = subprocess.run(["kathara", "exec", "leaf_1_0_1", "ip", "route"], text=True, capture_output=True)

with open("./leaf_1_0_1__ip_table.txt", mode="w") as file:
  file.write(output.stdout)

subprocess.run(["kathara", "lclean"])
