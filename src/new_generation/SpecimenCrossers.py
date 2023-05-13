import itertools
import random as rd
import networkx as nx
from networkx import Graph
import numpy as np
from common.Genotype import Genotype

from src.new_generation import generation_util
from src.common.Line import Line


class GenotypeCrosser:
    def __init__(self, G: Graph, best_paths) -> None:
        self.G = G
        self.best_paths = best_paths
        self.distances = dict(nx.all_pairs_shortest_path_length(self.G))

    def merge_genotypes(self, genotype1: Genotype, genotype2: Genotype) -> Genotype:
        lines1 = rd.choices(genotype1.lines, k=rd.randint(0, len(genotype1.lines)))
        lines2 = rd.choices(genotype2.lines, k=rd.randint(0, len(genotype2.lines)))

        return Genotype(lines1 + lines2)

    def cycle_stops_shift(self, genotype1: Genotype, genotype2: Genotype) -> Genotype:
        genotype = self.merge_genotypes(genotype1, genotype2)

        stops = generation_util.LineListLinearizer(genotype.lines)
        idxs = generation_util.create_index_cycle(
            list(range(len(stops))), np.random.randint(0, len(stops) // 2 + 1)
        )

        new_stops = generation_util.shift_by_idxs(stops, list(idxs), 1)
        new_lines = [Line(stops, self.best_paths) for stops in new_stops.stops()]

        return Genotype(new_lines)

    def line_based_merge(self, genotype1: Genotype, genotype2: Genotype) -> Genotype:
        """
        It takes genotypes G1 and G2 and returns genotype G such that
        every its line is a result of concatenation of half of L1-1 with half of L2-1.

        L1-n is nth line from G1
        L2-n is nth line from G2
        If genotypes have different number of lines then the shorter one is repeated.

        """
        less_lines = min([genotype1.lines, genotype2.lines], key=len)
        more_lines = max([genotype1.lines, genotype2.lines], key=len)

        new_lines = []
        for line1, line2 in zip(itertools.cycle(less_lines), more_lines):
            used_stops1 = np.random.choice(
                line1.stops, size=line1.stops_no // 2, replace=False
            )
            used_stops2 = np.random.choice(
                line2.stops, size=line2.stops_no // 2, replace=False
            )

            # assumes distances between ends of used stops are bidirectional
            possibilities = [
                (
                    self.distances[used_stops1[-1]][used_stops2[0]],
                    used_stops1,
                    used_stops2,
                ),
                (
                    self.distances[used_stops1[-1]][used_stops2[-1]],
                    used_stops1,
                    reversed(used_stops2),
                ),
                (
                    self.distances[used_stops1[0]][used_stops2[0]],
                    reversed(used_stops1),
                    used_stops2,
                ),
                (
                    self.distances[used_stops1[0]][used_stops2[-1]],
                    used_stops2,
                    used_stops1,
                ),
            ]

            _, first_part, second_part = min(possibilities)

            new_lines.append(
                Line(list(np.concatenate(first_part, second_part)), self.best_paths)
            )

        return Genotype(new_lines)
