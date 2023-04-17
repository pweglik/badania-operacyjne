from collections import Counter
from copy import deepcopy
from typing import Callable, Optional
import networkx as nx
from Genotype import Genotype
from show_graph import show_graph
from params import dprint


class SimulationEngine:
    def __init__(
        self,
        G: nx.Graph,
        initial_population: list[Genotype],
        fitness_function: Callable[[Genotype, nx.Graph], float],
        survival_function: Callable[
            [list[tuple[Genotype, float]]], list[tuple[Genotype, float]]
        ],
        new_generation_function: Callable[
            [list[tuple[Genotype, float]], nx.Graph], list[Genotype]
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
        self.latest_generation: Optional[list[Genotype]] = None

    def report(self, i: int, population: list[Genotype], report_show: bool = False):
        print(
            f"Population {i:5}, "
            f"best fitness function: {self.fitness_function(population[0], self.G):20.6f}, "
            f"best lines stops count: {population[0].get_line_stops_count_summary()}"
        )

        # save the best <new one> one to file
        show_graph(self.G, population[0], i, show=report_show)

    def purge_empty(self, population: list[Genotype]) -> list[Genotype]:
        """
        Removes empty lines from all genotypes and then removes empty genotypes (with no lines)
        :param population: population (potentially flawed)
        :return: Valid population with no empty genotypes/lines without stops
        """
        new_population = []

        for genotype in population:
            genotype = deepcopy(genotype)

            # non-empty lines
            genotype.lines = list(
                filter(lambda line: len(line.stops) > 0, genotype.lines)
            )

            # non-empty genotype
            if len(genotype.lines) > 0:
                new_population.append(genotype)

        return new_population

    def run(
        self,
        no_of_generations: int = 100,
        report_every_n: int = 10,
        report_show: bool = False,
    ):
        """

        :param no_of_generations: run for X generation
        :param report_every_n: every N, draw or save graph as picture
        :param report_show: if <True> run plt.show(), otherwise plt.savefig(...)
        """
        population: list[Genotype] = self.initial_population

        self.report(0, population, report_show)

        for i in range(no_of_generations):
            dprint(
                f"1 lines with X stops: {Counter([len(p.lines) for p in population])}"
            )
            population = self.purge_empty(population)
            dprint(
                f"2 lines with X stops: {Counter([len(p.lines) for p in population])}"
            )

            # calculating fitness for all organisms
            population_with_fitness: list[tuple[Genotype, float]] = [
                (organism, self.fitness_function(organism, self.G))
                for organism in population
            ]

            # applying survival function
            population_survived: list[tuple[Genotype, float]] = self.survival_function(
                population_with_fitness
            )
            self.latest_generation = population

            # print(
            #     "population_survived fitness", [item[1] for item in population_survived]
            # )

            dprint(
                f"3 lines with X stops: {Counter([len(p[0].lines) for p in population_survived])}"
            )

            # generating new population from survived
            population = self.new_generation_function(population_survived, self.G)

            # print(
            #     "new_generation fitness     ",
            #     [self.fitness_function(item, self.G) for item in population],
            # )
            # print()

            dprint(
                f"4 lines with X stops: {Counter([len(p.lines) for p in population])}\n\n"
            )

            if (i + 1) % report_every_n == 0:
                self.report(i + 1, population, report_show)
