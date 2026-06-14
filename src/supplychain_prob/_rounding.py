from __future__ import annotations
import numpy as np

def bankers_round_to_int(x: float | np.ndarray) -> int | np.ndarray:
    y = np.rint(x)
    if isinstance(y, np.ndarray):
        return y.astype(np.int64)
    return int(y)
