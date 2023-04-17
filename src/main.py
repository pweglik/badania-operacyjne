import random

from copy import deepcopy
import networkx as nx

import line_generation as lg
from Genotype import Genotype
from fitness import fitness
from simulation import new_generation_random

from graph_generation import generate_city_graph
from SimultionEngine import SimulationEngine
from new_generation.Mutators import GenotypeMutator, LineMutator
from new_generation.SpecimenCrossers import GenotypeCrosser
from src.params import N_IN_POPULATION, SEED, N


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


def run_simulation(
    G, best_paths, no_of_generations: int, report_every_n: int, report_show: bool
):
    line_mutator = LineMutator(best_paths)
    genotype_mutator = GenotypeMutator(G, best_paths)
    genotype_crosser = GenotypeCrosser(best_paths)

    sim_engine = SimulationEngine(
        G,
        initial_population=create_initial_population(G, best_paths),
        fitness_function=fitness,
        survival_function=lambda population: n_best_survive(
            population, N_IN_POPULATION // 5
        ),
        new_generation_function=lambda population, graph: new_generation_random(
            population,
            N_IN_POPULATION,
            line_mutator,
            genotype_mutator,
            genotype_crosser,
        ),
    )

    sim_engine.run(no_of_generations, report_every_n, report_show=report_show)


if __name__ == "__main__":
    random.seed(SEED)

    G, best_paths = generate_city_graph(N)

    run_simulation(G, best_paths, 10, 1, False)
