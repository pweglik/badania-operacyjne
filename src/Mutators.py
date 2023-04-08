from copy import deepcopy
import random
from src.Line import Line


def get_sublist_borders(n: int) -> tuple[int, int]:
    return (random.randrange(n), random.randrange(n))


class LineMutator:
    def __init__(self) -> None:
        pass

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

        return Line(new_stops, line.best_paths)

    def invert(self, line: Line) -> Line:
        start, end = get_sublist_borders(len(line.stops))
        start, end = 5, 2

        if start <= end:
            new_stops = line.stops[:start] + line.stops[end:start-1:-1] + line.stops[end+1:]
        else:
            new_stops = []
            taken_range = line.stops[start:] + line.stops[:end+1]
            inversed_range = list(reversed(taken_range))

            no_of_elems_to_take_first = len(line.stops)-start
            new_stops = inversed_range[no_of_elems_to_take_first:] + line.stops[end+1:start] + inversed_range[:no_of_elems_to_take_first]

        return Line(new_stops, line.best_paths)
        


if __name__ == "__main__":
    # advanced unit tests
    line_mutator = LineMutator()

    class LineMock(Line):
        def __init__(self, stops: list[int]):
            self.stops = stops


    line = LineMock([0,1,2,3,4,5,6])
    print(line.stops)
    # print(line_mutator.rotation_to_right(line).stops)
    print(line_mutator.invert(line).stops)
