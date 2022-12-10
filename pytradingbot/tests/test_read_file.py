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
