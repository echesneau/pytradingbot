# =================
# Python IMPORTS
# =================
import pandas as pd
import pytest

# =================
# Internal IMPORTS
# =================
from pytradingbot.cores import properties
from pytradingbot.utils.market_tools import market_from_file

# =================
# Variables
# =================


@pytest.mark.order(11)
def test_derivative(market_one_day_path):
    # Init properties
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.Derivative(market=market, parent=market.ask))

    # Check init
    assert type(market.child[0]) == properties.Derivative
    assert market.child[0].parents['data'] == market.ask
    assert market.child[0].parents['market'] == market
    assert market.child[0].name == "ask_deriv"

    # Update properties
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == "ask_deriv"
    assert pd.notnull(data).sum() == len(market.dataframe()) - 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.Derivative())
    data = market.child[0]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.order(12)
def test_moving_average(market_one_day_path):
    # Init
    k = 7
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.MovingAverage(market=market, parent=market.ask, param={'k': k}))

    # Check init
    assert type(market.child[0]) == properties.MovingAverage
    assert market.child[0].parents['data'] == market.ask
    assert market.child[0].parents['market'] == market
    assert market.child[0].name == f"ask_MA_k-{k}"

    # Update properties
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_MA_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k-1]).all()
    assert (data[pd.notnull(data)] > market.ask.data.max()).sum() == 0  # value should be higher than -100
    assert (data[pd.notnull(data)] < market.ask.data.min()).sum() == 0  # value should be smaller than 100

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.MovingAverage())
    data = market.child[0]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.order(13)
def test_exponential_moving_average(market_one_day_path):
    # Init
    k = 7
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': k}))

    # Check init
    assert type(market.child[0]) == properties.ExponentialMovingAverage
    assert market.child[0].parents['data'] == market.ask
    assert market.child[0].parents['market'] == market
    assert market.child[0].name == f"ask_EMA_k-{k}"

    # Update properties
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_EMA_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k-1]).all()
    assert (data[pd.notnull(data)] > market.ask.data.max()).sum() == 0  # value should be higher than -100
    assert (data[pd.notnull(data)] < market.ask.data.min()).sum() == 0  # value should be smaller than 100

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.ExponentialMovingAverage())
    data = market.child[0]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.order(14)
def test_standard_deviation(market_one_day_path):
    # Init
    k = 7
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.StandardDeviation(market=market, parent=market.ask, param={'k': k}))

    # Check init
    assert type(market.child[0]) == properties.StandardDeviation
    assert market.child[0].parents['data'] == market.ask
    assert market.child[0].parents['market'] == market
    assert market.child[0].name == f"ask_std_k-{k}"

    # Update properties
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_std_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k-1]).all()
    #assert (data[pd.notnull(data)] > market.ask.data.max()).sum() == 0  # value should be higher than -100
    #assert (data[pd.notnull(data)] < market.ask.data.min()).sum() == 0  # value should be smaller than 100

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.StandardDeviation())
    data = market.child[0]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0
