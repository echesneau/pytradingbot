# =================
# Python IMPORTS
# =================
import logging
import krakenex
from datetime import datetime
import requests.exceptions
from time import sleep

# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.base import BaseApi

# =================
# Variables
# =================


class KrakenApi(BaseApi):
    def __int__(self, inputs=""):
        super().__init__(inputs=inputs)

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

    def _query_market(self, timeout=5):
        query = self.session.query_public('Ticker', {'pair': self.pair}, timeout=timeout)
        values = {"ask": float(query['result'][self.pair]['a'][0]),
                  'bid': float(query['result'][self.pair]['b'][0])
                  }
        return values

    def _get_market(self):
        test = True
        failed = 0
        while test:
            if failed > 0 and failed % 5 == 0:
                self.connect()
            if failed > 0 and failed % 10 == 0:
                sleep(10)
            try:
                values = self._query_market()
                test = False
            except requests.exceptions.ConnectionError:
                if failed == 0:
                    logging.warning(f"Connexion problem at {datetime.now()}")
                failed += 1
        if failed > 0:
            logging.warning(f"Problem solved at {datetime.now()} after {failed} test(s)")
        return values


class KrakenApiDev(KrakenApi):
    def __init__(self, user='', inputs=""):
        super().__init__(inputs=inputs)
        self._set_id(user)


class CryptoEmptyLoad:
    pass
