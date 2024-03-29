"""
Module containing API for crypto trading
"""
# =================
# Python IMPORTS
# =================
import logging
from datetime import datetime
from time import sleep
import requests.exceptions
import krakenex

# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.base import BaseApi

# =================
# Variables
# =================


class KrakenApi(BaseApi):
    """
    API for Kraken
    """
    def __int__(self, input_path: str = ""):
        super().__init__(input_path=input_path)

    def connect(self):
        """
        connection to the API
        """
        if len(self.id) == 0:
            users = self._get_user_list()
            if users.shape[0] == 0:
                logging.error("No user read in the id.config")
            myuser = ""
            while myuser not in users:
                myuser = input("User: ")
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

    def _query_market(self, timeout: int = 5) -> dict:
        """
        Method to query the Kraken market

        Parameters
        ----------
        timeout: int
            maximum time for the query

        Returns
        -------
            dict: with market value

        """
        query = self.session.query_public('Ticker', {'pair': self.pair}, timeout=timeout)
        values = {"ask": float(query['result'][self.pair]['a'][0]),
                  'bid': float(query['result'][self.pair]['b'][0]),
                  'volume': float(query['result'][self.pair]['v'][0]),
                  'time': datetime.now()
                  }
        return values

    def get_market(self) -> dict:
        """
        Method to get market value

        Returns
        -------
            dict: with market value
        """
        test = True
        failed = 0
        values = {}
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
            except requests.exceptions.ReadTimeout:
                if failed == 0:
                    logging.warning(f"Timeout error at {datetime.now()}")
                failed += 1
            except requests.exceptions.HTTPError:
                if failed == 0:
                    logging.warning(f"HTTP error at {datetime.now()}")
                failed += 1
        if failed > 0:
            logging.warning(f"Problem solved at {datetime.now()} after {failed} test(s)")
        return values


class KrakenApiDev(KrakenApi):
    """
        API for Kraken in development mode (user defines in argument)
    """
    def __init__(self, user: str = '', input_path: str = ""):
        """

        Parameters
        ----------
        user: str
            username
        input_path: str
            input config path
        """
        super().__init__(input_path=input_path)
        self._set_id(user)


class CryptoEmptyLoad:
    """
    to be defined
    """
    pass
