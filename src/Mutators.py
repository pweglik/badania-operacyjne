from copy import deepcopy
import random

from networkx import Graph
from src.Genotype import Genotype
from src.Line import Line
from src import line_generation


def get_sublist_borders(n: int) -> tuple[int, int]:
    return (random.randrange(n), random.randrange(n))


class LineMutator:
    def __init__(self, best_paths) -> None:
        self.best_paths = best_paths

    def rotation_to_right(self, line: Line) -> Line:
        start, end = get_sublist_borders(len(line.stops))

        idxs = []
        i = start
        while i != end:
            idxs.append(i)
            i = (i+1) % len(line.stops)
        idxs.append(i)

        shift = random.randrange(len(idxs))

        new_stops = deepcopy(line.stops)

        for i in range(len(idxs)):
            new_stops[idxs[i]] = line.stops[idxs[i-shift]]

        return Line(new_stops, self.best_paths)

    def invert(self, line: Line) -> Line:
        start, end = get_sublist_borders(len(line.stops))

        if start <= end:
            new_stops = line.stops[:start] + line.stops[end:start-1:-1] + line.stops[end+1:]
        else:
            new_stops = []
            taken_range = line.stops[start:] + line.stops[:end+1]
            inversed_range = list(reversed(taken_range))

            no_of_elems_to_take_first = len(line.stops)-start
            new_stops = inversed_range[no_of_elems_to_take_first:] + line.stops[end+1:start] + inversed_range[:no_of_elems_to_take_first]

        return Line(new_stops, self.best_paths)


class GenotypeMutator:
    def __init__(self, graph: Graph, best_paths) -> None:
        self.best_paths = best_paths
        self.graph = graph

    def erase_line(self, genotype: Genotype) -> Genotype:
        new_genotype = deepcopy(genotype)
        i = random.randrange(genotype.no_of_lines)
        del new_genotype.lines[i]

        return new_genotype

    def create_line(self, genotype: Genotype) -> Genotype:
        new_line = line_generation.gen_random_line(self.graph, self.best_paths)

        return Genotype(genotype.lines + [new_line])
    
    def split_line(self, genotype: Genotype, duplicate_split_point: bool = True) -> Genotype:
        line_idx = random.randrange(genotype.no_of_lines)
        line = genotype.lines[line_idx]

        stop_idx = random.randrange(len(line.stops))

        new_line1 = Line(line.stops[:stop_idx + (1 if duplicate_split_point else 0)], self.best_paths)
        new_line2 = Line(line.stops[stop_idx:], self.best_paths)
        
        new_genotype = deepcopy(genotype)
        del new_genotype.lines[line_idx]
        new_genotype.lines.extend([new_line1, new_line2])
        
        return new_genotype
        


if __name__ == "__main__":
    # advanced unit tests
    line_mutator = LineMutator([[]])

    class LineMock(Line):
        def __init__(self, stops: list[int]):
            self.stops = stops


    line = LineMock([0,1,2,3,4,5,6])
    print(line.stops)
    # print(line_mutator.rotation_to_right(line).stops)
    print(line_mutator.invert(line).stops)
