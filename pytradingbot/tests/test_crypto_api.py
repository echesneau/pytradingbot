# =================
# Python IMPORTS
# =================
import pandas as pd
import pytest
import krakenex
from datetime import datetime

# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.crypto_api import KrakenApi, KrakenApiDev

# =================
# Variables
# =================


@pytest.mark.run(order=5)
def test_connect(kraken_user):
    api = KrakenApi()
    api._set_id(kraken_user)
    api.connect()
    assert type(api.session) is krakenex.api.API

    api = KrakenApiDev(user=kraken_user)
    api.connect()
    assert type(api.session) is krakenex.api.API


@pytest.mark.run(order=6)
def test_get_market(kraken_user, inputs_config_path):
    api = KrakenApiDev(user=kraken_user, input_path=inputs_config_path)
    api.connect()
    values = api.get_market()
    for key in ['bid', 'ask']:
        assert key in values.keys()
        assert type(values[key]) == float


@pytest.mark.run(order=6)
def test_get_money(kraken_user, inputs_config_path, balance_path):
    api = KrakenApiDev(user=kraken_user, input_path=inputs_config_path, imoney=200)
    api.connect()
    assert api.mymoney == 200
    api.money -= 100
    assert api.mymoney == 100
    api = KrakenApiDev(user=kraken_user, input_path=inputs_config_path, balance_path=balance_path)
    tmp = pd.DataFrame(columns=['name', 'quantity'], data=[["EUR", 100]]).to_csv(balance_path, sep=";", index=False)
    assert api.mymoney == 100
    tmp = pd.DataFrame(columns=['name', 'quantity'], data=[["EUR", 0]]).to_csv(balance_path, sep=";", index=False)
    assert api.mymoney == 0

@pytest.mark.run(order=6)
def test_calculate_quantity(kraken_user, inputs_config_path):  # Should be in test_base
    api = KrakenApiDev(user=kraken_user, input_path=inputs_config_path)
    api.money = 100
    assert api.calculate_quantity_buy(10) == 10
    assert api.calculate_quantity_buy(8) == 12.5


@pytest.mark.run(order=6)
def test_buy(kraken_user, inputs_config_path, balance_path):
    api = KrakenApiDev(user=kraken_user, input_path=inputs_config_path)
    api.money = 100
    api.buy(10, 10)
    assert api.mymoney == 0
    assert api.pair in api.balance.keys()
    assert api.balance[api.pair] == 10
    api = KrakenApiDev(user=kraken_user, input_path=inputs_config_path, balance_path=balance_path)
    pd.DataFrame(columns=['name', 'quantity'], data=[["EUR", 10]]).to_csv(balance_path, sep=";", index=False)
    api.buy(3.5, 2)
    assert api.mymoney == 3



@pytest.mark.run(order=-1)
def test_run_api(kraken_user, inputs_config_path):
    ntest = 10
    api = KrakenApiDev(user=kraken_user, input_path=inputs_config_path)
    api.connect()
    t0 = datetime.now()
    api.run(times=ntest)
    tf = datetime.now()

    assert (tf-t0).total_seconds() < ntest * api.refresh * 1.1
    assert len(api.market.dataframe()) == ntest
    assert len(api.market.order.data) == ntest
    assert api.market.order.action in [-1, 0, 1]
