from typing import Set
from Line import Line


class Genotype:
    def __init__(self, no_of_lines: int, lines: Set[Line]):
        self.no_of_lines = no_of_lines
        self.lines = lines
