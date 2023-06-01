import random
import time

import numpy as np

from fitness import fitness
from initial_population import create_initial_population
from networkx import Graph
from new_generation.new_generation_function import (
    new_generation_random,
    NewGenerationRandomParams,
)

from graph_generation import generate_city_graph, load_cracow_city_graph
from SimultionEngine import SimulationEngine
from new_generation.Mutators import GenotypeMutator, LineMutator
from new_generation.SpecimenCrossers import GenotypeCrosser
from common.params import N_IN_POPULATION, SEED, N, SimulationParams, default_params
from new_generation.Sanitizers import BasicSanitizer
from survival import n_best_survive


def run_simulation(
    G: Graph,
    all_stops: list[int],
    best_paths,
    no_of_generations: int,
    report_every_n: int,
    report_show: bool,
    simulation_params: SimulationParams = default_params,
) -> None:
    """
    Run simulation with given parameters
    :param G: Graph representing the city
    :param all_stops: All stops in the city (vertices of the graph)
    :param best_paths: Shortest paths between all stops
    :param no_of_generations: Number of generations to simulate
    :param report_every_n: Report every n-th generation
    :param report_show: if <True> run plt.show(), otherwise plt.savefig(...)
    :param simulation_params: optional parameter to set simulation params
    """
    line_mutator = LineMutator(G, all_stops, best_paths)
    genotype_mutator = GenotypeMutator(G, best_paths)
    genotype_crosser = GenotypeCrosser(G, best_paths)
    sanitizer = BasicSanitizer(best_paths)
    params = NewGenerationRandomParams(
        chance_create_line=0.1,
        chance_cycle=0.1,
        chance_erase_line=0.1,
        chance_invert=0.5,
        chance_merge=0.25,
        chance_merge_specimen=0.5,
        chance_rot_cycle=0.5,
        chance_rot_right=0.5,
        chance_split=0.75,
        chance_erase_stop=0.1,
        chance_add_stop=0.3,
        chance_add_stop_mix=0.1,
        chance_replace_stops=0.1,
        chance_replace_stops_proximity=0.1,
        chance_merge_mix=0.5,  # brak wplywu
        cycle_stops_shift=0.5,  # brak wplywu
        chance_cycle_stops_shift=0.1,
        chance_line_based_merge=0.1,
    )

    sim_engine = SimulationEngine(
        G,
        initial_population=create_initial_population(G, best_paths),
        fitness_function=fitness,
        survival_function=lambda population: n_best_survive(
            population, N_IN_POPULATION // 8  # deemed best by grid search
        ),
        new_generation_function=lambda population, graph: new_generation_random(
            population,
            N_IN_POPULATION,
            line_mutator,
            genotype_mutator,
            genotype_crosser,
            sanitizer,
            params,
        ),
        population_sanitizer=BasicSanitizer(best_paths),
        simulation_params=simulation_params,
    )

    sim_engine.run(no_of_generations, report_every_n, report_show=report_show)


def main_random():
    random.seed(SEED)

    G, best_paths = generate_city_graph(N)
    all_stops = list(G.nodes)

    start = time.time()
    run_simulation(G, all_stops, best_paths, 100, 1, False, default_params.no_osmnx())
    end = time.time()

    print(f"took {end - start:6.4f}s")


def main_cracow():
    G, best_paths = load_cracow_city_graph()
    all_stops = list(G.nodes)

    start = time.time()
    run_simulation(
        G,
        all_stops,
        best_paths,
        100,
        1,
        False,
        default_params.with_osmnx().with_quadrature_scaling(),
    )
    end = time.time()

    print(f"took {end - start:6.4f}s")


if __name__ == "__main__":
    print("available simulations:")
    print("\t[0] Random city")
    print("\t[1] Cracow city")
    choice = input("your choice: ")

    if choice == "0":
        print("running on random city")
        main_random()

    elif choice == "1":
        print("running on cracow city")
        main_cracow()

    else:
        print("wrong input")
