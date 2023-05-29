import math
from common.Genotype import Genotype
import networkx as nx
import numpy as np
from common.params import alpha, beta, delta, R, OSMNX, K


def get_count_of_lines_at_bus_stop(organism: Genotype, G: nx.Graph) -> np.ndarray:
    """
    Returns number of lines stopping at each bus stop as numpy array
    """
    lines_stopping_count = np.zeros(G.number_of_nodes())

    for line in organism.lines:
        for bus_stop in line.stops:
            lines_stopping_count[bus_stop] += 1

    return lines_stopping_count


def get_bus_stops_points(organism: Genotype, G: nx.Graph) -> np.ndarray:
    """
    Returns sum of points scored by all lines at each bus stop as numpy array
    """
    lines_stopping_count = get_count_of_lines_at_bus_stop(organism, G)

    empty_bus_stops_index = np.where(lines_stopping_count == 0)

    lines_stopping_count[empty_bus_stops_index] = 1

    bus_stop_points: np.ndarray = G.graph["points"] * np.power(
        (1 + R / lines_stopping_count), lines_stopping_count
    )

    bus_stop_points[empty_bus_stops_index] = -delta

    return bus_stop_points


def get_stop_penalty(organism: Genotype) -> float:
    """
    Returns sum of penalties for stopping at bus stops
    """
    penalty: int = 0

    for line in organism.lines:
        penalty += len(line.stops)

    return alpha * penalty


def get_lines_cost(organism: Genotype, G: nx.Graph) -> float:
    """
    Returns sum of costs of paths of all lines
    """
    cost = 0
    for line in organism.lines:
        line_cost = 0
        for edge in line.edges:
            if OSMNX:
                line_cost += K(G[edge[0]][edge[1]][0]["travel_time"])
            else:
                line_cost += K(G[edge[0]][edge[1]]["weight"])

        if len(line.edges) != 0:
            cost += line_cost * (np.log(len(line.edges)) / 2 + 1)

    return cost


def fitness(organism: Genotype, G: nx.Graph) -> float:
    """
    Returns fitness of organism in graph G
    """
    bus_stop_points = get_bus_stops_points(organism, G)
    penalty_number_of_lines = beta * organism.no_of_lines
    penalty_bus_stops = get_stop_penalty(organism)
    penalty_lines_cost = get_lines_cost(organism, G)

    return (
        np.sum(bus_stop_points)
        - penalty_number_of_lines
        - penalty_bus_stops
        - penalty_lines_cost
    )
