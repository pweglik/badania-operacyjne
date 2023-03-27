import networkx as nx
import matplotlib.pyplot as plt

dist = lambda x, y: sum(abs(a - b) for a, b in zip(x, y))
graph = nx.generators.geographical_threshold_graph(n=10, theta=0.8, metric=dist) 

nx.drawing.draw_networkx(graph)
plt.show()