from typing import Any
import numpy as np

import networkx as nx

from common.params import GRAPH_SEED, POINTS_MULTIPLIER

import json
import math
import osmnx as ox
from pyproj import Transformer


def f(d):
    return 10 * math.exp(-100 * d)


def generate_city_graph(n: int) -> tuple[nx.Graph, Any]:
    rng = np.random.default_rng(GRAPH_SEED)

    G = nx.generators.geometric.geographical_threshold_graph(
        n=n,
        theta=n * 0.8,
        seed=GRAPH_SEED,
    )

    solitary = [n for n in nx.algorithms.isolate.isolates(G)]
    G.remove_nodes_from(solitary)

    positions = nx.function.get_node_attributes(G, "pos")

    weights = np.zeros((n, n))

    for node1, pos1 in positions.items():
        for node2, pos2 in positions.items():
            weights[node1][node2] = weights[node2][node1] = np.linalg.norm(
                np.array([pos1[0] - pos2[0], pos1[1] - pos2[1]])
            )

    for edge in G.edges:
        G[edge[0]][edge[1]]["weight"] = weights[edge[0]][edge[1]]

    # mockup for tests, this should be
    # set manually or be derived from population density
    points = rng.random(G.number_of_nodes())
    G.graph["points"] = points * POINTS_MULTIPLIER

    best_paths = dict(nx.all_pairs_shortest_path(G))

    return (G, best_paths)


def parse_feature(f, transformer):
    center_lat = 0
    center_long = 0
    cnt = 0
    for x, y in f["geometry"]["coordinates"][0]:
        lat, long = transformer.transform(y, x)
        # simple avg
        center_lat += lat
        center_long += long
        cnt += 1

    center_lat /= cnt
    center_long /= cnt

    return {
        "lat": center_lat,
        "long": center_long,
        "people": f["properties"]["r_ogolem"],
    }


def load_cracow_city_graph() -> tuple[nx.Graph, Any]:
    ox.config(use_cache=True, log_console=True)

    # download street network data from OSM and construct a MultiDiGraph model
    G = ox.graph_from_point(
        (50.061541, 19.938039),
        dist=5000,
        network_type="drive",
        simplify=True,
        custom_filter='["highway"~"primary|secondary|tertiary"]',
    )

    G_orig = G

    G = ox.project_graph(G)
    G = ox.simplification.consolidate_intersections(
        G, tolerance=60, rebuild_graph=True, dead_ends=False, reconnect_edges=True
    )

    # impute edge (driving) speeds and calculate edge traversal times
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    G = G.to_undirected()

    Z = json.load(open("zameldowania_stale_2022_krk.geojson"))
    transformer = Transformer.from_crs(Z["crs"]["properties"]["name"], "EPSG:4326")
    lat_long_people = [parse_feature(zf, transformer) for zf in Z["features"]]

    def get_lat_long(node):
        if "lat" in node and "lon" in node:
            lat, long = node["lat"], node["lon"]
        else:
            lat = 0
            long = 0
            cnt = 0
            for orig_idx in eval(node["osmid_original"]):
                orig_node = G_orig.nodes[orig_idx]
                lat += orig_node["y"]
                long += orig_node["x"]
                cnt += 1
            lat /= cnt
            long /= cnt

        return lat, long

    points = []
    for idx in G.nodes:
        node = G.nodes[idx]
        lat, long = get_lat_long(node)

        # print(f"{lat:20.6f} {long:20.6f}")

        S = 0
        for llp in lat_long_people:
            d2 = (lat - llp["lat"]) ** 2 + (long - llp["long"]) ** 2
            d = math.sqrt(d2)

            S += llp["people"] * f(d)

        points.append(S)

    solitary = [n for n in nx.algorithms.isolate.isolates(G)]
    G.remove_nodes_from(solitary)

    # for edge in G.edges:
    #     G[edge[0]][edge[1]]["weight"] = G[edge[0]][edge[1]][0]["travel_time"]

    G.graph["points"] = points
    # nx.set_node_attributes(G, values=points, name="points")

    best_paths = dict(nx.all_pairs_shortest_path(G))

    return G, best_paths
