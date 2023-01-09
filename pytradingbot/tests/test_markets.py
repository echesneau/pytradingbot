# =================
# Python IMPORTS
# =================
import pandas as pd
import pytest
# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.crypto_api import KrakenApi, KrakenApiDev
from pytradingbot.cores import markets
# =================
# Variables
# =================

@pytest.mark.order(5)
def test_create_market():
    api = KrakenApiDev()
    api.set_market(markets.Market(parent=api))
    assert len(api.market.dataframe()) == 0
    assert api.market.ask.name == 'ask'
    assert type(api.market.ask.data) == pd.Series
    assert api.market.ask.data.name == 'ask'
    assert api.market.bid.name == 'bid'
    assert type(api.market.bid.data) == pd.Series
    assert api.market.bid.data.name == 'bid'

@pytest.mark.order(6)
def test_update(kraken_user, inputs_config_path):
    # Init API and Market
    api = KrakenApiDev(user=kraken_user, inputs=inputs_config_path)
    api.set_market(markets.Market(parent=api))
    api.connect()

    # Check initial state of Market
    assert len(api.market.ask.data) == 0
    assert len(api.market.bid.data) == 0
    assert api.market.bid.data.name == 'bid'
    assert api.market.ask.data.name == 'ask'
    assert len(api.market.dataframe()) == 0
    for prop in ['ask', 'bid']:
        assert prop in api.market.dataframe().columns

    # Check state after updates
    for i in range(3):
        api.update_market()
        assert len(api.market.ask.data) == i+1
        assert len(api.market.bid.data) == i+1
        assert api.market.bid.data.name == 'bid'
        assert api.market.ask.data.name == 'ask'
        assert len(api.market.dataframe()) == i+1
        for prop in ['ask', 'bid']:
            assert prop in api.market.dataframe().columns






def test_analyse():
    assert True
