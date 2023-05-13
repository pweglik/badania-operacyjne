# import from dirs below
import itertools
import os
import random
from multiprocessing import Process, Queue
from time import perf_counter
from typing import Tuple

from SimultionEngine import SimulationEngine
from common.params import N, SEED
from common.params import N_IN_POPULATION
from fitness import fitness
from graph_generation import generate_city_graph
from initial_population import create_initial_population
from new_generation.Mutators import LineMutator, GenotypeMutator
from new_generation.SpecimenCrossers import GenotypeCrosser
from new_generation.new_generation_function import new_generation_random
from survival import n_best_survive, n_best_and_m_random_survive

random.seed(SEED)

VERBOSE = True

SURVIVAL_FUNCTIONS = [
    (
        "(1/4)_best_survive",
        lambda population: n_best_survive(population, N_IN_POPULATION // 4),
    ),
    (
        "(1/8)_best_survive",
        lambda population: n_best_survive(population, N_IN_POPULATION // 8),
    ),
    (
        "(1/4)_best_and_(1/10)_random_survive",
        lambda population: n_best_and_m_random_survive(
            population, N_IN_POPULATION // 4, N_IN_POPULATION // 10
        ),
    ),
    (
        "(1/4)_best_and_(1/20)_random_survive",
        lambda population: n_best_and_m_random_survive(
            population, N_IN_POPULATION // 4, N_IN_POPULATION // 20
        ),
    ),
]


def process_params(tasks, results, G, best_paths, INITIAL_POPULATIONS):
    """
    Process params from tasks queue and put results in results queue
    :param tasks: Tasks to be processed
    :param results: Results of the tasks
    :param G: Our city
    :param best_paths: Best paths in our city
    """
    while not tasks.empty():
        params = tasks.get()

        if VERBOSE:
            print(os.getpid(), "Starting", params)

        survival_function = SURVIVAL_FUNCTIONS[params["survival_functions"]][1]

        line_mutator = LineMutator(G, best_paths)
        genotype_mutator = GenotypeMutator(G, best_paths)
        genotype_crosser = GenotypeCrosser(best_paths)

        fitness_sum = 0

        time_start = perf_counter()
        for initial_population in INITIAL_POPULATIONS:
            sim_engine = SimulationEngine(
                G,
                initial_population=initial_population,
                fitness_function=fitness,
                survival_function=survival_function,
                new_generation_function=lambda population, graph: new_generation_random(
                    population,
                    N_IN_POPULATION,
                    line_mutator,
                    genotype_mutator,
                    genotype_crosser,
                ),
            )
            fitness_values = sim_engine.run(params["epochs"], 0, report_show=False)
            best_fitness = fitness_values[-1]
            fitness_sum += best_fitness
        run_time = perf_counter() - time_start

        average_best_fitness = fitness_sum / len(INITIAL_POPULATIONS)

        if VERBOSE:
            print(
                os.getpid(), "Done", params, average_best_fitness, f"in {run_time:.2f}s"
            )
        results.put((params, average_best_fitness))

    print(f"Done {os.getpid()}")


if __name__ == "__main__":

    def main() -> None:
        # Setup of the city
        G, best_paths = generate_city_graph(N)

        # Parameters
        INITIAL_POPULATIONS = [
            create_initial_population(G, best_paths) for _ in range(3)
        ]

        grid_search_params = {
            "survival_functions": range(len(SURVIVAL_FUNCTIONS)),
            "epochs": [100],
        }

        # Setup of the grid search
        parallel_units = 1
        cpu_count = os.cpu_count()
        if cpu_count is not None:
            parallel_units = cpu_count - 1

        print("Parallel units:", parallel_units)

        params_keys = grid_search_params.keys()
        queue: "Queue[dict]" = Queue()
        results: "Queue[Tuple[dict, float]]" = Queue()

        for values in itertools.product(*grid_search_params.values()):
            queue.put(dict(zip(params_keys, values)))

        processes = [
            Process(
                target=process_params,
                args=(queue, results, G, best_paths, INITIAL_POPULATIONS),
            )
            for _ in range(parallel_units)
        ]

        # Start grid search
        for i in range(parallel_units):
            processes[i].start()

        # Wait for grid search to finish
        for p in processes:
            p.join()

        # Print results
        print("Results:")
        results_list = []
        while not results.empty():
            results_list.append(results.get())

        sorted(results_list, key=lambda x: x[1])

        print(f"Best parameters: \t{results_list[0][0]}")
        print(f"Best fitness: \t{results_list[0][1]:.2f}")

        print("Best survival function:")
        print(SURVIVAL_FUNCTIONS[results_list[0][0]["survival_functions"]][0])

        print(f"Best epochs: \t{results_list[0][0]['epochs']}")

    main()
