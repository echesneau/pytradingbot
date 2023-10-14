import numpy as np

def floor(value: float, precision: int = 0) -> float:
    """Function to floor a value with a decimal precision

    Parameters
    ----------
    value: float
        value to floor
    precision: int
        number of decimals

    Returns
    -------
    floor value
    """
    return np.floor(value*10**precision) / 10**precision


def ceil(value: float, precision: int = 0) -> float:
    """Function to ceil a value with a decimal precision

    Parameters
    ----------
    value: float
        value to ceil
    precision: int
        number of decimals

    Returns
    -------
    ceil value
    """
    return np.ceil(value*10**precision) / 10**precision
