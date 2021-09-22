import json, sys, os
# Python program for Dijkstra's single
# source shortest path algorithm. The program is
# for adjacency matrix representation of the graph

# This code is contributed by Divyanshu Mehta 
#(https://www.geeksforgeeks.org/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/)

class Graph():

    def __init__(self, vertices,names):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)]
                    for row in range(vertices)]
        self.names = names

    def printSolution(self, dist,path_dict,src):
        for node in range(self.V):
            print(f'Origen: {self.names[src]}\nDestino: {self.names[node]}')
            print(f'Camino: {[self.names[x] for x in path_dict[node]]} (costo {dist[node]})\n')

    # A utility function to find the vertex with
    # minimum distance value, from the set of vertices
    # not yet included in shortest path tree
    def minDistance(self, dist, sptSet):

        # Initialize minimum distance for next node
        min = sys.maxsize

        # Search not nearest vertex not in the
        # shortest path tree
        for v in range(self.V):
            if dist[v] < min and sptSet[v] == False:
                min = dist[v]
                min_index = v

        return min_index

    # Funtion that implements Dijkstra's single source
    # shortest path algorithm for a graph represented
    # using adjacency matrix representation
    def dijkstra(self, src):

        dist = [sys.maxsize] * self.V
        dist[src] = 0
        sptSet = [False] * self.V

        path_dict = {k:[] for k in range(self.V)}
        for cout in range(self.V):

            # Pick the minimum distance vertex from
            # the set of vertices not yet processed.
            # u is always equal to src in first iteration
            u = self.minDistance(dist, sptSet)

            # Put the minimum distance vertex in the
            # shortest path tree
            sptSet[u] = True

            # Update dist value of the adjacent vertices
            # of the picked vertex only if the current
            # distance is greater than new distance and
            # the vertex in not in the shortest path tree
            for v in range(self.V):
                if self.graph[u][v] > 0 and    sptSet[v] == False and dist[v] > (dist[u] + self.graph[u][v]):
                    dist[v] = dist[u] + self.graph[u][v]
                    path_dict[v] = [step for step in path_dict[u]] + [v]

        self.printSolution(dist,path_dict,src)

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
            for neighbour in lab_json['aggregation_layer'][tof_node]['neighbours']:
                node_neighbours[tof_node] += [neighbour[0]]
        for pod in lab_json['pod']:
            for node in lab_json['pod'][pod]:
                node_neighbours[node] = []
                if node.startswith('spine'): spine.append(node)
                elif node.startswith('leaf'): leaf.append(node)
                elif node.startswith('server'): server.append(node)
                for neighbour in lab_json['pod'][pod][node]['neighbours']:
                    node_neighbours[node] += [neighbour[0]]

    # Each node in the topology must have an id
    names = {}
    for number, node in enumerate(leaf + spine + tof + server):
        names[number] = node
    
    # Generate adjacency matrix representation of the topology
    # Graph object also has the id-name dictionary (self.names)
    fat_tree = Graph(len(names.keys()), names)
    for row_number in range(len(fat_tree.graph)):
        for column_number in range(len(fat_tree.graph)):
            if names[row_number] == names[column_number]:
                fat_tree.graph[row_number][column_number] = 0
            elif names[column_number] in node_neighbours[names[row_number]]:
                fat_tree.graph[row_number][column_number] = 1
            else:
                fat_tree.graph[row_number][column_number] = sys.maxsize
    
    return fat_tree

if __name__ == '__main__':
    print('=== Dijkstra desde el nodo 0 ===')
    k4 = build_fat_tree_from_lab('fat_tree_2_2_1+1_1_1+bgp')
    k4.dijkstra(0)