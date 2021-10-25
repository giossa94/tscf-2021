from src.utils import create_fat_tree, read_config
from build_config_json import build_config
import subprocess,os,sys

# params = read_config('config.json')
print(f'Creating Fat Tree with K={sys.argv[1]}. The number of planes is 2 by default.')

params = build_config(int(sys.argv[1]))
config, output_dir, lab_dir = create_fat_tree(params, os.path.abspath('.')) #, args.dir, args.name, args.kube_net)

os.chdir(lab_dir)
subprocess.run(["kathara", "lstart", "--noterminals"])

output = subprocess.run(["kathara", "exec", "leaf_1_0_1", "ip", "route"], text=True, capture_output=True)

with open("./leaf_1_0_1__ip_table.txt", mode="w") as file:
  file.write(output.stdout)

subprocess.run(["kathara", "lclean"])
