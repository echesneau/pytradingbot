# =================
# Python IMPORTS
# =================
import numpy as np
import pandas as pd
try:
    from numpy_ext import rolling_apply
    NP_ROLL = True
except ImportError:
    NP_ROLL = False

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
    if NP_ROLL:
        odata = rolling_apply(np.mean, k, data.values)
        return pd.Series(index=data.index, data=odata, name=data.name)
    else:
        pass


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
    if NP_ROLL:
        odata = rolling_apply(exp_data, k, data.values)
        return pd.Series(index=data.index, data=odata, name=data.name)
    else:
        pass


def standard_deviation(data: pd.Series, k: int) -> pd.Series:
    if NP_ROLL:
        odata = rolling_apply(np.std, k, data.values)
        return pd.Series(index=data.index, data=odata, name=data.name)
    else:
        pass


def variation(data: pd.Series, k: int):
    def var(values):
        max_prct = (values[1:].max() - values[0]) * 100 / values[0]
        min_prct = (values[1:].min() - values[0]) * 100 / values[0]
        if np.abs(max_prct) > np.abs(min_prct):
            return max_prct
        else:
            return min_prct
    if NP_ROLL:
        odata = rolling_apply(var, k, data.values)
        return pd.Series(index=data.index, data=odata, name=data.name)
    else:
        pass


def rsi(data: pd.Series, k: int):  # TODO
    def func(values):
        shift = np.roll(values, 1)
        diff = values - shift
        diff[0] = np.NaN
        lower = diff[diff < 0]
        higher = diff[diff > 0]
        if len(lower) == 0:
            lower = 0
        else:
            lower = np.mean(lower)
        if len(higher) == 0:
            higher = 0
        else:
            higher = np.mean(higher)
        if lower == higher:
            return 100
        else:
            return 100*higher/(higher-lower)
    if NP_ROLL:
        odata = rolling_apply(func, k, data.values)
        return pd.Series(index=data.index, data=odata, name=data.name)
    else:
        pass


def macd(short: pd.Series, long: pd.Series, k: int):
    diff = (short - long) / short * 100
    if NP_ROLL:
        odata = rolling_apply(np.mean, k, diff.values)
        return pd.Series(index=short.index, data=odata)
    else:
        pass


def bollinger():  # TODO
    pass
