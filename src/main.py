import numpy as np
import random

import networkx as nx

import line_generation as lg
from Genotype import Genotype
from show_graph import show_graph
from fitness import fitness
from params import N, SEED


random.seed(SEED)
rng = np.random.default_rng(SEED)


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
    G[edge[0]][edge[1]]["weight"] = weights[edge[0]][edge[1]]

# mockup for tests, this should be
# set manually or be derived from population density
points = rng.random(G.number_of_nodes()) * 10
G.graph["points"] = points

best_paths = dict(nx.all_pairs_shortest_path(G))

lines = set([lg.gen_random_line(G, best_paths) for _ in range(5)])

genotype = Genotype(len(lines), lines)


print(fitness(genotype, G))
show_graph(G, genotype)
