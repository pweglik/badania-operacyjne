import random

from copy import deepcopy
import networkx as nx

import line_generation as lg
from Genotype import Genotype
from fitness import fitness
from params import (
    CHANCE_CREATE_LINE,
    CHANCE_CYCLE,
    CHANCE_ERASE_LINE,
    CHANCE_INVERT,
    CHANCE_MERGE,
    CHANCE_MERGE_SPECIMEN,
    CHANCE_ROT_CYCLE,
    CHANCE_ROT_RIGHT,
    CHANCE_SPLIT,
    N,
    N_IN_POPULATION,
    SEED,
    dprint,
)
from graph_generation import generate_city_graph
from SimultionEngine import SimulationEngine
from new_generation.Mutators import GenotypeMutator, LineMutator
from new_generation.SpecimenCrossers import GenotypeCrosser


def n_best_survive(
    population_with_fitness: list[tuple[Genotype, float]], n: int
) -> list[tuple[Genotype, float]]:
    sorted_generation = sorted(
        population_with_fitness, key=lambda item: item[1], reverse=True
    )

    return sorted_generation[:n]


def new_generation_replace_random_line(
    population_with_fitness: list[tuple[Genotype, float]],
    G: nx.Graph,
    new_generation_size: int,
    best_paths,
) -> list[Genotype]:
    # extract organisms only (ignore fitness) from population_with_fitness
    new_generation: list[Genotype] = [
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


def create_initial_population(G, best_paths) -> list[Genotype]:
    initial_population: list[Genotype] = []

    for _ in range(N_IN_POPULATION):
        lines = [lg.gen_random_line(G, best_paths) for _ in range(10)]

        genotype = Genotype(lines)

        initial_population.append(genotype)

    return initial_population


def run_simulation(show=False):
    G, best_paths = generate_city_graph(N)

    line_mutator = LineMutator(best_paths)
    genotype_mutator = GenotypeMutator(G, best_paths)

    genotype_crosser = GenotypeCrosser(best_paths)

    random.seed(SEED)

    def new_generation(
        population_with_fitness: list[tuple[Genotype, float]],
        G: nx.Graph,
        new_generation_size: int,
        best_paths,
    ) -> list[Genotype]:
        # extract organisms only (ignore fitness) from population_with_fitness
        new_generation: list[Genotype] = [
            organism_with_fitness[0]
            for organism_with_fitness in population_with_fitness
        ]

        if random.random() < CHANCE_MERGE_SPECIMEN:
            idx1 = random.randrange(len(new_generation))
            idx2 = idx1
            while idx1 == idx2:  # gen different
                idx2 = random.randrange(len(new_generation))

            g_new = genotype_crosser.merge_genotypes(
                new_generation[idx1], new_generation[idx2]
            )
            new_generation.append(g_new)

        counter = 0
        while len(new_generation) < new_generation_size:
            # get organism (clone it, don't modify original) by
            # looping over population_with_fitness with counter index
            organism: Genotype = deepcopy(
                population_with_fitness[counter % len(population_with_fitness)][0]
            )

            # print(counter % len(population_with_fitness), fitness(organism, G))

            # (operating on clone)

            # run line mutators
            # get random line, remove it, run line mutator on it, add it back
            random_line = random.sample(organism.lines, 1)[0]
            organism.lines.remove(random_line)

            if random.random() < CHANCE_ROT_RIGHT:
                random_line = line_mutator.rotation_to_right(random_line)
                dprint("ROT RIGHT", len(random_line.stops))

            if random.random() < CHANCE_ROT_CYCLE:
                random_line = line_mutator.cycle_rotation(random_line)
                dprint("ROT CYCLE", len(random_line.stops))

            if random.random() < CHANCE_INVERT:
                random_line = line_mutator.invert(random_line)
                dprint("INVERT", len(random_line.stops))

            if len(random_line.stops) > 0:
                organism.lines.append(random_line)

            if len(organism.lines) == 0:
                continue

            # run genotype mutators

            if random.random() < CHANCE_ERASE_LINE:
                organism = genotype_mutator.erase_line(organism)
                dprint("ERASE", organism.get_line_stops_count_summary())

            if len(organism.lines) == 0:
                continue

            if random.random() < CHANCE_CREATE_LINE:
                organism = genotype_mutator.create_line(organism)
                dprint("CREATE", organism.get_line_stops_count_summary())

            # split some line
            if random.random() < CHANCE_SPLIT:
                organism = genotype_mutator.split_line(organism)
                dprint("SPLIT", organism.get_line_stops_count_summary())

            # merge some lines
            if random.random() < CHANCE_MERGE and len(organism.lines) > 1:
                organism = genotype_mutator.merge_lines(organism)
                dprint("MERGE", organism.get_line_stops_count_summary())

            if random.random() < CHANCE_CYCLE:
                organism = genotype_mutator.cycle_stops_shift(organism)
                dprint("CYCLE", organism.get_line_stops_count_summary())

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

    sim_engine.run(100, 10, report_show=show)


if __name__ == "__main__":
    random.seed(SEED)

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

    run_simulation()
