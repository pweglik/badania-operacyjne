from collections import Counter
from copy import deepcopy
from typing import Callable, List, Tuple
import networkx as nx
from Genotype import Genotype
from show_graph import show_graph
from src.params import dprint


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

    def report(self, i: int, population: List[Genotype], report_show: bool = False):
        print(f"Population {i}, fitness function: {self.fitness_function(population[0], self.G)}")

        from collections import Counter
        print(f"lines with X stops: {Counter([len(p.lines) for p in population])}")

        # save the best <new one> one to file
        show_graph(self.G, population[0], i, show=report_show)

    def purge_empty(self, population: List[Genotype]) -> List[Genotype]:
        """
        Removes empty lines from all genotypes and then removes empty genotypes (with no lines)
        :param population: population (potentially flawed)
        :return: Valid population with no empty genotypes/lines without stops
        """
        new_population = []

        for genotype in population:

            genotype = deepcopy(genotype)

            # non-empty lines
            genotype.lines = list(filter(lambda line: len(line.stops) > 0, genotype.lines))

            # non-empty genotype
            if len(genotype.lines) > 0:
                new_population.append(genotype)

        return new_population


    def run(self, no_of_generations: int = 100, report_every_n: int = 10, report_show: bool = False):
        """

        :param no_of_generations: run for X generation
        :param report_every_n: every N, draw or save graph as picture
        :param report_show: if <True> run plt.show(), otherwise plt.savefig(...)
        """
        population: List[Genotype] = self.initial_population

        self.report(0, population, report_show)

        for i in range(no_of_generations + 1):
            dprint(f"1 lines with X stops: {Counter([len(p.lines) for p in population])}")
            population = self.purge_empty(population)
            dprint(f"2 lines with X stops: {Counter([len(p.lines) for p in population])}")

            # calculating fitness for all organisms
            population_with_fitness: List[Tuple[Genotype, float]] = [
                (organism, self.fitness_function(organism, self.G))
                for organism in population
            ]

            # applying survival function
            population_survived: List[Tuple[Genotype, float]] = self.survival_function(
                population_with_fitness
            )

            dprint(f"3 lines with X stops: {Counter([len(p[0].lines) for p in population_survived])}")

            # generating new population from survived
            population = self.new_generation_function(population_survived, self.G)

            dprint(f"4 lines with X stops: {Counter([len(p.lines) for p in population])}\n\n")

            if (i+1) % report_every_n == 0:
                self.report(i+1, population, report_show)