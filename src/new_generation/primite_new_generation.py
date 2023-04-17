from copy import deepcopy
import random
from common.Genotype import Genotype

import networkx as nx

import common.line_generation as lg


def new_generation_replace_random_line(
    population_with_fitness: list[tuple[Genotype, float]],
    G: nx.Graph,
    new_generation_size: int,
    best_paths,
) -> list[Genotype]:
    new_generation: list[Genotype] = [
        organism_with_fitness[0] for organism_with_fitness in population_with_fitness
    ]

    counter = 0
    while len(new_generation) < new_generation_size:
        organism: Genotype = deepcopy(
            population_with_fitness[counter % len(population_with_fitness)][0]
        )

        line_to_remove = random.sample(organism.lines, 1)[0]

        organism.lines.remove(line_to_remove)

        organism.lines.append(lg.gen_random_line(G, best_paths))

        new_generation.append(organism)
        counter += 1

    return new_generation
