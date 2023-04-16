GRAPH_SEED = 46
SEED = 2137
N = 30
N_IN_POPULATION = 200


"""
Hyperparameters of fitness function

R - hyperparamter of diminishing returns function.
The function converges to e^R, as n->infinity

alpha - cost of stopping on a bu stop

beta - unit cost of a line
"""
R = 2
alpha = 2
beta = 10


# simulation params
CHANCE_MERGE_SPECIMEN = 0.9

CHANCE_ROT_RIGHT = 0.5
CHANCE_ROT_CYCLE = 0.5
CHANCE_INVERT = 0.5

CHANCE_ERASE_LINE = 0.01
CHANCE_CREATE_LINE = 0.9
CHANCE_SPLIT = 0.2
CHANCE_MERGE = 0.1
CHANCE_CYCLE = 0.5


# DEBUG = True
DEBUG = False
# debug print
def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)