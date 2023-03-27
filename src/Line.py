class Line:
    def __init__(self, stops: list[int], graph):
        self.stops = stops # ordered list of stops
        self.edges = [(v, u) for v in stops for u in graph[v] if (v, u) in graph.edges]
