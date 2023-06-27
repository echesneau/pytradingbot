# =================
# Python IMPORTS
# =================
import pytest
import numpy as np
import pandas as pd

# =================
# Internal IMPORTS
# =================
from pytradingbot.utils.market_tools import market_from_file
from pytradingbot.cores.orders import ConditionUpper, ConditionLower, ConditionCrossUp, ConditionCrossDown, ActionBuy, \
    ActionSell, Order, generate_condition_from_dict, generate_action_from_dict


@pytest.mark.run(order=39)
def test_condition_greater_than(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    condition = ConditionUpper(market.ask, 0)
    assert isinstance(condition, ConditionUpper)
    condition.update()
    assert len(condition.data) == len(market.ask.data)
    assert condition.data.all()
    median = market.ask.data.median()
    condition = ConditionUpper(market.ask, median)
    condition.update()
    data = condition.data
    assert len(data[data]) == np.floor(len(market.ask.data)/2)


@pytest.mark.run(order=40)
def test_condition_lower_than(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    condition = ConditionLower(market.ask, 0)
    assert isinstance(condition, ConditionLower)
    condition.update()
    assert len(condition.data) == len(market.ask.data)
    assert condition.data.sum() == 0
    median = market.ask.data.median()
    condition = ConditionLower(market.ask, median)
    condition.update()
    data = condition.data
    assert len(data[data == True]) == np.floor(len(market.ask.data)/2) - 1


@pytest.mark.run(order=41)
def test_condition_cross_up(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    size = market.ask.data
    market.ask.data = pd.Series(data=range(len(size)))
    condition = ConditionCrossUp(market.ask, 10)
    assert isinstance(condition, ConditionCrossUp)
    condition.update()
    data = condition.data
    assert len(data) == len(market.ask.data)
    assert data.sum() == 1
    assert data[data == 1].index == 10
    market.ask.data = pd.Series(data=np.arange(len(size)+1, 0, -1))
    condition.update()
    assert condition.data.sum() == 0
    
    
@pytest.mark.run(order=42)
def test_condition_cross_down(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    size = market.ask.data
    market.ask.data = pd.Series(data=range(len(size)))
    condition = ConditionCrossDown(market.ask, 10)
    assert isinstance(condition, ConditionCrossDown)
    condition.update()
    data = condition.data
    assert len(data) == len(market.ask.data)
    assert data.sum() == 0
    market.ask.data = pd.Series(data=np.arange(len(size)+1, 0, -1))
    condition.update()
    assert condition.data.sum() == 1
    
     
@pytest.mark.run(order=43)
def test_action_add_child(market_one_day_path, caplog):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    action = ActionBuy(market=market)
    condition = ConditionUpper(market.ask, 0)
    action.add_child(condition)
    assert len(action.child) == 1
    action.add_child(market.ask)
    assert len(action.child) == 1
    assert "Wrong object type" in caplog.text


@pytest.mark.run(order=44)
def test_action_update(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    action = ActionBuy(market=market)
    condition1 = ConditionUpper(market.ask, 0)
    action.add_child(condition1)
    action.update()
    assert len(action.data) == len(market.ask.data)
    assert len(action.data) == action.data.sum()
    condition2 = ConditionLower(market.ask, 0)
    action.add_child(condition2)
    action.update()
    assert len(action.data) == len(market.ask.data)
    assert action.data.sum() == 0

    
@pytest.mark.run(order=45)
def test_order(market_one_day_path):    
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    order = Order(market=market)
    # test update empty order
    order.update()
    assert len(order.data) == len(market.ask.data)
    assert order.data.sum() == 0
    assert order.action == 0
    
    # test with always buy
    order = Order(market=market)
    action_buy = ActionBuy(market=market)
    condition1 = ConditionUpper(market.ask, 0)
    action_buy.add_child(condition1)
    order.add_child(action_buy)
    order.update()
    assert len(order.data) == len(market.ask.data)
    assert order.data.sum() == len(market.ask.data)
    assert order.action == 1
    
    # test with never sell
    order = Order(market=market)
    action_buy = ActionBuy(market=market)
    condition1 = ConditionUpper(market.ask, 0)
    action_buy.add_child(condition1)
    order.add_child(action_buy)
    action_sell = ActionSell(market=market)
    condition1_sell = ConditionLower(market.ask, 0)
    action_sell.add_child(condition1_sell)
    order.add_child(action_sell)
    order.update()
    assert len(order.data) == len(market.ask.data)
    assert order.data.sum() == len(market.ask.data)
    assert order.action == 1

    # test with always nothing
    order = Order(market=market)
    action_buy = ActionBuy(market=market)
    condition1 = ConditionUpper(market.ask, 0)
    action_buy.add_child(condition1)
    order.add_child(action_buy)
    action_sell2 = ActionSell(market=market)
    condition2_sell = ConditionUpper(market.ask, 0)
    action_sell2.add_child(condition2_sell)
    order.add_child(action_sell2)
    order.update()
    assert len(order.data) == len(market.ask.data)
    assert order.data.sum() == 0
    assert order.action == 0

    # test with always sell
    order = Order(market=market)
    action_sell = ActionSell(market=market)
    condition1_sell = ConditionUpper(market.ask, 0)
    action_sell.add_child(condition1_sell)
    order.add_child(action_sell)
    order.update()
    assert len(order.data) == len(market.ask.data)
    assert order.data.sum() == -len(market.ask.data)
    assert order.action == -1


@pytest.mark.run(order=46)
def test_generate_condition(market_one_day_path, caplog):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    # Test wrong dict
    condition_dict = {"value": 0, "function": "<"}
    condition = generate_condition_from_dict(condition_dict, market=market)
    assert "Invalid dictionary keys" in caplog.text
    assert condition is None
    # test Wrong function
    condition_dict = {"value": 0, "function": "toto", 'property': "EMA_k-12_ask"}
    condition = generate_condition_from_dict(condition_dict, market=market)
    assert condition is None
    assert "Unknown function" in caplog.text
    # test ConditionLower
    condition_dict = {"value": 0, "function": "<", 'property': "EMA_k-12_ask"}
    condition = generate_condition_from_dict(condition_dict, market=market)
    assert isinstance(condition, ConditionLower)
    assert condition.value == 0
    assert condition.parent.name == "EMA_k-12_ask"
    # test ConditionUpper
    condition_dict = {"value": 0, "function": ">", 'property': "EMA_k-12_ask"}
    condition = generate_condition_from_dict(condition_dict, market=market)
    assert isinstance(condition, ConditionUpper)
    assert condition.value == 0
    assert condition.parent.name == "EMA_k-12_ask"
    # test ConditionCrossUp
    condition_dict = {"value": 0, "function": "+=", 'property': "EMA_k-12_ask"}
    condition = generate_condition_from_dict(condition_dict, market=market)
    assert isinstance(condition, ConditionCrossUp)
    assert condition.value == 0
    assert condition.parent.name == "EMA_k-12_ask"
    # test ConditionCrossDown
    condition_dict = {"value": 0, "function": "-=", 'property': "EMA_k-12_ask"}
    condition = generate_condition_from_dict(condition_dict, market=market)
    assert isinstance(condition, ConditionCrossDown)
    assert condition.value == 0
    assert condition.parent.name == "EMA_k-12_ask"


@pytest.mark.run(order=47)
def test_generate_action_from_dict(market_one_day_path, caplog):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    # Test wrong dict
    action_dict = {"type": "sell"}
    action = generate_action_from_dict(action_dict, market)
    assert "Invalid dictionary" in caplog.text
    assert action is None
    # Test wrong type
    action_dict = {"type": "wrong", "conditions": []}
    action = generate_action_from_dict(action_dict, market)
    assert "Unknown action type" in caplog.text
    assert action is None
    # Test wrong conditions
    action_dict = {"type": "buy", "conditions": {}}
    action = generate_action_from_dict(action_dict, market)
    assert "Conditions of action should be a list" in caplog.text
    assert action is None
    # Test good conditions
    action_dict = {"type": "buy", "conditions": [{"value": 0, "function": "+=", 'property': "EMA_k-12_ask"}]}
    action = generate_action_from_dict(action_dict, market)
    assert isinstance(action, ActionBuy)
    condition = action.child[0]
    assert condition.parent.name == "EMA_k-12_ask"


@pytest.mark.run(order=49)
def test_simulate_trading(market_one_day_path, caplog):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.analyse()
    # Do nothing
    result = market.order.simulate_trading(imoney=100, fees=0.1, cost_no_action=-100)
    assert result == (-100, 0, 0)
    # Always buy
    market.order.data = market.order.data.replace(0, 1)
    result = market.order.simulate_trading(imoney=100, fees=0.1, cost_no_action=-100)
    assert result == (-100, 0, 0)
    # one on 2 buy
    market.order.data = market.order.data.replace(1, 0)
    index = list(market.order.data.index)
    market.order.data.iloc[[i for i in range(0, len(index), 4)]] = 1
    market.order.data.iloc[[i for i in range(1, len(index), 4)]] = -1
    result = market.order.simulate_trading(imoney=100, fees=0.1, cost_no_action=-100)
    gain, win, loose = result
    assert gain != 0 and -100 < gain < 100
    assert (win+loose) == int(len(index)/4)
