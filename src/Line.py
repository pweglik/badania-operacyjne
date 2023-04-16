from typing import List


class Line:
    next_id = 0
    next_color = 0
    colors = ["red", "green", "yellow", "purple", "orange", "olive"]

    def __init__(self, stops: List[int], best_paths):
        self.id = Line.get_next_id()
        self.stops = stops  # ordered list of stops
        self.edges = []
        self.edge_color, self.edge_style = Line.get_next_edge_style()

        for i in range(len(stops) - 1):
            best_path = best_paths[self.stops[i]][self.stops[i + 1]]
            for j in range(len(best_path) - 1):
                v = best_path[j]
                u = best_path[j + 1]
                self.edges.append((v, u))

    def __repr__(self) -> str:
        return str(self.stops)

    @staticmethod
    def get_next_edge_style():
        color = Line.colors[Line.next_color]
        Line.next_color = (Line.next_color + 1) % (len(Line.colors))
        return color, "solid"

    @staticmethod
    def get_next_id():
        Line.next_id += 1
        return Line.next_id - 1
