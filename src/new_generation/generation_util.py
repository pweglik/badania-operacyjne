import numpy as np

def create_index_cycle(idx: list[int], n: int):
    return np.random.choice(idx, size=n, replace=False)
