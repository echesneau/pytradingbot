# =================
# Python IMPORTS
# =================
import pytest
from importlib import resources

# =================
# Internal IMPORTS
# =================

# =================
# Variables
# =================


@pytest.fixture()
def id_config_path():
    dirname = resources.files("pytradingbot")  # return the path of the file id.config of the module tradingbot
    return f"{dirname}/id.config"


@pytest.fixture()
def kraken_user():
    return 'erwan'


@pytest.fixture()
def inputs_config_path():
    return 'data/config.xml'


@pytest.fixture()
def df_market_test():
    # lire un fichier pkl market
    pass
