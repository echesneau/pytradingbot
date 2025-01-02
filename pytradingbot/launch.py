"""A launch script for pytradingbot in production mode"""

# =================
# Python IMPORTS
# =================

# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.crypto_api import KrakenApi

# =================
# Variables
CONFIG = "data/inputs/config.xml"

API = KrakenApi(input_path=CONFIG)
API.connect()

if __name__ == "__name__":
    pass
