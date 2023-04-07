from typing import List, Tuple
import random

from copy import deepcopy
import networkx as nx

import line_generation as lg
from Genotype import Genotype
from fitness import fitness
from params import N, SEED, N_IN_POPULATION
from graph_generation import generate_city_graph
from SimultionEngine import SimulationEngine


random.seed(SEED)


def n_best_survive(
    population_with_fitness: List[Tuple[Genotype, float]], n: int
) -> List[Tuple[Genotype, float]]:
    sorted_generation = sorted(
        population_with_fitness, key=lambda item: item[1], reverse=True
    )

    return sorted_generation[:n]


def new_generation_replace_random_line(
    population_with_fitness: List[Tuple[Genotype, float]],
    G: nx.Graph,
    new_generation_size: int,
    best_paths,
) -> List[Genotype]:
    new_generation: List[Genotype] = [
        organism_with_fitness[0] for organism_with_fitness in population_with_fitness
    ]

    counter = 0
    while len(new_generation) < new_generation_size:
        organism: Genotype = deepcopy(
            population_with_fitness[counter % len(population_with_fitness)][0]
        )

        line_to_remove = random.sample(organism.lines, 1)[0]

        organism.lines.remove(line_to_remove)

        organism.lines.append(lg.gen_random_line(G, best_paths, 5))

        new_generation.append(organism)
        counter += 1

    return new_generation


G, best_paths = generate_city_graph(N)

# creating inital population

initial_population: List[Genotype] = []

for _ in range(N_IN_POPULATION):
    lines = [lg.gen_random_line(G, best_paths) for _ in range(10)]

    genotype = Genotype(len(lines), lines)

    initial_population.append(genotype)


sim_engine = SimulationEngine(
    G,
    initial_population=initial_population,
    fitness_function=fitness,
    survival_function=lambda population: n_best_survive(
        population, N_IN_POPULATION // 5
    ),
    new_generation_function=lambda population, graph: new_generation_replace_random_line(
        population, graph, N_IN_POPULATION, best_paths
    ),
)

sim_engine.run(1000, 200)
