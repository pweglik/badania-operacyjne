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

    def __eq__(self, __value: object) -> bool:
        if type(__value) != Genotype:
            return False
        return all(line in __value.lines for line in self.lines) and all(
            line in self.lines for line in __value.lines
        )
