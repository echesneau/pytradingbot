import pytest
from pytradingbot.utils import math


@pytest.mark.run(order=29)
def test_floor_function():
    value = 2.64321
    assert math.floor(value) == 2
    assert math.floor(value, precision=2) == 2.64
    assert math.floor(value, precision=20) == 2.64321


@pytest.mark.run(order=29)
def test_ceil_function():
    value = 2.64321
    assert math.ceil(value) == 3
    assert math.ceil(value, precision=2) == 2.65
    assert math.ceil(value, precision=20) == 2.64321
