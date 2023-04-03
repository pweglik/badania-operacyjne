import random

from Line import Line


def random_one(X):
    # TODO probably inefficient
    return random.sample(list(X), 1)[0]

def random_one_not_in(X, excluded, max_attempts):
    # get random neighbor (non-repeating ones only)
    for _ in range(max_attempts):
        u = random_one(X)
        if u not in excluded:
            break
        # u not repeating but we may be
    else:
        return None

    return u

# this one has a problem that it can repeat A LOT
# of stops as it's vertice-oriented
def gen_random_line_random_vertices(G, best_paths, length):

    # take random <length> nodes from G
    vertices = random.sample(list(G.nodes), length)
    # random.shuffle(V)

    print("vertices", vertices)


    stops = [vertices[0]]
    for v, u in zip(vertices, vertices[1:]):
        # skip first as this loops to the next best path
        for k in best_paths[v][u][1:]:
            stops.append(k)

    print("stops", stops)

    return Line(stops)


def gen_random_line_random_paths(G, length, max_attempts=100):

    # take random node from G
    v = random_one(G)

    stops = [v]
    # faster <in> checks
    stops_set = set(stops)

    for _ in range(length-1):
        # get random neighbor (non-repeating ones only)
        # for _ in range(max_attempts):
        #     u = random_one(G[v])
        #     if u not in stops_set:
        #         break
        #     # u not repeating but we may be
        # else:
        #     print(f"couldn't find next stop for line length={length}, left={length-len(stops)} stuck in {v}")
        #     print(f"returning line length {len(stops)} of requested {length}")
        #     break

        u = random_one_not_in(G[v], stops_set, max_attempts)
        if u is None:
            print(f"couldn't find next stop for line length={length}, left={length-len(stops)} stuck in {v}")
            print(f"returning line length {len(stops)} of requested {length}")
            break

        stops.append(u)
        stops_set.add(u)
        v = u


    return Line(stops)


def gen_random_line_random_paths_recursive(G, length, max_attempts=100):

    not_in = set()

    def get_line(start, length):
        if length == 0:
            return []

        for _ in range(max_attempts):
            nxt = random_one_not_in(G[start], not_in, max_attempts)
            if nxt is None:
                # nowhere to go from here
                return None

            not_in.add(nxt)

            rest_of_line = get_line(nxt, length-1)
            if rest_of_line is None:
                # failed to find line from <nxt>
                not_in.remove(nxt)

            else:
                # found good ending
                return [start] + rest_of_line

        return None

    # take random start node from G
    v = random_one(G)
    not_in.add(v)

    return Line(get_line(v, length))