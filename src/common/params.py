from dataclasses import dataclass
from typing import Callable

GRAPH_SEED = 46
SEED = 2137
N = 30
N_IN_POPULATION = 200
POINTS_MULTIPLIER = 1


@dataclass
class SimulationParams:
    """
    Hyperparameters of fitness function

    :param R - hyperparamter of diminishing returns function.
    The function converges to e^R, as n->infinity

    :param alpha - cost of stopping on a bus stop

    :param beta - unit cost of a line

    :param K - line length scaling function

    :param delta - cost of empty bus stop
    """

    R: float
    alpha: float
    beta: float

    K: Callable[[float], float]

    delta: float
    osmnx: bool

    def with_osmnx(self):
        self.osmnx = True
        return self

    def no_osmnx(self):
        self.osmnx = False
        return self

    def with_quadrature_scaling(self, expected=10, top=20000, cutoff=5):
        """
        :param expected - line length for maximal fitness
        :param top - fitness for line of expected length
        :param cutoff - how fast fitness diminishes
        """
        K = lambda S: top - cutoff * (S - expected) ** 2
        return self


default_params = SimulationParams(
    R=2, alpha=0.05, beta=0.6, K=lambda S: S, delta=0.7, osmnx=False  # identity
)

# DEBUG = True
DEBUG = False


# debug print
def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)
