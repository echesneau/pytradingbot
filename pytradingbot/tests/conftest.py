# =================
# Python IMPORTS
# =================
import pytest
import os.path

# =================
# Internal IMPORTS
# =================

# =================
# Variables
# =================


@pytest.fixture()
def id_config_path():
    root_dir = os.path.dirname(__file__)
    return f"{root_dir}/../id.config"


@pytest.fixture()
def kraken_user():
    return 'erwan'


@pytest.fixture()
def inputs_config_path():
    return 'data/config.xml'


@pytest.fixture()
def market_one_day_path():
    return 'data/XXBTZEUR_1day.dat'


@pytest.fixture()
def market_two_days_path():
    return 'data/XXBTZEUR_2days.dat'


@pytest.fixture()
def market_two_days_list():
    return 'data/XXBTZEUR_2days.list'


@pytest.fixture()
def market_two_days_missingdata_path():
    return 'data/XXBTZEUR_2days_datamissing.dat'


@pytest.fixture()
def df_market_test():
    # TODO: read a pkl market file
    pass
