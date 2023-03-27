import networkx as nx
import matplotlib.pyplot as plt

import random

from Line import Line

dist = lambda x, y: sum(abs(a - b) for a, b in zip(x, y))
graph = nx.generators.geographical_threshold_graph(n=10, theta=0.8, metric=dist) 

def gen_random_line(length):
    V = random.sample(list(graph.nodes), length)
    # random.shuffle(V)
    line = Line(V, graph)
    print(line.stops)
    print(line.edges)


gen_random_line(3)

# nx.drawing.draw_networkx(graph)
# plt.show()
