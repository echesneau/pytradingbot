# =================
# Python IMPORTS
# =================
import pytest
import numpy as np
# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.base import BaseApi

# =================
# Variables
# =================


@pytest.mark.order(2)
def test_base_api(id_config_path, kraken_user, inputs_config_path):
    api = BaseApi(inputs=inputs_config_path)

    # get users list
    assert type(api._get_user_list()) is np.ndarray
    dim = api._get_user_list().shape
    assert len(dim) in [1, 2]
    if len(dim) == 2:
        assert dim[1] == 1
    assert dim[0] > 0

    # ID check
    api._set_id(kraken_user)
    assert type(api.id) == dict
    for value in ['user', 'private', 'key']:
        assert value in api.id.keys()
    assert api.id['user'] == kraken_user

    # read inputs XML config
    api.set_config(inputs_config_path)
    assert hasattr(api, 'pair')
    assert api.pair == "XXBTZEUR"

    assert hasattr(api, 'symbol')
    assert api.symbol == "XXBT"

    assert hasattr(api, 'refresh')
    assert api.refresh == 5
