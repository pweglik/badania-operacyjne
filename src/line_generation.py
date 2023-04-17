import random
import networkx as nx
from Line import Line


def gen_random_line(
    G: nx.Graph, best_paths: dict[int, dict[int, list[int]]], length: int = 5
) -> Line:
    vertices = random.sample(list(G.nodes), length)

    return Line(vertices, best_paths)
