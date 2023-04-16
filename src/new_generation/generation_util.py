from copy import deepcopy
from typing import MutableSequence, TypeVar
from intervaltree import IntervalTree, Interval
import random as rd
import numpy as np

from src.Line import Line

T = TypeVar("T", bound=MutableSequence)

def create_index_cycle(idx: list[int], n: int):
    return np.random.choice(idx, size=n, replace=False)

def get_sublist_borders(n: int) -> tuple[int, int]:
    return (rd.randrange(n), rd.randrange(n))

def shift_by_idxs(arr: T, idxs: list[int], shift: int) -> T:
    copied = deepcopy(arr)

    for i in range(len(idxs)):
        copied[idxs[i]] = arr[idxs[i-shift]]

    return copied

class LineListLinearizer(MutableSequence):
    def __init__(self, lines: list[Line]) -> None:
        index_intervals = []
        idx = 0
        for line in lines:
            index_intervals.append(Interval(idx, idx + len(line.stops), data=line))
            idx += len(line.stops)

        self.tree = IntervalTree(index_intervals)

    def __getitem__(self, i: int) -> int:
        interval = self.tree.at(i).pop()
        line: Line = interval.data

        return line.stops[i - interval.begin]

    def __setitem__(self, i: int, val: int) -> None:
        # assumes i is already in the existing range
        interval = self.tree.at(i).pop()
        line: Line = interval.data
        line.stops[i - interval.begin] = val

    def __delitem__(self, i: int) -> None:
        raise NotImplementedError()

    def insert(self, index: int, value: int) -> None:
        raise NotImplementedError()

    def __len__(self) -> int:
        return self.tree.end() - self.tree.begin()

    def stops(self) -> list[list[int]]:
        return [interval.data.stops for interval in self.tree.items()]


if __name__ == "__main__":
    def main():
        from src import line_generation, graph_generation
        G, bp = graph_generation.generate_city_graph(10)
        lines = [line_generation.gen_random_line(G, bp, i + 3) for i in range(4)]

        print('lines', lines)

        linearized = LineListLinearizer(lines)
        print('stops', linearized.stops())
        print(linearized[1])
        print(linearized[2])
        print(linearized[3])
        print(linearized[4])
        print(linearized[5])
        print(len(linearized))

    main()
