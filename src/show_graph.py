import math
from typing import Dict, List, Tuple

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

from Genotype import Genotype
from src.Line import Line


def show_graph(G: nx.Graph, genotype: Genotype, gen_number: int = 0, show: bool = False):
    pos = nx.drawing.layout.spring_layout(G, seed=0)
    nx.drawing.nx_pylab.draw_networkx(G, pos, node_color="gray")

    edges_lines: Dict[Tuple[int, int], List[Line]] = defaultdict(list)
    node_sizes: Dict[Tuple[int], int] = defaultdict(int)

    for i, line in enumerate(genotype.lines):
        edges = line.edges
        for u, v in edges:
            edges_lines[(min(u, v), max(u, v))].append(line)
            node_sizes[u] += 1
            node_sizes[v] += 1

    for (u, v), lines in edges_lines.items():
        for i, line in enumerate(lines):
            w = (len(lines) - i) * 4
            nx.drawing.nx_pylab.draw_networkx_edges(
                G, pos, edgelist=[(u, v)], edge_color=line.edge_color, width=w
            )

        label = ", ".join(map(lambda x: str(x.id), lines))

        nx.drawing.nx_pylab.draw_networkx_edge_labels(
            G, pos, edge_labels={(u, v): label}, font_size=8
        )

    node_colors = list(map(math.sqrt, node_sizes.values()))
    v_max = max(node_colors)
    nx.drawing.nx_pylab.draw_networkx_nodes(
        G,
        pos,
        nodelist=node_sizes.keys(),
        node_color=node_colors,
        vmin=0,
        vmax=v_max + 1,
        cmap=plt.cm.Greens,
    )

    if show:
        plt.show()
    else:
        plt.savefig(f"../results/gen_{gen_number}.svg")
        plt.clf()


if __name__ == "__main__":
    verticies = [0, 1, 4, 5, 6, 9, 10]
    G1 = nx.generators.classic.path_graph(verticies)
    best_paths = dict(nx.all_pairs_shortest_path(G1))

    l1 = Line(verticies, best_paths)
    l2 = Line([2, 3, 4, 5, 6, 7, 8], best_paths)
    l3 = Line([4, 5, 6], best_paths)
    g = Genotype(set([l1, l2]))

    G1.add_nodes_from([2, 3, 7, 8])
    G1.add_edges_from([(2, 3), (3, 4), (6, 7), (7, 8)])

    show_graph(G1, g)
