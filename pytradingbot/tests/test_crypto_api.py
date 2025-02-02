"""module to test crypto api"""

import time

# =================
# Python IMPORTS
# =================
from datetime import datetime
import pandas as pd
import pytest
import krakenex

# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.crypto_api import KrakenApi, KrakenApiDev

# =================
# Variables
# =================


@pytest.mark.run(order=5)
def test_connect():
    api = KrakenApi()
    api._set_id()
    api.connect()
    assert isinstance(api.session, krakenex.api.API)

    api = KrakenApiDev()
    api.connect()
    assert isinstance(api.session, krakenex.api.API)


@pytest.mark.run(order=6)
def test_get_market(inputs_config_path):
    api = KrakenApi(input_path=inputs_config_path)
    api.connect()
    values = api.get_market()
    for key in ["bid", "ask"]:
        assert key in values
        assert isinstance(values[key], float)


@pytest.mark.run(order=6)
def test_balance(inputs_config_path, balance_path):
    api = KrakenApi(inputs_config_path)
    api.connect()
    balance = api.balance
    assert isinstance(balance, dict)
    assert len(balance.keys()) > 0
    assert "ZEUR" in balance
    for symbol, value in balance.items():
        assert isinstance(symbol, str)
        assert isinstance(value, float)
    api = KrakenApiDev(input_path=inputs_config_path, balance_path=balance_path)
    api.connect()
    balance = api.balance
    assert isinstance(balance, dict)
    assert len(balance.keys()) > 0
    assert "ZEUR" in balance
    for symbol, value in balance.items():
        assert isinstance(symbol, str)
        assert isinstance(value, float)


@pytest.mark.run(order=6)
def test_get_money(inputs_config_path, balance_path):
    api = KrakenApi(inputs_config_path)
    api.connect()
    assert api.mymoney >= 0
    api = KrakenApiDev(input_path=inputs_config_path, imoney=200)
    api.connect()
    assert api.mymoney == 200
    api.balance_dict["ZEUR"] -= 100
    assert api.mymoney == 100
    api = KrakenApiDev(input_path=inputs_config_path, balance_path=balance_path)
    tmp = pd.DataFrame(columns=["name", "quantity"], data=[["ZEUR", 100]]).to_csv(
        balance_path, sep=";", index=False
    )
    assert api.mymoney == 100
    tmp = pd.DataFrame(columns=["name", "quantity"], data=[["ZEUR", 0]]).to_csv(
        balance_path, sep=";", index=False
    )
    assert api.mymoney == 0


@pytest.mark.run(order=6)
def test_calculate_quantity(inputs_config_path):  # Should be in test_base
    api = KrakenApiDev(input_path=inputs_config_path)
    api.balance_dict["ZEUR"] = 100
    assert api.calculate_quantity_buy(10) == 10
    assert api.calculate_quantity_buy(8) == 12.5


@pytest.mark.run(order=6)
def test_buy(inputs_config_path, balance_path):
    api = KrakenApiDev(input_path=inputs_config_path)
    api.balance_dict["ZEUR"] = 100
    api.buy(10, 10)
    assert api.mymoney == 0
    assert api.pair in api.balance.keys()
    assert api.balance[api.pair] == 10
    api = KrakenApiDev(input_path=inputs_config_path, balance_path=balance_path)
    pd.DataFrame(columns=["name", "quantity"], data=[["ZEUR", 10]]).to_csv(
        balance_path, sep=";", index=False
    )
    api.buy(3.5, 2)
    assert api.mymoney == 3
    api = KrakenApi(inputs_config_path)
    api.connect()
    api.pair = "XXBTZEUR"
    api.buy(0.5, 1)
    time.sleep(1)
    assert len(api.open_orders(type="buy", pair="XBTEUR")) == 1
    for o_id in api.open_orders(type="buy", pair="XBTEUR"):
        api.cancel_order_by_id(o_id)


@pytest.mark.run(order=6)
def test_sell(inputs_config_path, balance_path):
    api = KrakenApiDev(input_path=inputs_config_path)
    api.balance_dict["ZEUR"] = 0
    api.balance[api.pair] = 5
    api.sell(5, 10)
    assert api.mymoney == 50
    assert api.pair in api.balance.keys()
    assert api.balance[api.pair] == 0
    api.balance_dict["ZEUR"] = 0
    api.balance[api.pair] = 5
    api.sell(7, 10)
    assert api.mymoney == 50
    assert api.pair in api.balance.keys()
    assert api.balance[api.pair] == 0
    api = KrakenApiDev(input_path=inputs_config_path, balance_path=balance_path)
    pd.DataFrame(
        columns=["name", "quantity"], data=[["ZEUR", 0], ["XXBTZEUR", 5]]
    ).to_csv(balance_path, sep=";", index=False)
    api.sell(5, 2)
    assert api.mymoney == 10
    balance = pd.read_csv(balance_path, sep=";", index_col="name").squeeze(axis=1)
    balance = balance.to_dict()
    assert balance[api.pair] == 0
    pd.DataFrame(
        columns=["name", "quantity"], data=[["ZEUR", 0], ["XXBTZEUR", 5]]
    ).to_csv(balance_path, sep=";", index=False)
    api.sell(7, 4)
    assert api.mymoney == 20
    balance = pd.read_csv(balance_path, sep=";", index_col="name").squeeze(axis=1)
    balance = balance.to_dict()
    assert balance[api.pair] == 0
    api = KrakenApi(inputs_config_path)
    api.connect()
    api.pair = "XETCZEUR"
    api.sell(0.3, 100)
    time.sleep(1)
    assert len(api.open_orders(type="sell", pair="ETCEUR")) == 1
    for o_id in api.open_orders(type="sell", pair="ETCEUR"):
        api.cancel_order_by_id(o_id)


@pytest.mark.run(order=6)
def test_open_orders(inputs_config_path):
    # test structure
    api = KrakenApi(inputs_config_path)
    api.connect()
    open_orders_dict = api._get_open_orders()
    assert "sell" in open_orders_dict
    assert "buy" in open_orders_dict
    open_orders_list = api.open_orders()
    assert isinstance(open_orders_list, list)
    # test filtering type
    api.pair = "XETCZEUR"
    api.buy(5, 0.1)
    api.sell(0.3, 100)
    time.sleep(1)
    assert len(api.open_orders()) == 2
    assert len(api.open_orders(type="sell")) == 1
    assert len(api.open_orders(type="buy")) == 1
    for o_id in api.open_orders(pair="ETCEUR"):
        api.cancel_order_by_id(o_id)


@pytest.mark.run(order=-1)
def test_run_api(inputs_config_path):
    ntest = 10
    api = KrakenApiDev(input_path=inputs_config_path)
    api.connect()
    t0 = datetime.now()
    api.run(times=ntest)
    tf = datetime.now()

    assert (tf - t0).total_seconds() < ntest * api.refresh * 1.1
    assert len(api.market.dataframe()) == ntest
    assert len(api.market.order.data) == ntest
    assert api.market.order.action in [-1, 0, 1]
