# Python program for Dijkstra's single
# source shortest path algorithm. The program is
# for adjacency matrix representation of the graph

# Library for INT_MAX
import sys


# This code is contributed by Divyanshu Mehta

class Graph():

    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)]
                    for row in range(vertices)]

    def printSolution(self, dist):
        # print("Vertex tDistance from Source")
        for node in range(self.V):
            # print(node, "t", dist[node])
            print(f'Al nodo {node} se llega con costo {dist[node]}')

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

        self.printSolution(dist)

def build_fat_tree_graph():
    # Formulas used:
    #   Number of Planes: k_leaf / r
    #   Number of PoDs: (k_leaf + k_top) / r
    #   Number of Leaf per PoD: k_top
    #   Number of ToP per PoD: k_leaf
    #   Number of ToFs: k_top * (k_leaf / r)
  
    fat_tree = Graph(20)
    for row_number,row in enumerate(fat_tree.graph):
        if row_number in range(8) and row_number % 2 == 0:
            fat_tree.graph[row_number][row_number+8] = 1
            fat_tree.graph[row_number+8][row_number] = 1
            fat_tree.graph[row_number][row_number+8+1] = 1
            fat_tree.graph[row_number+8+1][row_number] = 1  
        elif row_number in range(8) and row_number % 2 == 1:
            fat_tree.graph[row_number][row_number+8-1] = 1
            fat_tree.graph[row_number+8-1][row_number] = 1
            fat_tree.graph[row_number][row_number+8] = 1
            fat_tree.graph[row_number+8][row_number] = 1
        elif row_number in range(8,16) and row_number % 2 == 0:
            fat_tree.graph[row_number][16] = 1
            fat_tree.graph[16][row_number] = 1
            fat_tree.graph[row_number][17] = 1
            fat_tree.graph[17][row_number] = 1  
        elif row_number in range(8,16) and row_number % 2 == 1:
            fat_tree.graph[row_number][18] = 1
            fat_tree.graph[18][row_number] = 1
            fat_tree.graph[row_number][19] = 1
            fat_tree.graph[19][row_number] = 1  
        for i in range(20):
            if row_number!=i and fat_tree.graph[row_number][i]==0:
                fat_tree.graph[row_number][i] = 99
    return fat_tree       


if __name__ == '__main__':
    k4 = build_fat_tree_graph() 
    k4.dijkstra(0)