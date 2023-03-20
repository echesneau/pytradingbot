# =================
# Python IMPORTS
# =================
import os
import pytest
import pandas as pd

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


def test_read_analysis_properties(inputs_config_path, caplog):
    # test is not a file
    properties = read_file.read_input_analysis_config('toto')
    assert len(properties) == 0
    assert "is not a file" in caplog.text
    caplog.clear()
    properties = read_file.read_input_analysis_config(inputs_config_path)
    assert len(properties) == 3
    assert "Unknown property format" in caplog.text
