import random
from copy import deepcopy
from typing import Optional

from networkx import Graph
import numpy as np
import networkx as nx

from new_generation.Sanitizers import Sanitizer
from src.utils import exp_pdf_for_range
from src.common.Genotype import Genotype
from src.common.Line import Line
from src.common import line_generation
from src.new_generation import generation_util


class LineMutator:
    def __init__(self, G: Graph, all_stops: list[int], best_paths) -> None:
        self.G = G
        self.best_paths = best_paths
        self.all_stops = all_stops
        self.distances = dict(nx.all_pairs_shortest_path_length(self.G))
        self.sorted_distances = {
            stop: sorted(self.distances[stop].items(), key=lambda x: x[1])
            for stop in all_stops
        }

    def rotation_to_right(
        self,
        line: Line,
        shift: Optional[int] = None,
        list_lenght_from_normal_distribution: bool = False,
    ) -> Line:
        start, end = generation_util.get_sublist_borders(
            len(line.stops), use_normal=list_lenght_from_normal_distribution
        )

        idxs = []
        i = start
        while i != end:
            idxs.append(i)
            i = (i + 1) % len(line.stops)
        idxs.append(i)

        if shift is None:
            shift = np.random.randint(len(idxs))

        new_stops = generation_util.shift_by_idxs(line.stops, idxs, shift)

        return Line(new_stops, self.best_paths)

    def cycle_rotation(self, line: Line) -> Line:
        idxs = generation_util.create_index_cycle(
            list(range(len(line.stops))), np.random.randint(0, len(line.stops) // 2 + 1)
        )

        new_stops = generation_util.shift_by_idxs(line.stops, list(idxs), 1)

        return Line(new_stops, self.best_paths)

    def invert(
        self, line: Line, list_length_from_normal_distribution: bool = False
    ) -> Line:
        start, end = generation_util.get_sublist_borders(
            len(line.stops), use_normal=list_length_from_normal_distribution
        )

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
        no_of_stops_to_erase = min(no_of_stops_to_erase, line.stops_no)
        idx = np.random.choice(
            len(line.stops) - no_of_stops_to_erase, replace=False, size=1
        )
        new_stops = np.array(line.stops)[idx]
        return Line(new_stops, self.best_paths)

    def add_stops(self, line: Line, no: int = 1, mix: bool = False) -> Line:
        used_stops_set = set(line.stops)
        not_used_stops = list(self.G.nodes.keys() - used_stops_set)
        stops_to_add = list(np.random.choice(not_used_stops, size=no, replace=False))

        if not mix:
            return Line(line.stops + stops_to_add, self.best_paths)

        current_stops = list(used_stops_set)
        idxs = np.random.choice(
            [0] * len(current_stops) + [1] * no, len(current_stops) + no, replace=False
        )
        i = [0, 0]
        stops = [current_stops, not_used_stops]
        new_stops = []
        for stops_i in idxs:
            stop = stops[stops_i][i[stops_i]]
            new_stops.append(stop)
            i[stops_i] += 1

        return Line(new_stops, self.best_paths)

    def replace_stops(
        self,
        line: Line,
        lambda_param: float = 0.2,
        no_to_replace: int = 1,
        proximity_based: bool = True,
    ) -> Line:
        stops = np.array(line.stops, dtype=int)
        stops_to_replace_idxs = np.random.choice(
            line.stops_no, size=no_to_replace, replace=False
        )

        if not proximity_based:
            stops[stops_to_replace_idxs] = np.random.choice(
                self.all_stops, no_to_replace, replace=False
            )
            return Line(list(stops), self.best_paths)

        stops_to_replace = stops[stops_to_replace_idxs]
        choosen_neighbours = [
            np.random.choice(
                [
                    s for s, _ in self.sorted_distances[stop]
                ],  # take stop from tuple[stop, distance]
                replace=False,
                p=exp_pdf_for_range(
                    # take distance from tuple[stop, distance]
                    neighbours := np.array([d for _, d in self.sorted_distances[stop]]),
                    neighbours.size,
                    lambda_param,
                ),
            )
            for stop in stops_to_replace
        ]
        stops[stops_to_replace_idxs] = choosen_neighbours

        return Line(list(stops), self.best_paths)

    @staticmethod
    def mutate_one_line_out_of_organism(
        organism: Genotype, sanitizer: Sanitizer, mutator_function, *args, **kwargs
    ):
        original_line = random.sample(organism.lines, 1)[0]
        new_line = mutator_function(original_line, *args, **kwargs)
        new_line = sanitizer.sanitizeLine(new_line)
        if new_line is not None:
            # line is ok
            organism = Genotype(organism.lines.copy())
            organism.lines.remove(original_line)
            organism.lines.append(new_line)
        else:
            # line not ok
            # leave original line in place
            pass

        return organism


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
        new_stops_set: set[int] = set()
        while len(idxs) > 0:
            line_id = np.random.choice(list(idxs.keys()))
            while True:
                stop = genotype.lines[line_id].stops[idxs[line_id]]
                if stop not in new_stops_set:
                    new_stops.append(stop)
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
