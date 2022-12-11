# =================
# Python IMPORTS
# =================
import importlib
# importlib.reload(nameOfModule)
# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.crypto_api import KrakenApiDev
#importlib.reload(crypto_api)
# =================
# Variables
# =================
USER = "erwan"

API = KrakenApiDev()
print(API.id)
API.connect()


if __name__ == '__name__':

    pass
