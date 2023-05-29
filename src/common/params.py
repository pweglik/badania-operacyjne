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

K - function for cost for line length

delta - cost of empty bus stop
"""
R = 2
alpha = 0.05
beta = 0.6

# gamma = 50
# 250: ({2: 17, 3: 11, 4: 8, 1: 6, 6: 6, 5: 5, 8: 5, 12: 2, 10: 2, 9: 2, 13: 1, 7: 1, 20: 1, 11: 1, 14: 1}) no of lines: 69
# 125: ({2: 26, 3: 15, 7: 8, 5: 6, 4: 5, 8: 5, 9: 4, 13: 4, 1: 3, 6: 3, 18: 2, 20: 2, 10: 2, 15: 2, 33: 1, 37: 1, 14: 1, 12: 1})no of lines: 91
# 50 : ({2: 9, 5: 6, 3: 5, 22: 5, 16: 4, 12: 3, 89: 3, 8: 3, 1: 3, 6: 3, 65: 2, 54: 2, 10: 2, 7: 2, 27: 2, 40: 2, 24: 2, 72: 2, 48: 2, 29: 2, 14: 2, 11: 1, 37: 1, 26: 1, 38: 1, 34: 1, 25: 1, 13: 1, 36: 1, 21: 1, 4: 1, 9: 1, 47: 1, 43: 1, 23: 1, 15: 1})no of lines: 81
# TODO more experiments


def K(S):
    expected = 10
    top = 20000
    cutoff = 5
    return top - cutoff * (S - expected) ** 2


# expected 10 top 20000 cutoff 5 population 100: long lines

delta = 0.7


# DEBUG = True
DEBUG = False


# debug print
def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)
