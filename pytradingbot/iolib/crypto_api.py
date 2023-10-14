"""
Module containing API for crypto trading
"""
# =================
# Python IMPORTS
# =================
import os
import logging
from datetime import datetime
from time import sleep
import requests.exceptions
import krakenex
import pandas as pd

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
    def __init__(self, user: str = '', input_path: str = "", imoney: float = 100, balance_path: str = None):
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
        self.balance_path = balance_path
        if balance_path is None:
            self.money = imoney
            self.balance = {}
        elif not os.path.isfile(balance_path):
            raise FileNotFoundError(f"Balance file {balance_path} is not a file")


    @property
    def mymoney(self):
        if self.balance_path is None:
            return self.money
        else:
            balance = pd.read_csv(self.balance_path, sep=";", index_col='name').squeeze(axis=1)
            balance = balance.to_dict()
            return balance['EUR']


    def buy(self, quantity, price):
        tot_price = quantity * price
        if self.balance_path is None:
            self.money -= tot_price
            if self.pair not in self.balance.keys():
                self.balance[self.pair] = quantity
            else:
                self.balance[self.pair] += quantity
        else:
            balance = pd.read_csv(self.balance_path, sep=";", index_col='name').squeeze(axis=1).to_dict()
            balance['EUR'] -= tot_price
            if self.pair in balance.keys():
                balance[self.pair] += quantity
            else:
                balance[self.pair] = quantity
            tmp = pd.Series(balance).to_frame().reset_index()
            tmp.columns = ['name', 'quantity']
            tmp.to_csv(self.balance_path, sep=';', index=False)


class CryptoEmptyLoad:
    """
    to be defined
    """
    pass
