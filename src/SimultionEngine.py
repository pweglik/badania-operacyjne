from typing import Callable, List, Set, Tuple
import networkx as nx
from Genotype import Genotype
from show_graph import show_graph


class SimulationEngine:
    def __init__(
        self,
        G: nx.Graph,
        initial_population: List[Genotype],
        fitness_function: Callable[[Genotype, nx.Graph], float],
        survival_function: Callable[
            [List[Tuple[Genotype, float]]], List[Tuple[Genotype, float]]
        ],
        new_generation_function: Callable[
            [List[Tuple[Genotype, float]], nx.Graph], List[Genotype]
        ],
    ):
        self.G = G
        self.initial_population = initial_population
        self.fitness_function = fitness_function
        self.survival_function = survival_function
        self.new_generation_function = new_generation_function

    def run(self, no_of_generations: int = 100, report_every_n: int = 10):
        population: List[Genotype] = self.initial_population

        for i in range(no_of_generations + 1):
            print(f"Population {i}")
            # calculating fitness for all organisms
            population_with_fitness: List[Tuple[Genotype, float]] = [
                (organism, self.fitness_function(organism, self.G))
                for organism in population
            ]

            # applying survival function
            population_survived: List[Tuple[Genotype, float]] = self.survival_function(
                population_with_fitness
            )

            # generating new population form survived
            population = self.new_generation_function(population_survived, self.G)

            if i % report_every_n == 0:
                # save the best one to file
                show_graph(self.G, population_survived[0][0], i)
                print(self.fitness_function(population_survived[0][0], self.G))
