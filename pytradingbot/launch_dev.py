# =================
# Python IMPORTS
# =================

# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.crypto_api import KrakenApiDev

# =================
# Variables
# =================
USER = "erwan"
CONFIG = 'data/inputs/config.xml'

API = KrakenApiDev(user='erwan', input_path=CONFIG)
API.connect()
API.get_market()


if __name__ == '__name__':
    pass
