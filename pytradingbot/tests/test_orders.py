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
from pytradingbot.cores.orders import ConditionUpper, ConditionLower, ConditionCrossUp, ConditionCrossDown, ActionBuy, ActionSell, Order


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
    data = condition.data
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
    
    # test with always buy
    action_buy = ActionBuy(market=market)
    condition1 = ConditionUpper(market.ask, 0)
    action_buy.add_child(condition1)
    order.add_child(action_buy) 
    order.update()
    assert  len(order.data) == len(market.ask.data)
    assert order.data.sum() == len(market.ask.data)
    
    # test with never sell
    action_sell =ActionSell(market=market)
    condition1_sell = ConditionLower(market.ask, 0)
    action_sell.add_child(condition1_sell)
    order.add_child(action_sell)
    order.update()
    assert  len(order.data) == len(market.ask.data)
    assert order.data.sum() == len(market.ask.data)
    

if __name__ == "__main__":
    market_one_day_path = 'data/XXBTZEUR_1day.dat'
    test_order(market_one_day_path)
    