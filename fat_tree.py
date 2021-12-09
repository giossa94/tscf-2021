import os
from fat_tree_generator.src.utils import create_fat_tree


def build_config(k: int = 4, planes: int = 2):
    if k % 2 != 0:
        raise Exception("Input error: k must be an even number!")
    if (k / 2) % planes != 0:
        raise Exception("Input error: The number of planes must be a divisor of k/2!")

    config = {
        "k_leaf": int(k / 2),
        "k_top": int(k / 2),
        "redundancy_factor": int((k / 2) / planes),
        "n_pods": k,
        "servers_for_rack": 1,
        "tof_rings": False,
        "leaf_spine_parallel_links": 1,
        "spine_tof_parallel_links": 1,
        "ring_parallel_links": 1,
        "protocol": "bgp",
    }

    return config


def build_fat_tree(params, exp_id):
    dir_name = "fat_tree_%d_%d_%d+%d_%d_%d+%s+%s" % (
        params["k_leaf"],
        params["k_top"],
        params["redundancy_factor"],
        params["leaf_spine_parallel_links"],
        params["spine_tof_parallel_links"],
        params["ring_parallel_links"],
        params["protocol"],
        exp_id,
    )

    # Check if the requested topology already exists.
    if os.path.exists(dir_name):
        output_dir = dir_name
        lab_dir = os.path.join(dir_name, "lab")
    else:
        _, output_dir, lab_dir = create_fat_tree(
            params, os.path.abspath("."), dir_name=dir_name
        )

    return output_dir, lab_dir
