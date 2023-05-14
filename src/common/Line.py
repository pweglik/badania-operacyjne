from copy import deepcopy
from functools import cached_property


class Line:
    next_id = 0
    next_color = 0
    colors = ["red", "green", "yellow", "purple", "orange", "olive"]

    def __init__(self, stops: list[int], best_paths):
        self.id = Line.get_next_id()
        self.stops = stops  # ordered list of stops
        self.edge_color, self.edge_style = Line.get_next_edge_style()
        self.best_paths = best_paths

    @cached_property
    def edges(self) -> list[tuple[int, int]]:
        edges = []
        for i in range(len(self.stops) - 1):
            best_path = self.best_paths[self.stops[i]][self.stops[i + 1]]
            for j in range(len(best_path) - 1):
                v = best_path[j]
                u = best_path[j + 1]
                edges.append((v, u))

        return edges

    @property
    def stops_no(self) -> int:
        return len(self.stops)

    def __eq__(self, __value: object) -> bool:
        if type(__value) != Line:
            return False
        return self.stops == __value.stops

    def __repr__(self) -> str:
        return str(self.stops)

    def __deepcopy__(self, _):
        return Line(deepcopy(self.stops), self.best_paths)

    @staticmethod
    def get_next_edge_style():
        color = Line.colors[Line.next_color]
        Line.next_color = (Line.next_color + 1) % (len(Line.colors))
        return color, "solid"

    @staticmethod
    def get_next_id():
        Line.next_id += 1
        return Line.next_id - 1
