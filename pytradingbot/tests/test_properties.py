# =================
# Python IMPORTS
# =================
import pandas as pd
import pytest
from numpy.testing import assert_approx_equal

# =================
# Internal IMPORTS
# =================
from pytradingbot.cores import properties
from pytradingbot.properties_functions import functions
from pytradingbot.utils.market_tools import market_from_file


# =================
# Variables
# =================


@pytest.mark.run(order=14)
def test_derivative(market_one_day_path):
    # Init properties
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.Derivative(market=market, parent=market.ask))

    # Check init
    assert type(market.child[3]) == properties.Derivative
    assert market.child[3].parents["data"] == market.ask
    assert market.child[3].parents["market"] == market
    assert market.child[3].name == "deriv_ask"

    # Update properties
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == "deriv_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.Derivative())
    data = market.child[3]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.run(order=15)
def test_moving_average(market_one_day_path):
    # Init
    k = 7
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(
        properties.MovingAverage(market=market, parent=market.ask, param={"k": k})
    )

    # Check init
    assert type(market.child[3]) == properties.MovingAverage
    assert market.child[3].parents["data"] == market.ask
    assert market.child[3].parents["market"] == market
    assert market.child[3].name == f"MA_k-{k}_ask"

    # Update properties with np_ext rolling
    functions.NP_ROLL = True
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == f"MA_k-{k}_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (
        data[pd.notnull(data)] > market.ask.data.max()
    ).sum() == 0  # value should be higher than -100
    assert (
        data[pd.notnull(data)] < market.ask.data.min()
    ).sum() == 0  # value should be smaller than 100
    data_np = data.copy()

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(
        properties.MovingAverage(market=market, parent=market.ask, param={"k": k})
    )
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == f"MA_k-{k}_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (
        data[pd.notnull(data)] > market.ask.data.max()
    ).sum() == 0  # value should be higher than -100
    assert (
        data[pd.notnull(data)] < market.ask.data.min()
    ).sum() == 0  # value should be smaller than 100
    pd.testing.assert_series_equal(data_np, data, atol=1e-3)

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.MovingAverage())
    data = market.child[3]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.run(order=16)
def test_exponential_moving_average(market_one_day_path):
    # Init
    k = 7
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(
        properties.ExponentialMovingAverage(
            market=market, parent=market.ask, param={"k": k}
        )
    )

    # Check init
    assert type(market.child[3]) == properties.ExponentialMovingAverage
    assert market.child[3].parents["data"] == market.ask
    assert market.child[3].parents["market"] == market
    assert market.child[3].name == f"EMA_k-{k}_ask"

    # Update properties
    functions.NP_ROLL = True
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == f"EMA_k-{k}_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (
        data[pd.notnull(data)] > market.ask.data.max()
    ).sum() == 0  # value should be higher than -100
    assert (
        data[pd.notnull(data)] < market.ask.data.min()
    ).sum() == 0  # value should be smaller than 100
    data_np = data.copy(deep=True)

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(
        properties.ExponentialMovingAverage(
            market=market, parent=market.ask, param={"k": k}
        )
    )
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == f"EMA_k-{k}_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (
        data[pd.notnull(data)] > market.ask.data.max()
    ).sum() == 0  # value should be higher than -100
    assert (
        data[pd.notnull(data)] < market.ask.data.min()
    ).sum() == 0  # value should be smaller than 100
    pd.testing.assert_series_equal(data_np, data, atol=1e-3)

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.ExponentialMovingAverage())
    data = market.child[3]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.run(order=17)
def test_standard_deviation(market_one_day_path):
    # Init
    k = 7
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(
        properties.StandardDeviation(market=market, parent=market.ask, param={"k": k})
    )

    # Check init
    assert type(market.child[3]) == properties.StandardDeviation
    assert market.child[3].parents["data"] == market.ask
    assert market.child[3].parents["market"] == market
    assert market.child[3].name == f"std_k-{k}_ask"

    # Update properties
    functions.NP_ROLL = True
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == f"std_k-{k}_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    data_np = data.copy(deep=True)

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(
        properties.StandardDeviation(market=market, parent=market.ask, param={"k": k})
    )
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == f"std_k-{k}_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    pd.testing.assert_series_equal(data_np, data, atol=1e-3)

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.StandardDeviation())
    data = market.child[3]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.run(order=18)
