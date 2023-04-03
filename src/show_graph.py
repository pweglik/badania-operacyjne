import collections

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from functools import reduce

from Genotype import Genotype
from Line import Line


def show_graph(G: nx.Graph, genotype: Genotype):
    pos = nx.spring_layout(G, seed=0)
    nx.drawing.draw_networkx(G, pos)

    edges_size = defaultdict(list)

    for i, line in enumerate(genotype.lines):
        stops = line.stops
        edges = [(u, v) for u, v in zip(stops, stops[1:])]
        for u, v in edges:
            edges_size[(min(u, v), max(u, v))].append(line)

    for (u, v), lines in edges_size.items():
        for i, line in enumerate(lines):
            w = (len(lines)-i)*4
            nx.drawing.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=line.edge_color, width=w)

        label = ', '.join(map(lambda x: str(x.id), lines))

        nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): label}, font_size=8)

    plt.show()


if __name__ == '__main__':
    l1 = Line([0, 1, 4, 5, 6, 9, 10])
    l2 = Line([2, 3, 4, 5, 6, 7, 8])
    l3 = Line([4, 5, 6])
    g = Genotype(2, [l1, l2])

    G1 = nx.path_graph(l1.stops)
    G1.add_nodes_from([2, 3, 7, 8])
    G1.add_edges_from([(2, 3), (3, 4), (6, 7), (7, 8)])

    show_graph(G1, g)


    print('main')