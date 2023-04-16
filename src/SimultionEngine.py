from typing import Callable, List, Tuple
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
        """
        Creates simulation
        :param G: City graph
        :param initial_population: First population
        :param fitness_function: Calculates some metric for organism, result passed to survival_function
        :param survival_function: Implements dying of the weakest organisms
        :param new_generation_function: Implements mutations/crossing/etc.
        """
        self.G = G
        self.initial_population = initial_population
        self.fitness_function = fitness_function
        self.survival_function = survival_function
        self.new_generation_function = new_generation_function

    def run(self, no_of_generations: int = 100, report_every_n: int = 10, report_show: bool = False):
        """

        :param no_of_generations: run for X generation
        :param report_every_n: every N, draw or save graph as picture
        :param report_show: if <True> run plt.show(), otherwise plt.savefig(...)
        """
        population: List[Genotype] = self.initial_population

        for i in range(no_of_generations + 1):
            # calculating fitness for all organisms
            population_with_fitness: List[Tuple[Genotype, float]] = [
                (organism, self.fitness_function(organism, self.G))
                for organism in population
            ]

            # applying survival function
            population_survived: List[Tuple[Genotype, float]] = self.survival_function(
                population_with_fitness
            )

            # generating new population from survived
            population = self.new_generation_function(population_survived, self.G)

            if i % report_every_n == 0:
                print(f"Population {i}, fitness function: {self.fitness_function(population[0], self.G)}")

                from collections import Counter
                print(f"lines with X stops: {Counter([len(p.lines) for p in population])}")

                # save the best <new one> one to file
                show_graph(self.G, population[0], i, show=report_show)