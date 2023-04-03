from typing import List


class Line:

    next_id = 0
    next_color = 0
    colors = ["red", "green", "yellow", "purple", "orange", "olive"]

    def __init__(self, stops: List[int], graph=None):
        self.id = Line.get_next_id()
        self.stops = stops  # ordered list of stops
        # self.edges = [(v, u) for v in stops for u in graph[v] if (v, u) in graph.edges]
        self.edges = []
        self.edge_color, self.edge_style = Line.get_next_edge_style()
        for i in range(len(self.stops) - 1):
            v = self.stops[i]
            u = self.stops[i + 1]
            self.edges.append((v, u))

    @staticmethod
    def get_next_edge_style():
        color = Line.colors[Line.next_color]
        Line.next_color = (Line.next_color + 1) % (len(Line.colors))
        return color, "solid"

    @staticmethod
    def get_next_id():
        Line.next_id += 1
        return Line.next_id - 1
