# =================
# Python IMPORTS
# =================
import pytest
import krakenex
# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.crypto_api import KrakenApi, KrakenApiDev

# =================
# Variables
# =================


@pytest.mark.order(3)
def test_connect(kraken_user):
    api = KrakenApi()
    api._set_id(kraken_user)
    api.connect()
    assert type(api.session) is krakenex.api.API

    api = KrakenApiDev(user=kraken_user)
    api.connect()
    assert type(api.session) is krakenex.api.API

@pytest.mark.order(4)
def test_get_market(kraken_user, inputs_config_path):
    api = KrakenApiDev(user=kraken_user, inputs=inputs_config_path)
    api.connect()
    values = api._get_market()
    for key in ['bid', 'ask']:
        assert key in values.keys()
        assert type(values[key]) == float