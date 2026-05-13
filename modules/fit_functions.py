import numpy as np
import numpy.typing as npt

def linear_function(x: float | npt.NDArray[np.float64], a: float, b: float) -> float | npt.NDArray[np.float64]:
    return a * x + b

