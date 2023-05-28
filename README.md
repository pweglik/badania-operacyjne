# Genetic algorithms

## Description
Genetic algorithm solving public transportation problem. The goal is to find the best lines for public transportation.

---

## Setup
1. Make sure you have `Python 3.11` installed.
2. Install requirements
```
pip install -r requirements.txt
```
---
## Running the app
The app consist of several modules:
- `main.py` - main module for running the app,
- `grid_search.py` - grid search for looking for hyperparameters,
- `city_generation_test.ipynb` - notebook for testing Cracow city generation.

### Main module
#### Description
This module shows a short example of how to use our genetic algorithm. It provides us with `run_simulation` function,
which takes several parameters:
- `G: Graph` - graph representing the city,
- `all_stops: list[int]` - all stops in the city (vertices of the graph),
- `best_paths` - shortest paths between all stops
- `no_of_generations: int` - number of generations to simulate,
- `report_every_n: int` - report every n-th generation,
- `report_show: bool` - if `True` then the map image is displayed, otherwise it is saved to the file
#### Running the app
To run the app, run the following command in directory:
```
python main.py
```

### Grid search
#### Running the grid search
To run grid search, run the following command in `src` directory:
```
python src/grid_search.py
```

#### Setting the parameters

To set the parameters, edit the `grid_search.py` file. Look for variable named `grid_search_params` and edit it.
Remember, that the grid search will run all possible combinations of the parameters. It may take a while.

#### Setting number of parallel processes
To set the number of parallel processes, edit the `grid_search.py` file.
Look for variable named `parallel_units` and edit it.
By default, it is set to -1, which means that the number of parallel processes will be equal to
the number of cores on your machine minus 1.

#### Results
The results of the grid search will be saved in the `results/gridsearch.csv` file.


### Cracow city
#### Running the Cracow city generation
To run Cracow city generation, run the `city_generation_test.ipynb` file in Jupyter Notebook.

---

## Development setup
Install hooks
```
pre-commit install
```

Running hook against all files
```
pre-commit run --all-files
```

---

## Authors
TODO
