# =================
# Python IMPORTS
# =================
import logging
import krakenex

# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.base import BaseApi

# =================
# Variables
# =================


class KrakenApi(BaseApi):
    def __int__(self):
        super().__init__()

    def connect(self):
        if len(self.id) == 0:
            users = self._get_user_list()
            if users.shape[0] == 0:
                logging.error(f"No user read in the id.config")
            myuser = ""
            while myuser not in users:
                myuser = input(f"User: ")
                if myuser not in users:
                    print(f"{myuser} is not in the id.config")
            self._set_id(myuser)
        test = True
        while test:
            try:
                self.session = krakenex.API(key=self.id['key'],
                                            secret=self.id['private'])
                test = False
            except:
                pass


class KrakenApiDev(KrakenApi):
    def __init__(self, user=''):
        super().__init__()
        self._set_id(user)


class CryptoEmptyLoad:
    pass
