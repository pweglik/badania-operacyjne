GRAPH_SEED = 46
SEED = 2137
N = 30
N_IN_POPULATION = 200
POINTS_MULTIPLIER = 1

"""
Hyperparameters of fitness function

R - hyperparamter of diminishing returns function.
The function converges to e^R, as n->infinity

alpha - cost of stopping on a bus stop

beta - unit cost of a line

delta - cost of empty bus stop
"""
R = 2
alpha = 0.05
beta = 0.6
delta = 0.7


# DEBUG = True
DEBUG = False


# debug print
def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


# if using OSMNX this needs to be true
# I know, kinda sketchy, TODO handle better
OSMNX = True
