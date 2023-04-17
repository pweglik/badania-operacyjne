from common.Genotype import Genotype
from common.params import N_IN_POPULATION


import common.line_generation as lg


def create_initial_population(G, best_paths) -> list[Genotype]:
    initial_population: list[Genotype] = []

    for _ in range(N_IN_POPULATION):
        lines = [lg.gen_random_line(G, best_paths) for _ in range(10)]

        genotype = Genotype(lines)

        initial_population.append(genotype)

    return initial_population
