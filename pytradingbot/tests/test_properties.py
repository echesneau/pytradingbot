# =================
# Python IMPORTS
# =================
import os
import pandas as pd
import pytest

# =================
# Internal IMPORTS
# =================
from pytradingbot.cores import markets, properties
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

    # Update properties
    market.child[0].update()
    data = market.child[0].data
    assert pd.notnull(data).sum() == len(market.dataframe()) - 1
    assert (data < -100).sum() == 0  # value should be higher than -100
    assert (data > 100).sum() == 0  # value should be smaller than 100

    # Check what's happened if parents and market is None
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.add_child(properties.Derivative())
    data = market.child[0]
    assert len(data.parents.keys()) == 0
    assert len(data.data) == 0
