from typing import List

class Line:
    def __init__(self, stops: List[int], graph):
        self.stops = stops # ordered list of stops
        # self.edges = [(v, u) for v in stops for u in graph[v] if (v, u) in graph.edges]
        self.edges = []
        for i in range(len(self.stops) - 1):
            v = self.stops[i]
            u = self.stops[i+1]
            self.edges.append((v, u))
