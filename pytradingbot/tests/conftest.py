"""test configuration"""

# =================
# Python IMPORTS
# =================
import os.path
import pytest


# =================
# Internal IMPORTS
# =================

# =================
# Variables
# =================

ROOT_DIR = os.path.dirname(__file__)


@pytest.fixture()
def inputs_config_path():
    return f"{ROOT_DIR}/data/config.xml"


@pytest.fixture()
def balance_path():
    return f"{ROOT_DIR}/data/balance_test.csv"


@pytest.fixture()
def market_one_day_path():

    return f"{ROOT_DIR}/data/XXBTZEUR_1day.dat"


@pytest.fixture()
def market_one_day_missing_volume_col_path():
    """market without volume column"""
    return f"{ROOT_DIR}/data/XXBTZEUR_1day_missing_volume_col.dat"


@pytest.fixture()
def market_two_days_path():
    """Two days market csv"""
    return f"{ROOT_DIR}/data/XXBTZEUR_2days.dat"


@pytest.fixture()
def market_two_days_list():
    """List of market"""
    return f"{ROOT_DIR}/data/XXBTZEUR_2days.list"


@pytest.fixture()
def market_two_days_list_with_dir():
    """Two days market with data read in directory"""
    return f"{ROOT_DIR}/data/XXBTZEUR_2days_dir.list"


@pytest.fixture()
def market_two_days_list_with_wrong_dir():
    """Two days marking with wrong directory"""
    return f"{ROOT_DIR}/data/XXBTZEUR_2days_wrong-dir.list"


@pytest.fixture()
def market_two_days_missingdata_path():
    """two days market data with a mistake to test functions"""
    return f"{ROOT_DIR}/data/XXBTZEUR_2days_datamissing.dat"


@pytest.fixture()
def df_market_test():
    # TODO: read a pkl market file
    pass
