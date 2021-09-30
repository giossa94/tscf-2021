import json, sys, os
from graph import build_fat_tree_from_lab

def dijkstra_ECMP(G, src):
    pass

if __name__ == '__main__':
    print('=== Dijkstra desde el nodo 0 ===')
    k4 = build_fat_tree_from_lab('fat_tree_2_2_1+1_1_1+bgp')
    dijkstra_ECMP(k4,0)