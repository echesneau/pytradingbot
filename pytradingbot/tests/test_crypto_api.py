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

    # api = KrakenApiDev(user=kraken_user)
    # api.connect()
    # print(api.session)
