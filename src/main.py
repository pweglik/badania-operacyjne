from typing import List, Tuple
import random

from copy import deepcopy
import networkx as nx

import src.line_generation as lg
from src.Genotype import Genotype
from src.fitness import fitness
from src.params import N, SEED, N_IN_POPULATION
from src.graph_generation import generate_city_graph
from src.SimultionEngine import SimulationEngine
from src.new_generation.Mutators import GenotypeMutator, LineMutator
from src.new_generation.SpecimenCrossers import GenotypeCrosser

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

    # extract organisms only (ignore fitness) from population_with_fitness
    new_generation: List[Genotype] = [
        organism_with_fitness[0] for organism_with_fitness in population_with_fitness
    ]

    counter = 0
    while len(new_generation) < new_generation_size:
        # get organism (clone it, don't modify original) by
        # looping over population_with_fitness with counter index
        organism: Genotype = deepcopy(
            population_with_fitness[counter % len(population_with_fitness)][0]
        )

        # (operating on clone)
        # get random line and delete it
        # random_line = random.sample(organism.lines, 1)[0]
        # organism.lines.remove(random_line)

        organism = GenotypeMutator(G, best_paths).split_line(organism)

        # generate random line and add it to clone
        # add clone itself to new generation
        # organism.lines.append(lg.gen_random_line(G, best_paths, 5))
        new_generation.append(organism)

        counter += 1

    return new_generation


def create_initial_population(
        G,
        best_paths
) -> List[Genotype]:
    initial_population: List[Genotype] = []

    for _ in range(N_IN_POPULATION):
        lines = [lg.gen_random_line(G, best_paths) for _ in range(10)]

        genotype = Genotype(lines)

        initial_population.append(genotype)

    return initial_population


if __name__ == '__main__':
    # G, best_paths = generate_city_graph(N)
    #
    # sim_engine = SimulationEngine(
    #     G,
    #     initial_population=create_initial_population(G, best_paths),
    #     fitness_function=fitness,
    #     survival_function=lambda population: n_best_survive(
    #         population, N_IN_POPULATION // 5
    #     ),
    #     new_generation_function=lambda population, graph: new_generation_replace_random_line(
    #         population, graph, N_IN_POPULATION, best_paths
    #     ),
    # )
    #
    # sim_engine.run(10, 1)

    CHANCE_INVERT = 0.1

    CHANCE_SPLIT = 0.1
    CHANCE_MERGE = 0.1

    G, best_paths = generate_city_graph(N)

    line_mutator = LineMutator(best_paths)
    genotype_mutator = GenotypeMutator(G, best_paths)

    genotype_crosser = GenotypeCrosser(best_paths)

    def new_generation(
            population_with_fitness: List[Tuple[Genotype, float]],
            G: nx.Graph,
            new_generation_size: int,
            best_paths,
    ) -> List[Genotype]:

        # extract organisms only (ignore fitness) from population_with_fitness
        new_generation: List[Genotype] = [
            organism_with_fitness[0] for organism_with_fitness in population_with_fitness
        ]

        counter = 0
        while len(new_generation) < new_generation_size:
            # get organism (clone it, don't modify original) by
            # looping over population_with_fitness with counter index
            organism: Genotype = deepcopy(
                population_with_fitness[counter % len(population_with_fitness)][0]
            )

            # (operating on clone)

            # run line mutators

            # get random line, remove it, run line mutator on it, add it back
            random_line = random.sample(organism.lines, 1)[0]
            organism.lines.remove(random_line)

            if random.random() < CHANCE_INVERT:
                random_line = line_mutator.invert(random_line)

            if len(random_line.stops) > 0:
                organism.lines.append(random_line)

            if len(organism.lines) == 0:
                continue

            # run genotype mutators

            # split some line
            if random.random() < CHANCE_SPLIT:
                organism = genotype_mutator.split_line(organism)

            # merge some lines
            if random.random() < CHANCE_MERGE:
                organism = genotype_mutator.merge_lines(organism)

            # add clone to new generation
            new_generation.append(organism)

            counter += 1

        return new_generation


    sim_engine = SimulationEngine(
        G,
        initial_population=create_initial_population(G, best_paths),
        fitness_function=fitness,
        survival_function=lambda population: n_best_survive(
            population, N_IN_POPULATION // 5
        ),
        new_generation_function=lambda population, graph: new_generation(
            population, graph, N_IN_POPULATION, best_paths
        ),
    )

    sim_engine.run(1000, 100, report_show=False)
