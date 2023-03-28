# =================
# Python IMPORTS
# =================
import pytest
import numpy as np

# =================
# Internal IMPORTS
# =================
from pytradingbot.utils.market_tools import market_from_file
from pytradingbot.cores.orders import ConditionUpper, ConditionLower, ConditionCrossUp, ConditionCrossDown


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
    condition = ConditionCrossUp()


if __name__ == "__main__":
    market_one_day_path = 'data/XXBTZEUR_1day.dat'
    test_condition_cross_up(market_one_day_path)