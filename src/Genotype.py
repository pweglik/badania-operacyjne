from src.Line import Line


class Genotype:
    def __init__(self, lines: list[Line]):
        self.lines = lines

    @property
    def no_of_lines(self) -> int:
        return len(self.lines)
