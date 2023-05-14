# import from dirs below
import itertools
import os
import random
from multiprocessing import Process, Queue
from time import perf_counter
from typing import Tuple

from typing import IO

from new_generation.Sanitizers import BasicSanitizer
from SimultionEngine import SimulationEngine
from common.params import N, SEED
from common.params import N_IN_POPULATION
from fitness import fitness
from graph_generation import generate_city_graph
from initial_population import create_initial_population
from new_generation.Mutators import LineMutator, GenotypeMutator
from new_generation.SpecimenCrossers import GenotypeCrosser
from new_generation.new_generation_function import (
    new_generation_random,
    NewGenerationRandomParams,
)
from survival import n_best_survive, n_best_and_m_random_survive
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
)

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


def save_headers(f: IO[str], params_keys: list[str]):
    for key in params_keys:
        f.write(key + ",")
    f.write("fitness")
    f.write("\n")


def save_results(
    f: IO[str], params_keys: list[str], params_values: dict, fitness: float
):
    for key in params_keys:
        f.write(str(params_values[key]) + ",")
    f.write(str(fitness))
    f.write("\n")


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

        all_stops = list(G.nodes)

        line_mutator = LineMutator(G, all_stops, best_paths)
        genotype_mutator = GenotypeMutator(G, best_paths)
        genotype_crosser = GenotypeCrosser(G, best_paths)
        sanitizer = BasicSanitizer(best_paths)
        new_generation_params = NewGenerationRandomParams(
            params["chance_create_line"],
            params["chance_cycle"],
            params["chance_erase_line"],
            params["chance_invert"],
            params["chance_merge"],
            params["chance_merge_specimen"],
            params["chance_rot_cycle"],
            params["chance_rot_right"],
            params["chance_split"],
        )

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
                    sanitizer,
                    new_generation_params,
                ),
                population_sanitizer=sanitizer,
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

        # (0 to 10) / 10 = 0.0 to 1.0
        use_reduced = True
        zero_to_one: list[float] = [x / 10 for x in range(11)]
        zero_to_one_reduced: list[float] = [0.2, 0.5, 0.8]

        float_param_list: list[float] = (
            zero_to_one_reduced if use_reduced else zero_to_one
        )

        grid_search_params = {
            "survival_functions": range(len(SURVIVAL_FUNCTIONS)),
            "epochs": [100],
            "chance_create_line": float_param_list,
            "chance_cycle": float_param_list,
            "chance_erase_line": float_param_list,
            "chance_invert": float_param_list,
            "chance_merge": float_param_list,
            "chance_merge_specimen": float_param_list,
            "chance_rot_cycle": float_param_list,
            "chance_rot_right": float_param_list,
            "chance_split": float_param_list,
        }

        # Setup of the grid search
        parallel_units = 1
        cpu_count = os.cpu_count()
        if cpu_count is not None:
            parallel_units = cpu_count - 1

        print("Parallel units:", parallel_units)

        # fixed order list
        # order of keys in params_keys define column order in csv file
        # must stay the same for all processes
        params_keys = list(grid_search_params.keys())
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

        # open results file and save headers
        f = open("results/gridsearch.csv", "w")
        save_headers(f, params_keys)

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

        results_list.sort(key=lambda x: x[1])

        print(f"Best parameters: \t{results_list[0][0]}")
        print(f"Best fitness: \t{results_list[0][1]:.2f}")

        print("Best survival function:")
        print(SURVIVAL_FUNCTIONS[results_list[0][0]["survival_functions"]][0])

        print(f"Best epochs: \t{results_list[0][0]['epochs']}")

        for params_values, fitness in results_list:
            save_results(f, params_keys, params_values, fitness)

        f.close()

    main()
