import unittest
import random

import numpy as np

from graph_generation import generate_city_graph
from line_generation import gen_random_line
from new_generation.Mutators import LineMutator


class LineTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LineTest, self).__init__(*args, **kwargs)
        np.random.seed(0)
        random.seed(0)

        self.G, self.best_paths = generate_city_graph(8)
        self.line_mutator = LineMutator(self.best_paths)

    def test_line_rotation_to_right(self):
        l1 = gen_random_line(self.G, self.best_paths)
        l2 = self.line_mutator.rotation_to_right(l1, 1)

        self.assertListEqual([l1.stops[-1]] + l1.stops[:-1], l2.stops)