def test_variation(market_one_day_path):
    # Init
    k = 7
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(
        properties.Variation(market=market, parent=market.ask, param={"k": k})
    )

    # Check init
    assert type(market.child[3]) == properties.Variation
    assert market.child[3].parents["data"] == market.ask
    assert market.child[3].parents["market"] == market
    assert market.child[3].name == f"variation_k-{k}_ask"

    # Update properties
    functions.NP_ROLL = True
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == f"variation_k-{k}_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100
    data_np = data.copy(deep=True)

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(
        properties.Variation(market=market, parent=market.ask, param={"k": k})
    )
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == f"variation_k-{k}_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100
    pd.testing.assert_series_equal(data_np, data, atol=1e-3)

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.Variation())
    data = market.child[3]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.run(order=19)
def test_rsi(market_one_day_path):
    # Init
    k = 7
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.RSI(market=market, parent=market.ask, param={"k": k}))

    # Check init
    assert type(market.child[3]) == properties.RSI
    assert market.child[3].parents["data"] == market.ask
    assert market.child[3].parents["market"] == market
    assert market.child[3].name == f"rsi_k-{k}_ask"

    # Update properties
    functions.NP_ROLL = True
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == f"rsi_k-{k}_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (data < 0).sum() == 0  # value should be higher than -100
    assert (data > 100.1).sum() == 0  # value should be smaller than 100
    data_np = data.copy(deep=True)

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.RSI(market=market, parent=market.ask, param={"k": k}))
    market.child[3].update()
    data = market.child[3].data
    assert market.child[3].name == f"rsi_k-{k}_ask"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (data < 0).sum() == 0  # value should be higher than -100
    assert (data > 100.1).sum() == 0  # value should be smaller than 100
    pd.testing.assert_series_equal(data_np, data, atol=1e-3)

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.RSI())
    data = market.child[3]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.run(order=20)
def test_macd(market_one_day_path):
    # Init
    k = 5
    kshort = 7
    klong = 15

    market = market_from_file(market_one_day_path, fmt="csv")[0]
    short = properties.MovingAverage(
        market=market, parent=market.ask, param={"k": kshort}
    )
    long = properties.MovingAverage(
        market=market, parent=market.ask, param={"k": klong}
    )
    short.update()
    long.update()
    market.add_child(
        properties.MACD(
            market=market, parent={"short": short, "long": long}, param={"k": k}
        )
    )

    # Check init
    assert type(market.child[-1]) == properties.MACD
    assert market.child[-1].parents["short"] == short
    assert market.child[-1].parents["long"] == long
    assert market.child[-1].parents["market"] == market
    assert market.child[-1].name == f"macd_k-{k}_long_{long.name}_short_{short.name}"

    # Update properties
    functions.NP_ROLL = True
    market.child[-1].update()
    data = market.child[-1].data
    assert market.child[-1].name == f"macd_k-{k}_long_{long.name}_short_{short.name}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k - klong + 2
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100
    data_np = data.copy(deep=True)

    # Update properties with pd roll
    functions.NP_ROLL = False
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    short = properties.MovingAverage(
        market=market, parent=market.ask, param={"k": kshort}
    )
    long = properties.MovingAverage(
        market=market, parent=market.ask, param={"k": klong}
    )
    short.update()
    long.update()
    market.add_child(
        properties.MACD(
            market=market, parent={"short": short, "long": long}, param={"k": k}
        )
    )
    market.child[-1].update()
    data = market.child[-1].data
    assert market.child[-1].name == f"macd_k-{k}_long_{long.name}_short_{short.name}"
    assert pd.notnull(data).sum() == len(market.dataframe()) - k - klong + 2
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100
    pd.testing.assert_series_equal(data_np, data, atol=1e-3)

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.MACD())
    data = market.child[-1]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.run(order=21)
