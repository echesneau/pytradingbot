# =================
# Python IMPORTS
# =================
import os
import pytest
import pandas as pd
import logging

# =================
# Internal IMPORTS
# =================
from pytradingbot.utils import read_file

# =================
# Variables
# =================


@pytest.mark.run(order=2)
def test_read_analysis_properties(inputs_config_path, caplog):
    # test is not a file
    properties = read_file.read_input_analysis_config('toto')
    assert len(properties) == 0
    assert "is not a file" in caplog.text
    caplog.clear()
    properties = read_file.read_input_analysis_config(inputs_config_path)
    assert len(properties) == 4
    assert "Unknown property format" in caplog.text


@pytest.mark.run(order=3)
def test_read_action_config(inputs_config_path, caplog):
    # test is not a file
    actions = read_file.read_input_order_config('toto')
    assert len(actions) == 0
    assert "is not a file" in caplog.text
    caplog.clear()
    actions = read_file.read_input_order_config(inputs_config_path)
    assert "Unknown type" in caplog.text
    assert "Unknown function" in caplog.text
    assert len(actions) == 1
    action = actions[0]
    assert action['type'] in ['buy', "sell"]
    assert len(action['conditions']) == 2
    for condition in action['conditions']:
        assert "value" in condition
        assert isinstance(condition['value'], float)
        assert 'function' in condition
        assert condition['function'] in ['<', ">", '+=', '-=']
        assert isinstance(condition['property'], str)

@pytest.mark.run(order=3)
def test_read_csv_market(market_one_day_path, caplog):
    df = read_file.read_csv_market(market_one_day_path)
    assert type(df) == pd.DataFrame
    assert len(df) > 0

    # test wrong path
    df = read_file.read_csv_market('toto')
    assert df is None
    assert "is not a file" in caplog.text


@pytest.mark.run(order=4)
def test_read_list_market(market_two_days_list, market_two_days_list_with_dir,
                          market_two_days_list_with_wrong_dir, caplog):
    df = read_file.read_list_market(market_two_days_list)
    assert len(df) > 0
    delta = df.index[-1] - df.index[0]
    assert delta.ceil('D').days == 2
    df = read_file.read_list_market(market_two_days_list_with_dir)
    assert len(df) > 0
    delta = df.index[-1] - df.index[0]
    assert delta.ceil('D').days == 2
    df = read_file.read_list_market(market_two_days_list_with_wrong_dir)
    assert len(df) == 0
    assert "is not a directory" in caplog.text
    assert "is not a file" in caplog.text
    caplog.clear()
    df = read_file.read_list_market('toto')
    assert df is None
    assert "market is not loaded" in caplog.text
