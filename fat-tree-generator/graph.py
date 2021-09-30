import json, sys, os

# This code is contributed by Divyanshu Mehta 
#(https://www.geeksforgeeks.org/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/)

class Graph():

    def __init__(self, vertices,names):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)]
                    for row in range(vertices)]
        self.names = names

def build_fat_tree_from_lab(path_to_lab):
    node_neighbours = {}
    tof = []
    spine = []
    leaf = []
    server = []
    
    # Get every node's name from lab.json and the name of their neighbours as well
    with open(os.path.join(path_to_lab,'lab.json')) as json_file:
        lab_json = json.load(json_file)
        for tof_node in lab_json['aggregation_layer']:
            node_neighbours[tof_node] = []
            tof.append(tof_node)
            interfaces = lab_json['aggregation_layer'][tof_node]['interfaces']
            for interface in interfaces:
                if interface['collision_domain'] != 'lo':
                    for neighbour in interface['neighbours']:
                        node_neighbours[tof_node] += [(neighbour[0],neighbour[1])]
        print(node_neighbours)
        for pod in lab_json['pod']:
            for node in lab_json['pod'][pod]:
                node_neighbours[node] = []
                if node.startswith('spine'): spine.append(node)
                elif node.startswith('leaf'): leaf.append(node)
                elif node.startswith('server'): server.append(node)
                interfaces = lab_json['pod'][pod][node]['interfaces']
                for interface in interfaces:
                    if interface['collision_domain'] != 'lo':
                        for neighbour in interface['neighbours']:
                            node_neighbours[node] += [(neighbour[0],neighbour[1])]

    # Each node in the topology must have an id
    names = {}
    for number, node in enumerate(leaf + spine + tof + server):
        names[number] = node
    
    
    # Generate adjacency matrix representation of the topology
    # Graph object also has the id-name dictionary (self.names)
    fat_tree = Graph(len(names.keys()), names)
    for row_number in range(len(fat_tree.graph)):
        for column_number in range(len(fat_tree.graph)):
            neighbour_names = [x[0] for x in node_neighbours[names[row_number]]]
            if names[row_number] == names[column_number]:
                fat_tree.graph[row_number][column_number] = 0
            elif names[column_number] in neighbour_names:
                fat_tree.graph[row_number][column_number] = 1
            else:
                fat_tree.graph[row_number][column_number] = sys.maxsize
    
    return fat_tree
