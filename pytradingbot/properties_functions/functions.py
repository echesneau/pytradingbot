# =================
# Python IMPORTS
# =================
import numpy as np
from numpy_ext import rolling_apply
import pandas as pd

# =================
# Internal IMPORTS
# =================

# =================
# Variables
# =================


def derivative(data: pd.Series) -> pd.Series:
    # Difference
    odata = data.diff()

    # normalize to minute
    time = data.index.to_series().diff().dt.total_seconds()/60
    odata /= time

    # normalize in %
    odata = odata / data * 100
    return odata


def MA(data: pd.Series, k: int) -> pd.Series:
    """
    function to calculate Moving average of data

    Parameters
    ----------
    data: pd.Series
    k: int
        window size for the moving average

    Returns
    -------
    pd.Series

    """
    odata = rolling_apply(np.mean, k, data.values)
    return pd.Series(index=data.index, data=odata, name=data.name)


def EMA(data: pd.Series, k: int) -> pd.Series:
    """
    function to calculate Exponential Moving average of data

    Parameters
    ----------
    data: pd.Series
    k: int
        window size for the moving average

    Returns
    -------
    pd.Series

    """
    def exp_data(value):
        size = value.shape[0]
        a = 2 / (np.arange(1, size+1)+1)
        a = np.flipud(a)
        exp_val = value * a
        mean = np.sum(exp_val) / np.sum(a)
        return mean

    odata = rolling_apply(exp_data, k, data.values)
    return pd.Series(index=data.index, data=odata, name=data.name)


def standard_deviation(data: pd.Series, k: int) -> pd.Series:
    odata = rolling_apply(np.std, k, data.values)
    return pd.Series(index=data.index, data=odata, name=data.name)
