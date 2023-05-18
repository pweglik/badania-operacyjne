import numpy as np


def exp_pdf_for_range(i: np.ndarray, n: int, lamb: float) -> np.ndarray:
    x_to_neg_lamb_x = pow(1 - i / n, lamb)
    almost_probs = lamb * x_to_neg_lamb_x
    return almost_probs / almost_probs.sum()
