import random
import networkx as nx
from common.Line import Line


def gen_random_line(G: nx.Graph, best_paths: dict[int, dict[int, list[int]]]) -> Line:
    number_of_verticies = random.randint(2, len(G.nodes) * 2 // 3)
    vertices = random.sample(list(G.nodes), number_of_verticies)

    return Line(vertices, best_paths)
