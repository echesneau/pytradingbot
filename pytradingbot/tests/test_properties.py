# =================
# Python IMPORTS
# =================
import pandas as pd
import pytest

# =================
# Internal IMPORTS
# =================
from pytradingbot.cores import properties
from pytradingbot.properties_functions import functions
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

    # Update properties with np_ext rolling
    functions.NP_ROLL = True
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_MA_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k-1]).all()
    assert (data[pd.notnull(data)] > market.ask.data.max()).sum() == 0  # value should be higher than -100
    assert (data[pd.notnull(data)] < market.ask.data.min()).sum() == 0  # value should be smaller than 100
    data_np = data.copy()

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.MovingAverage(market=market, parent=market.ask, param={'k': k}))
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_MA_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k - 1]).all()
    assert (data[pd.notnull(data)] > market.ask.data.max()).sum() == 0  # value should be higher than -100
    assert (data[pd.notnull(data)] < market.ask.data.min()).sum() == 0  # value should be smaller than 100
    pd.testing.assert_series_equal(data_np, data, check_less_precise=True)

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
    functions.NP_ROLL = True
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_EMA_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k-1]).all()
    assert (data[pd.notnull(data)] > market.ask.data.max()).sum() == 0  # value should be higher than -100
    assert (data[pd.notnull(data)] < market.ask.data.min()).sum() == 0  # value should be smaller than 100
    data_np = data.copy(deep=True)

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': k}))
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_EMA_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k - 1]).all()
    assert (data[pd.notnull(data)] > market.ask.data.max()).sum() == 0  # value should be higher than -100
    assert (data[pd.notnull(data)] < market.ask.data.min()).sum() == 0  # value should be smaller than 100
    pd.testing.assert_series_equal(data_np, data, check_less_precise=True)

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
    functions.NP_ROLL = True
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_std_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k-1]).all()
    data_np = data.copy(deep=True)

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.StandardDeviation(market=market, parent=market.ask, param={'k': k}))
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_std_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k - 1]).all()
    pd.testing.assert_series_equal(data_np, data, check_less_precise=True)

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.StandardDeviation())
    data = market.child[0]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.order(15)
def test_variation(market_one_day_path):
    # Init
    k = 7
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.Variation(market=market, parent=market.ask, param={'k': k}))

    # Check init
    assert type(market.child[0]) == properties.Variation
    assert market.child[0].parents['data'] == market.ask
    assert market.child[0].parents['market'] == market
    assert market.child[0].name == f"ask_variation_k-{k}"

    # Update properties
    functions.NP_ROLL = True
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_variation_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k-1]).all()
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100
    data_np = data.copy(deep=True)

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.Variation(market=market, parent=market.ask, param={'k': k}))
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_variation_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k - 1]).all()
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100
    pd.testing.assert_series_equal(data_np, data, check_less_precise=True)

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.Variation())
    data = market.child[0]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.order(16)
def test_rsi(market_one_day_path):
    # Init
    k = 7
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.RSI(market=market, parent=market.ask, param={'k': k}))

    # Check init
    assert type(market.child[0]) == properties.RSI
    assert market.child[0].parents['data'] == market.ask
    assert market.child[0].parents['market'] == market
    assert market.child[0].name == f"ask_rsi_k-{k}"

    # Update properties
    functions.NP_ROLL = True
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_rsi_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k-1]).all()
    assert (data < 0).sum() == 0  # value should be higher than -100
    assert (data > 100.1).sum() == 0  # value should be smaller than 100
    data_np = data.copy(deep=True)

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.RSI(market=market, parent=market.ask, param={'k': k}))
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"ask_rsi_k-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k - 1]).all()
    assert (data < 0).sum() == 0  # value should be higher than -100
    assert (data > 100.1).sum() == 0  # value should be smaller than 100
    pd.testing.assert_series_equal(data_np, data, check_less_precise=True)

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.RSI())
    data = market.child[0]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.order(17)
def test_macd(market_one_day_path):
    # Init
    k = 5
    kshort = 7
    klong = 15

    market = market_from_file(market_one_day_path, fmt='csv')[0]
    short = properties.MovingAverage(market=market, parent=market.ask, param={'k': kshort})
    long = properties.MovingAverage(market=market, parent=market.ask, param={'k': klong})
    short.update()
    long.update()
    market.add_child(properties.MACD(market=market, parent={'short': short, 'long': long}, param={'k': k}))

    # Check init
    assert type(market.child[0]) == properties.MACD
    assert market.child[0].parents['short'] == short
    assert market.child[0].parents['long'] == long
    assert market.child[0].parents['market'] == market
    assert market.child[0].name == f"macd_{kshort}-{klong}-{k}"

    # Update properties
    functions.NP_ROLL = True
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"macd_{kshort}-{klong}-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k - klong + 2
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k-1]).all()
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100
    data_np = data.copy(deep=True)

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    short = properties.MovingAverage(market=market, parent=market.ask, param={'k': kshort})
    long = properties.MovingAverage(market=market, parent=market.ask, param={'k': klong})
    short.update()
    long.update()
    market.add_child(properties.MACD(market=market, parent={'short': short, 'long': long}, param={'k': k}))
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"macd_{kshort}-{klong}-{k}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k - klong + 2
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k - 1]).all()
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100
    pd.testing.assert_series_equal(data_np, data, check_less_precise=True)

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.MACD())
    data = market.child[0]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.order(18)
def test_bollinger(market_one_day_path):
    # Init
    k = 7

    market = market_from_file(market_one_day_path, fmt='csv')[0]
    mean = properties.MovingAverage(market=market, parent=market.ask, param={'k': k})
    std = properties.StandardDeviation(market=market, parent=market.ask, param={'k': k})
    mean.update()
    std.update()
    market.add_child(properties.Bollinger(market=market, parent={'data': market.ask, 'mean': mean, 'std': std},
                                          param={'k': 2}))

    # Check init
    assert type(market.child[0]) == properties.Bollinger
    assert market.child[0].parents['data'] == market.ask
    assert market.child[0].parents['mean'] == mean
    assert market.child[0].parents['std'] == std
    assert market.child[0].name == f"bollinger_ask-{k}_{2}"

    # Update properties
    market.child[0].update()
    data = market.child[0].data
    assert market.child[0].name == f"bollinger_ask-{k}_{2}"
    n0 = len(std.data[std.data == 0])
    assert pd.notnull(data).sum() == len(market.dataframe()) - k - n0 + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[:k - 1]).all()
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.Bollinger())
    data = market.child[0]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0
