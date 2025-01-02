# =================
# Python IMPORTS
# =================
import os

import pytest
import numpy as np
# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.base import BaseApi, APILoadData

# =================
# Variables
# =================


@pytest.mark.run(order=6)
def test_base_api(inputs_config_path):
    api = BaseApi(input_path=inputs_config_path)

    # ID check
    api._set_id()
    assert type(api.id) == dict
    for value in ['user', 'private', 'key']:
        assert value in api.id.keys()
    variables = {
        "API_USER": os.getenv('API_USER'),
        "API_KEY": os.getenv('API_KEY'),
        "API_PRIVATE": os.getenv('API_PRIVATE')
    }
    for name, value in variables.items():
        assert (value is not None) and (value != ''), f"La variable {name} est manquante ou vide."

    # read inputs XML config
    api.set_config(inputs_config_path)
    assert hasattr(api, 'pair')
    assert api.pair == "XXBTZEUR"

    assert hasattr(api, 'symbol')
    assert api.symbol == "XXBT"

    assert hasattr(api, 'refresh')
    assert api.refresh == 5

    assert hasattr(api, 'odir')
    assert api.odir == 'data/outputs/market'

    assert hasattr(api, 'oformat')
    assert api.oformat == 'pandas'


@pytest.mark.run(order=6)
def test_APILoadData(market_one_day_path):
    api = APILoadData(market_one_day_path, fmt='csv')
    assert len(api.market) == 1
    assert api.market[0].parents['api'] == api
