from typing import Tuple, Any
import numpy as np

import networkx as nx

import line_generation as lg
from params import GRAPH_SEED


def generate_city_graph(n: int) -> Tuple[nx.Graph, Any]:
    rng = np.random.default_rng(GRAPH_SEED)

    G = nx.generators.geometric.geographical_threshold_graph(
        n=n,
        theta=n * 0.8,
        seed=GRAPH_SEED,
    )

    solitary = [n for n in nx.algorithms.isolate.isolates(G)]
    G.remove_nodes_from(solitary)

    positions = nx.function.get_node_attributes(G, "pos")

    weights = np.zeros((n, n))

    for node1, pos1 in positions.items():
        for node2, pos2 in positions.items():
            weights[node1][node2] = weights[node2][node1] = np.linalg.norm(
                np.array([pos1[0] - pos2[0], pos1[1] - pos2[1]])
            )

    for edge in G.edges:
        G[edge[0]][edge[1]]["weight"] = weights[edge[0]][edge[1]]

    # mockup for tests, this should be
    # set manually or be derived from population density
    points = rng.random(G.number_of_nodes()) * 10
    G.graph["points"] = points

    best_paths = dict(nx.all_pairs_shortest_path(G))

    return (G, best_paths)
