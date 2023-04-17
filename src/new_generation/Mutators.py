from copy import deepcopy

from networkx import Graph
import numpy as np
from Genotype import Genotype
from Line import Line
from src import line_generation
import new_generation.generation_util as generation_util


class LineMutator:
    def __init__(self, best_paths) -> None:
        self.best_paths = best_paths

    def rotation_to_right(self, line: Line) -> Line:
        start, end = generation_util.get_sublist_borders(len(line.stops))

        idxs = []
        i = start
        while i != end:
            idxs.append(i)
            i = (i + 1) % len(line.stops)
        idxs.append(i)

        shift = np.random.randint(len(idxs))

        new_stops = generation_util.shift_by_idxs(line.stops, idxs, shift)

        return Line(new_stops, self.best_paths)

    def cycle_rotation(self, line: Line) -> Line:
        idxs = generation_util.create_index_cycle(
            list(range(len(line.stops))), np.random.randint(0, len(line.stops) // 2 + 1)
        )

        new_stops = generation_util.shift_by_idxs(line.stops, list(idxs), 1)

        return Line(new_stops, self.best_paths)

    def invert(self, line: Line) -> Line:
        start, end = generation_util.get_sublist_borders(len(line.stops))

        if start <= end:
            new_stops = (
                line.stops[:start]
                + line.stops[end : start - 1 : -1]
                + line.stops[end + 1 :]
            )
        else:
            new_stops = []
            taken_range = line.stops[start:] + line.stops[: end + 1]
            inversed_range = list(reversed(taken_range))

            no_of_elems_to_take_first = len(line.stops) - start
            new_stops = (
                inversed_range[no_of_elems_to_take_first:]
                + line.stops[end + 1 : start]
                + inversed_range[:no_of_elems_to_take_first]
            )

        return Line(new_stops, self.best_paths)

    def erase_stops(self, line: Line, no_of_stops_to_erase: int = 1) -> Line:
        idx = np.random.choice(len(line.stops) - no_of_stops_to_erase, replace=False)
        new_stops = np.array(line.stops)[idx]
        return Line(new_stops, self.best_paths)


class GenotypeMutator:
    def __init__(self, graph: Graph, best_paths) -> None:
        self.best_paths = best_paths
        self.graph = graph

    def erase_line(self, genotype: Genotype) -> Genotype:
        new_genotype = deepcopy(genotype)
        i = np.random.randint(genotype.no_of_lines)
        del new_genotype.lines[i]

        return new_genotype

    def create_line(self, genotype: Genotype) -> Genotype:
        new_line = line_generation.gen_random_line(self.graph, self.best_paths)

        return Genotype(genotype.lines + [new_line])

    def split_line(
        self, genotype: Genotype, duplicate_split_point: bool = True
    ) -> Genotype:
        line_idx = np.random.randint(genotype.no_of_lines)
        line = genotype.lines[line_idx]

        s = 1 if duplicate_split_point else 2
        e = len(line.stops) - 2
        if e < s:
            return genotype
        stop_idx = np.random.randint(s, e + 1)

        new_line1 = Line(
            line.stops[: stop_idx + (1 if duplicate_split_point else 0)],
            self.best_paths,
        )
        new_line2 = Line(line.stops[stop_idx:], self.best_paths)

        new_genotype = deepcopy(genotype)
        del new_genotype.lines[line_idx]
        new_genotype.lines.extend([new_line1, new_line2])

        return new_genotype

    def merge_lines(
        self, genotype: Genotype, no_of_lines_to_merge: int = 2, mix_stops: bool = False
    ) -> Genotype:
        line_ids_to_mix = np.random.choice(
            genotype.no_of_lines, size=no_of_lines_to_merge, replace=False
        )

        idxs = {line_id: 0 for line_id in line_ids_to_mix}
        new_lines = [line for i, line in enumerate(genotype.lines) if i not in idxs]
        new_stops = []
        while len(idxs) > 0:
            line_id = np.random.choice(list(idxs.keys()))
            while True:
                new_stops.append(genotype.lines[line_id].stops[idxs[line_id]])
                idxs[line_id] += 1

                if idxs[line_id] >= len(genotype.lines[line_id].stops):
                    del idxs[line_id]
                    break
                if mix_stops:
                    break

        new_lines.append(Line(new_stops, self.best_paths))

        return Genotype(new_lines)

    def cycle_stops_shift(self, genotype: Genotype) -> Genotype:
        stops = generation_util.LineListLinearizer(genotype.lines)
        idxs = generation_util.create_index_cycle(
            list(range(len(stops))), np.random.randint(0, len(stops) // 2 + 1)
        )

        new_stops = generation_util.shift_by_idxs(stops, list(idxs), 1)
        new_lines = [Line(stops, self.best_paths) for stops in new_stops.stops()]

        return Genotype(new_lines)


if __name__ == "__main__":

    def main():
        # advanced unit tests
        line_mutator = LineMutator([[]])

        class LineMock(Line):
            def __init__(self, stops: list[int]):
                self.stops = stops

        line = LineMock([0, 1, 2, 3, 4, 5, 6])
        print(line.stops)
        # print(line_mutator.rotation_to_right(line).stops)
        print(line_mutator.invert(line).stops)

    main()
