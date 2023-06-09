from random import choices
from typing import Callable
from common.Genotype import Genotype
import numpy as np
from utils import exp_pdf_for_range


def _partition(
    population_with_fitness: list[tuple[Genotype, float]],
    kth: list[int],
) -> np.ndarray:
    partitioned = np.empty_like(population_with_fitness, dtype=object)
    partitioned[:] = population_with_fitness

    partitioned = partitioned[partitioned[:, 1].argpartition(kth=-np.array(kth))]

    return np.flip(partitioned, axis=0)


def n_best_survive(
    population_with_fitness: list[tuple[Genotype, float]],
    n: int,
) -> list[tuple[Genotype, float]]:
    return list(_partition(population_with_fitness, [n])[:n])


def n_best_and_m_random_survive(
    population_with_fitness: list[tuple[Genotype, float]], n: int, m: int
) -> list[tuple[Genotype, float]]:
    if n + m > len(population_with_fitness):
        raise ValueError("n + m > len(population_with_fitness)")

    partitioned = list(_partition(population_with_fitness, [n])[:n])

    return partitioned[:n] + choices(partitioned[m:], k=m)


def n_best_and_m_worst_survive(
    population_with_fitness: list[tuple[Genotype, float]],
    n: int,
    m: int,
) -> list[tuple[Genotype, float]]:
    tail_idx = max(n, len(population_with_fitness) - m)
    partitioned = _partition(population_with_fitness, [n, tail_idx - 1])

    return list(np.concatenate(partitioned[:n], partitioned[tail_idx:]))


def custom_decision_function_suvival(
    population_with_fitness: list[tuple[Genotype, float]],
    decision_function: Callable[[int, float, Genotype], bool],
) -> list[tuple[Genotype, float]]:
    sorted_generation = sorted(
        population_with_fitness, key=lambda item: item[1], reverse=True
    )

    return [
        (gen, fit)
        for i, (gen, fit) in enumerate(sorted_generation)
        if decision_function(i, fit, gen)
    ]


def custom_decision_function_with_normalized_fitness_suvival(
    population_with_fitness: list[tuple[Genotype, float]],
    decision_function: Callable[[int, float, Genotype], bool],
) -> list[tuple[Genotype, float]]:
    sorted_generation = sorted(
        population_with_fitness, key=lambda item: item[1], reverse=True
    )
    key = lambda item: item[1]
    min_fit = min(population_with_fitness, key=key)[1]
    max_fit = max(population_with_fitness, key=key)[1]

    def scaler(number: float) -> float:
        return (number - min_fit) / (max_fit - min_fit)

    return [
        (gen, fit)
        for i, (gen, fit) in enumerate(sorted_generation)
        if decision_function(i, scaler(fit), gen)
    ]


def rank_based_survival(
    population_with_fitness: list[tuple[Genotype, float]],
    decision_function: Callable[[int, Genotype], bool],
) -> list[tuple[Genotype, float]]:
    sorted_generation = sorted(
        population_with_fitness, key=lambda item: item[1], reverse=True
    )

    return [
        (gen, fit)
        for i, (gen, fit) in enumerate(sorted_generation)
        if decision_function(i, gen)
    ]


def _exponentional_delegate(
    sorted_generation: np.ndarray,
    n: int,
    lambda_param: float,
) -> list[tuple[Genotype, float]]:
    return list(
        np.random.choice(
            sorted_generation,
            replace=False,
            p=exp_pdf_for_range(
                np.arange(len(sorted_generation)), len(sorted_generation), lambda_param
            ),
            size=n,
        )
    )


def exponentional_survival(
    population_with_fitness: list[tuple[Genotype, float]],
    n: int,
    lambda_param: float,
) -> list[tuple[Genotype, float]]:
    sorted_generation = sorted(
        population_with_fitness, key=lambda item: item[1], reverse=True
    )
    numpy_sorted_generation = np.empty(len(sorted_generation), dtype=object)
    numpy_sorted_generation[:] = sorted_generation
    return _exponentional_delegate(numpy_sorted_generation, n, lambda_param)


def exponentional_survival_with_protection(
    population_with_fitness: list[tuple[Genotype, float]],
    survivors: int,
    lambda_param: float,
    best_protected: int,
    worst_protected: int,
) -> list[tuple[Genotype, float]]:
    best_protected = min(best_protected, len(population_with_fitness))
    tail_idx = max(best_protected, len(population_with_fitness) - worst_protected)
    worst_protected = len(population_with_fitness) - tail_idx
    partitioned = _partition(population_with_fitness, [best_protected, tail_idx - 1])

    return _exponentional_delegate(
        partitioned[best_protected:tail_idx],
        survivors - best_protected - worst_protected,
        lambda_param,
    )
