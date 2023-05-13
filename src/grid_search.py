# import from dirs below
import sys

sys.path.insert(0, ".")
sys.path.insert(0, ".")
sys.path.insert(0, "./new_generation")

import itertools
import os
from concurrent.futures import ThreadPoolExecutor
import random

from common.params import N, SEED

from graph_generation import generate_city_graph

from new_generation.Mutators import LineMutator, GenotypeMutator
from new_generation.SpecimenCrossers import GenotypeCrosser

from SimultionEngine import SimulationEngine
from common.params import N_IN_POPULATION
from fitness import fitness
from initial_population import create_initial_population
from new_generation.new_generation_function import new_generation_random
from survival import n_best_survive

random.seed(SEED)


def custom_grid_search(GridSearchParams, cv=5, parallel_units=1, **model_params):
    def process_param_set(args):
        (params,) = args

        G = model_params["G"]
        best_paths = model_params["best_paths"]
        line_mutator = model_params["line_mutator"]
        genotype_mutator = model_params["genotype_mutator"]
        genotype_crosser = model_params["genotype_crosser"]

        sim_engine = SimulationEngine(
            G,
            initial_population=create_initial_population(G, best_paths),
            fitness_function=fitness,
            survival_function=lambda population: n_best_survive(
                population, N_IN_POPULATION // params["survival_rate"]
            ),
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

        return params, best_fitness

    # Initialize variables to store the results
    results = []
    Keys = GridSearchParams.keys()
    max_score = -sys.maxsize
    best_params = {}
    ParamSets = [
        dict(zip(Keys, values))
        for values in itertools.product(*GridSearchParams.values())
    ]

    # Check the number of parallel units
    if parallel_units == -1:
        parallel_units = os.cpu_count()
    elif parallel_units > os.cpu_count():
        raise RuntimeError(f"Maksimum CPU: {os.cpu_count()}")

    print("Parallel Units:", parallel_units)

    # Start the thread pool executor
    try:
        with ThreadPoolExecutor(max_workers=parallel_units) as executor:
            for params in ParamSets:
                total_score = 0
                futures = []

                print("started", params)

                for _ in range(cv):
                    future = executor.submit(process_param_set, (params,))
                    futures.append(future)

                for future in futures:
                    _, error = future.result()
                    total_score += error

                avg_error = total_score / cv

                print("finished", params, "average result", avg_error)

                results.append((params, avg_error))
                print("avg_error", avg_error, "max_score", max_score)
                if avg_error > max_score:
                    max_score = avg_error
                    best_params = params

    except KeyboardInterrupt:
        print("Stopping...")
        executor.shutdown(wait=False)

    return results, best_params, max_score


if __name__ == "__main__":
    # Parameters
    grid_search_params = {
        "survival_rate": range(1, 2, 1),
        "epochs": [10],
    }

    G, best_paths = generate_city_graph(N)
    #
    line_mutator = LineMutator(G, best_paths)
    genotype_mutator = GenotypeMutator(G, best_paths)
    genotype_crosser = GenotypeCrosser(best_paths)

    # Searching Best Parameters
    results, best_params, error = custom_grid_search(
        grid_search_params,
        cv=5,
        parallel_units=-1,
        G=G,
        best_paths=best_paths,
        line_mutator=line_mutator,
        genotype_mutator=genotype_mutator,
        genotype_crosser=genotype_crosser,
    )

    # Print results
    print("Results:")
    for res in results:
        print(res)

    print("Best Parameters:", best_params)
    print("Error:", error)
