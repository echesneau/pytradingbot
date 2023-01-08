# =================
# Python IMPORTS
# =================
import pytest
# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.crypto_api import KrakenApi, KrakenApiDev

# =================
# Variables
# =================

def test_update(kraken_user, inputs_config_path):
    api = KrakenApiDev(user=kraken_user, inputs=inputs_config_path)
    
    assert False


def test_analyse():
    assert False
