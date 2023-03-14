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

ROOT_DIR = os.path.dirname(__file__)

@pytest.fixture()
def id_config_path():
    root_dir = os.path.dirname(__file__)
    return f"{root_dir}/../id.config"


@pytest.fixture()
def kraken_user():
    return 'erwan'


@pytest.fixture()
def inputs_config_path():
    return f'{ROOT_DIR}/data/config.xml'


@pytest.fixture()
def market_one_day_path():
    return f'{ROOT_DIR}/data/XXBTZEUR_1day.dat'


@pytest.fixture()
def market_one_day_missing_volume_col_path():
    return f'{ROOT_DIR}/data/XXBTZEUR_1day_missing_volume_col.dat'


@pytest.fixture()
def market_two_days_path():
    return f'{ROOT_DIR}/data/XXBTZEUR_2days.dat'


@pytest.fixture()
def market_two_days_list():
    return f'{ROOT_DIR}/data/XXBTZEUR_2days.list'


@pytest.fixture()
def market_two_days_list_with_dir():
    return f'{ROOT_DIR}/data/XXBTZEUR_2days_dir.list'


@pytest.fixture()
def market_two_days_list_with_wrong_dir():
    return f'{ROOT_DIR}/data/XXBTZEUR_2days_wrong-dir.list'


@pytest.fixture()
def market_two_days_missingdata_path():
    return f'{ROOT_DIR}/data/XXBTZEUR_2days_datamissing.dat'


@pytest.fixture()
def df_market_test():
    # TODO: read a pkl market file
    pass
