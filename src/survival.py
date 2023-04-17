from common.Genotype import Genotype


def n_best_survive(
    population_with_fitness: list[tuple[Genotype, float]], n: int
) -> list[tuple[Genotype, float]]:
    sorted_generation = sorted(
        population_with_fitness, key=lambda item: item[1], reverse=True
    )

    return sorted_generation[:n]
