import random


from fitness import fitness
from initial_population import create_initial_population
from networkx import Graph
from new_generation.new_generation_function import new_generation_random

from graph_generation import generate_city_graph
from SimultionEngine import SimulationEngine
from new_generation.Mutators import GenotypeMutator, LineMutator
from new_generation.SpecimenCrossers import GenotypeCrosser
from common.params import N_IN_POPULATION, SEED, N
from new_generation_function import NewGenerationRandomParams
from src.new_generation.Sanitizers import BasicSanitizer
from survival import n_best_survive
from src.common.params import (
    CHANCE_CREATE_LINE,
    CHANCE_CYCLE,
    CHANCE_ERASE_LINE,
    CHANCE_INVERT,
    CHANCE_MERGE,
    CHANCE_MERGE_SPECIMEN,
    CHANCE_ROT_CYCLE,
    CHANCE_ROT_RIGHT,
    CHANCE_SPLIT,
    dprint,
)


def run_simulation(
    G: Graph,
    all_stops: list[int],
    best_paths,
    no_of_generations: int,
    report_every_n: int,
    report_show: bool,
):
    line_mutator = LineMutator(G, all_stops, best_paths)
    genotype_mutator = GenotypeMutator(G, best_paths)
    genotype_crosser = GenotypeCrosser(G, best_paths)
    sanitizer = BasicSanitizer(best_paths)
    params = NewGenerationRandomParams(
        CHANCE_CREATE_LINE,
        CHANCE_CYCLE,
        CHANCE_ERASE_LINE,
        CHANCE_INVERT,
        CHANCE_MERGE,
        CHANCE_MERGE_SPECIMEN,
        CHANCE_ROT_CYCLE,
        CHANCE_ROT_RIGHT,
        CHANCE_SPLIT,
    )

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
            sanitizer,
            params,
        ),
        population_sanitizer=BasicSanitizer(best_paths),
    )

    sim_engine.run(no_of_generations, report_every_n, report_show=report_show)


if __name__ == "__main__":
    random.seed(SEED)

    G, best_paths = generate_city_graph(N)
    all_stops = list(G.nodes)

    run_simulation(G, all_stops, best_paths, 10, 1, False)
