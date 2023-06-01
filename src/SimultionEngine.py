from typing import Callable, Optional
import networkx as nx
from common.Genotype import Genotype
from common.show_graph import show_graph, show_graph_osmnx
from common.params import dprint, SimulationParams
from new_generation.Sanitizers import Sanitizer


class SimulationEngine:
    def __init__(
        self,
        G: nx.Graph,
        initial_population: list[Genotype],
        fitness_function: Callable[[Genotype, nx.Graph, SimulationParams], float],
        survival_function: Callable[
            [list[tuple[Genotype, float]]], list[tuple[Genotype, float]]
        ],
        new_generation_function: Callable[
            [list[tuple[Genotype, float]], nx.Graph], list[Genotype]
        ],
        population_sanitizer: Sanitizer,
        simulation_params: SimulationParams,
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
        self.population_sanitizer = population_sanitizer
        self.simulation_params = simulation_params

    def report(self, i: int, population: list[Genotype], report_show: bool = False):
        line_lengths = [len(line.stops) for line in population[0].lines]

        print(
            f"Epoch:                   {i:20}\n"
            f"best fitness function:   {self.fitness_function(population[0], self.G, self.simulation_params):20.6f}\n"
            # f"best lines stops count:  {population[0].get_line_stops_count_summary():20}\n"
            f"no of lines:             {len(population[0].lines):20}\n"
            f"longest line:            {max(line_lengths):20}\n"
            f"shortest line:           {min(line_lengths):20}\n"
        )

        # save the best <new one> one to file
        if not self.simulation_params.osmnx:
            show_graph(self.G, population[0], i, show=report_show)
        else:
            show_graph_osmnx(self.G, population[0], i, show=report_show)

    def sanitize_population(self, population: list[Genotype]) -> list[Genotype]:
        """
        Performs sanitization of the given population according to the self.population_sanitizer
        :param population: population (potentially flawed)
        :return: Valid population with no empty genotypes/lines without stops
        """
        return [
            genotype
            for genotype in map(self.population_sanitizer.sanitizeGenotype, population)
            if genotype is not None
        ]

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

        if report_every_n != 0:
            self.report(0, population, report_show)

        fitness_values = []

        for i in range(no_of_generations):
            population = self.sanitize_population(population)

            # calculating fitness for all organisms
            population_with_fitness: list[tuple[Genotype, float]] = [
                (
                    organism,
                    self.fitness_function(organism, self.G, self.simulation_params),
                )
                for organism in population
            ]

            # applying survival function
            population_survived: list[tuple[Genotype, float]] = self.survival_function(
                population_with_fitness
            )
            self.latest_generation = population
            fitness_values.append(
                self.fitness_function(
                    self.latest_generation[0], self.G, self.simulation_params
                )
            )

            # generating new population from survived
            population = self.new_generation_function(population_survived, self.G)

            if report_every_n != 0 and (i + 1) % report_every_n == 0:
                self.report(i + 1, self.latest_generation, report_show)

        return fitness_values
