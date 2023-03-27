import networkx as nx
import matplotlib.pyplot as plt

G = nx.generators.geographical_threshold_graph(n=10, theta=4.5, seed=0)
pos = nx.spring_layout(G, seed=0)

line1 = [9, 2, 3]
edges = [(u, v) for u, v in zip(line1, line1[1:])]

# colors = {(u, v): {'color': 'red'} for (u, v) in edges}
# nx.set_edge_attributes(G, colors)

nx.drawing.draw_networkx_edges(G, pos, edgelist=edges, edge_color='red')

nx.drawing.draw_networkx(G, pos)
plt.show()