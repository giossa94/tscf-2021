import json, sys, os
from graph import build_fat_tree_from_lab
# Python program for Dijkstra's single
# source shortest path algorithm. The program is
# for adjacency matrix representation of the graph

# This code is contributed by Divyanshu Mehta 
#(https://www.geeksforgeeks.org/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/)


def printSolution(G, dist,path_dict,src):
    for node in range(G.V):
        print(f'Origen: {G.names[src]}\nDestino: {G.names[node]}')
        print(f'Camino: {[G.names[x] for x in path_dict[node]]} (costo {dist[node]})\n')

# A utility function to find the vertex with
# minimum distance value, from the set of vertices
# not yet included in shortest path tree
def minDistance(G, dist, sptSet):

    # Initialize minimum distance for next node
    min = sys.maxsize

    # Search not nearest vertex not in the
    # shortest path tree
    for v in range(G.V):
        if dist[v] < min and sptSet[v] == False:
            min = dist[v]
            min_index = v

    return min_index

# Funtion that implements Dijkstra's single source
# shortest path algorithm for a graph represented
# using adjacency matrix representation
def dijkstra(G, src):

    dist = [sys.maxsize] * G.V
    dist[src] = 0
    sptSet = [False] * G.V

    path_dict = {k:[] for k in range(G.V)}
    for cout in range(G.V):

        # Pick the minimum distance vertex from
        # the set of vertices not yet processed.
        # u is always equal to src in first iteration
        u = minDistance(G,dist, sptSet)

        # Put the minimum distance vertex in the
        # shortest path tree
        sptSet[u] = True

        # Update dist value of the adjacent vertices
        # of the picked vertex only if the current
        # distance is greater than new distance and
        # the vertex in not in the shortest path tree
        for v in range(G.V):
            if G.graph[u][v] > 0 and sptSet[v] == False and dist[v] > (dist[u] + G.graph[u][v]):
                dist[v] = dist[u] + G.graph[u][v]
                path_dict[v] = [step for step in path_dict[u]] + [v]

    printSolution(G,dist,path_dict,src)

if __name__ == '__main__':
    print('=== Dijkstra desde el nodo 0 ===')
    k4 = build_fat_tree_from_lab('fat_tree_2_2_1+1_1_1+bgp')
    dijkstra(k4,0)