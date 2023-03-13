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


@pytest.mark.order(1)
def test_read_idconfig(id_config_path):
    assert os.path.isfile(id_config_path)
    assert type(read_file.read_idconfig(id_config_path)) == pd.DataFrame
    assert len(read_file.read_idconfig(id_config_path)) > 0


@pytest.mark.order(2)
def test_read_list_market(market_two_days_list, market_two_days_list_with_dir,
                          market_two_days_list_with_wrong_dir, caplog):
    LOGGER = logging.getLogger(__name__)
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
