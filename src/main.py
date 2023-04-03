import numpy as np
import random

import networkx as nx

import line_generation as lg
from Genotype import Genotype
from show_graph import show_graph

# hyperparameters
SEED = 46
N = 30  # number of vertices


random.seed(SEED)

G = nx.generators.geometric.geographical_threshold_graph(
    n=N,
    theta=N * 0.8,
    seed=SEED,
)

solitary = [n for n in nx.algorithms.isolate.isolates(G)]
G.remove_nodes_from(solitary)

positions = nx.function.get_node_attributes(G, "pos")

weights = np.zeros((N, N))

for node1, pos1 in positions.items():
    for node2, pos2 in positions.items():
        weights[node1][node2] = weights[node2][node1] = np.linalg.norm(
            np.array([pos1[0] - pos2[0], pos1[1] - pos2[1]])
        )


for edge in G.edges:
    G[edge[0]][edge[1]]['weight'] = weights[edge[0]][edge[1]]


# list of paths
# double indexed by vertice number

# TODO no idea from where this gets distances
# it should from geographical_threshold_graph
# metric which is euclidean by default
best_paths = dict(nx.all_pairs_shortest_path(G))


lines = [
    lg.gen_random_line_random_vertices(G, best_paths, 10),
    lg.gen_random_line_random_paths(G, 10),
    lg.gen_random_line_random_paths(G, 4),
    lg.gen_random_line_random_paths(G, 7),
    lg.gen_random_line_random_paths(G, 4),
    lg.gen_random_line_random_paths(G, 5),
    lg.gen_random_line_random_paths_recursive(G, 15),
]

genotype = Genotype(len(lines), lines)
show_graph(G, genotype)