def test_bollinger(market_one_day_path):
    # Init
    k = 7

    market = market_from_file(market_one_day_path, fmt="csv")[0]
    mean = properties.MovingAverage(market=market, parent=market.ask, param={"k": k})
    std = properties.StandardDeviation(market=market, parent=market.ask, param={"k": k})
    mean.update()
    std.update()
    market.add_child(
        properties.Bollinger(
            market=market,
            parent={"data": market.ask, "mean": mean, "std": std},
            param={"k": 2},
        )
    )

    # Check init
    assert type(market.child[-1]) == properties.Bollinger
    assert market.child[-1].parents["data"] == market.ask
    assert market.child[-1].parents["mean"] == mean
    assert market.child[-1].parents["std"] == std
    assert (
        market.child[-1].name
        == f"bollinger_k-2_data_ask_mean_{mean.name}_std_{std.name}"
    )

    # Update properties
    market.child[-1].update()
    data = market.child[-1].data
    assert (
        market.child[-1].name
        == f"bollinger_k-2_data_ask_mean_{mean.name}_std_{std.name}"
    )
    n0 = len(std.data[std.data == 0])
    assert pd.notnull(data).sum() == len(market.dataframe()) - k - n0 + 1
    assert pd.isnull(data).values[0]
    assert pd.notnull(data).values[-1]
    assert pd.isnull(data.iloc[: k - 1]).all()
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    market.add_child(properties.Bollinger())
    data = market.child[-1]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0


@pytest.mark.run(order=22)
def test_generate_derivative_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    prop = properties.generate_property_by_name("deriv_ask", market)
    assert prop.type == "deriv"
    assert prop.parents["data"].type == "market"


@pytest.mark.run(order=23)
def test_generate_moving_average_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    prop = properties.generate_property_by_name("MA_k-7_ask", market)
    assert prop.type == "MA"
    assert prop.param["k"] == 7
    assert prop.parents["data"].type == "market"


@pytest.mark.run(order=24)
def test_generate_exponential_moving_average_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    prop = properties.generate_property_by_name("EMA_k-7_ask", market)
    assert prop.type == "EMA"
    assert prop.param["k"] == 7
    assert prop.parents["data"].type == "market"


@pytest.mark.run(order=25)
def test_generate_standard_deviation_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    prop = properties.generate_property_by_name("std_k-7_ask", market)
    assert prop.type == "std"
    assert prop.param["k"] == 7
    assert prop.parents["data"].type == "market"


@pytest.mark.run(order=26)
def test_generate_variation_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    prop = properties.generate_property_by_name("variation_k-7_ask", market)
    assert prop.type == "variation"
    assert prop.param["k"] == 7
    assert prop.parents["data"].type == "market"


@pytest.mark.run(order=27)
def test_generate_rsi_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    prop = properties.generate_property_by_name("rsi_k-7_ask", market)
    assert prop.type == "rsi"
    assert prop.param["k"] == 7
    assert prop.parents["data"].type == "market"


@pytest.mark.run(order=28)
def test_generate_macd_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    prop = properties.generate_property_by_name(
        "macd_k-7_long_EMA_k-21_ask_short_EMA_k-7_ask", market
    )
    assert prop.type == "macd"
    assert prop.param["k"] == 7


@pytest.mark.run(order=29)
def test_generate_bollinger_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    prop = properties.generate_property_by_name(
        "bollinger_k-2_data_ask_mean_MA_k-7_ask_std_std_k-7_ask", market
    )
    assert prop.type == "bollinger"
    assert prop.param["k"] == 2


@pytest.mark.run(order=30)
def test_generate_properties_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt="csv")[0]
    prop = properties.generate_property_by_name("ask", market)
    assert prop.name == "ask"
    prop = properties.generate_property_by_name("deriv_MA_k-7_ask", market)
    assert prop.type == "deriv"
    prop = properties.generate_property_by_name("toto", market)
    assert prop is None
    prop = properties.generate_property_by_name("toto_k-7_ask", market)
    assert prop is None
