
def build_config(k: int, planes: int = 2):
    if k % 2 != 0:
        raise Exception("Input error: k must be an even number!") 
    if (k/2) % planes != 0:
        raise Exception("Input error: The number of planes must be a divisor of k/2!") 

    config = {
        "k_leaf": int(k/2),
        "k_top": int(k/2),
        "redundancy_factor": int((k/2)/planes),
        "n_pods": k,
        "servers_for_rack": 1,
        "tof_rings": 'false',
        "leaf_spine_parallel_links": 1,
        "spine_tof_parallel_links": 1,
        "ring_parallel_links": 1,
        "protocol": "bgp"
    }
    return config

if __name__== '__main__':
    try:
        print(build_config(8))
    except Exception as e:
        print(e)