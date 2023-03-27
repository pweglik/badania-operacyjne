import networkx as nx
import matplotlib.pyplot as plt

import random

from Line import Line

N = 30

graph = nx.generators.geographical_threshold_graph(n=N, theta=N * 0.8)

solitary=[ n for n in nx.algorithms.isolates(graph)]
graph.remove_nodes_from(solitary)


def gen_random_line(length):
    V = random.sample(list(graph.nodes), length)
    # random.shuffle(V)
    line = Line(V, graph)
    print(line.stops)
    #print(line.edges)
    for u, v in line.edges:
        print(u, v)
        graph.add_edge(u, v, color='r', weight=3)


gen_random_line(10)

colors = [graph[u][v]['color'] if 'color' in graph[u][v] else "black" for u,v in graph.edges()]
weights = [graph[u][v]['weight'] if 'weight' in graph[u][v] else 1 for u,v in graph.edges()]

nx.draw(graph, with_labels=True, edge_color=colors, width=weights)
plt.show()
