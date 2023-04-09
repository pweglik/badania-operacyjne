from copy import deepcopy
from typing import MutableSequence, TypeVar
from intervaltree import IntervalTree, Interval
import numpy as np

from src.Line import Line

T = TypeVar("T", bound=MutableSequence)

def create_index_cycle(idx: list[int], n: int):
    return np.random.choice(idx, size=n, replace=False)


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
            index_intervals.append(Interval(idx, idx + len(line.stops) - 1, data=line))
            idx += len(line.stops)

        self.tree = IntervalTree(index_intervals)

    def __getitem__(self, i: int) -> int:
        interval = self.tree.at(i).pop()
        line: Line = interval.data

        return line.stops[i - interval.begin]

    def __setitem__(self, i: int, val: int) -> None:
        interval = self.tree.at(i).pop()
        line: Line = interval.data
        line.stops[i - interval.begin] = val

    def __len__(self) -> int:
        return self.tree.end() - self.tree.begin() + 1

    def stops(self) -> set[list[int]]:
        return {interval.data.stops for interval in self.tree.items()}

