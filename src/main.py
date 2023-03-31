import random

import networkx as nx

import src.line_generation as lg
from src.Genotype import Genotype
from src.show_graph import show_graph

# hyperparameters
SEED = 46
N = 30     # number of vertices



random.seed(SEED)

G = nx.generators.geographical_threshold_graph(
    n=N,
    theta=N * 0.8,
    seed=SEED,
)

solitary = [n for n in nx.algorithms.isolates(G)]
G.remove_nodes_from(solitary)

# list of paths
# double indexed by vertice number

# TODO no idea from where this gets distances
# it should from geographical_threshold_graph
# metric which is euclidean by default
best_paths = dict(nx.all_pairs_shortest_path(G))


lines = [
    # lg.gen_random_line_random_vertices(G, best_paths, 10)

    lg.gen_random_line_random_paths(G, 10),
    lg.gen_random_line_random_paths(G, 4),
    lg.gen_random_line_random_paths(G, 7),
    lg.gen_random_line_random_paths(G, 4),
    lg.gen_random_line_random_paths(G, 5),

    lg.gen_random_line_random_paths_recursive(G, 15)
]

genotype = Genotype(len(lines), lines)
show_graph(G, genotype)