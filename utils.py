def index_list_by_key(list, key):
    return {item[key]: item for item in list}


def update_node_config_file(nodes, line_template, get_path):
    for node in nodes:
        path = get_path(node)
        with (open(path, "r")) as startup:
            lines = startup.readlines()
        line = line_template % node
        if line not in lines:
            with (open(path, "a+")) as startup:
                startup.write(line)
