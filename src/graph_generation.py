import networkx as nx
import matplotlib.pyplot as plt

N = 30

graph = nx.generators.geographical_threshold_graph(n=N, theta=N * 0.8)

solitary=[ n for n in nx.algorithms.isolates(graph)]
graph.remove_nodes_from(solitary)


nx.drawing.draw_networkx(graph)
plt.show()