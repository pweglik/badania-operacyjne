import random as rd
import numpy as np
from common.Genotype import Genotype

import generation_util
from common.Line import Line


class GenotypeCrosser:
    def __init__(self, best_paths) -> None:
        self.best_paths = best_paths

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
