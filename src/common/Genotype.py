from collections import Counter

from common.Line import Line


class Genotype:
    def __init__(self, lines: list[Line]):
        self.lines = lines

    @property
    def no_of_lines(self) -> int:
        return len(self.lines)

    def get_line_stops_count_summary(self):
        return Counter([len(line.stops) for line in self.lines])
