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
        self._set_id()
        test = True
        while test:
            try:
                self.session = krakenex.API(
                    key=self.id["key"], secret=self.id["private"]
                )
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
        query = self.session.query_public(
            "Ticker", {"pair": self.pair}, timeout=timeout
        )
        values = {
            "ask": float(query["result"][self.pair]["a"][0]),
            "bid": float(query["result"][self.pair]["b"][0]),
            "volume": float(query["result"][self.pair]["v"][0]),
            "time": datetime.now(),
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
            logging.warning(
                f"Problem solved at {datetime.now()} after {failed} test(s)"
            )
        return values


class KrakenApiDev(KrakenApi):
    """
    API for Kraken in development mode (user defines in argument)
    """

    def __init__(
        self, input_path: str = "", imoney: float = 0, balance_path: str = None
    ):
        """

        Parameters
        ----------
        input_path: str
            input config path
        """
        super().__init__(input_path=input_path)
        self._set_id()
        self.balance_path = balance_path
        if balance_path is None:
            self.balance_dict = {"ZEUR": imoney}
        elif not os.path.isfile(balance_path):
            raise FileNotFoundError(f"Balance file {balance_path} is not a file")

    def _get_balance(self):
        if self.balance_path is None:
            return self.balance_dict
        else:
            balance = pd.read_csv(self.balance_path, sep=";", index_col="name").squeeze(
                axis=1
            )
            return balance.to_dict()

    def buy(self, quantity, price):
        tot_price = quantity * price
        if self.balance_path is None:
            self.balance_dict["ZEUR"] -= tot_price
            if self.pair not in self.balance_dict:
                self.balance_dict[self.pair] = quantity
            else:
                self.balance_dict[self.pair] += quantity
        else:
            balance = self.balance
            balance["ZEUR"] -= tot_price
            if self.pair in balance.keys():
                balance[self.pair] += quantity
            else:
                balance[self.pair] = quantity
            tmp = pd.Series(balance).to_frame().reset_index()
            tmp.columns = ["name", "quantity"]
            tmp.to_csv(self.balance_path, sep=";", index=False)

    def sell(self, quantity, price):
        if self.balance_path is None:
            quantity = min(quantity, self.balance[self.pair])
            self.balance_dict["ZEUR"] += quantity * price
            self.balance_dict[self.pair] -= quantity
        else:
            balance = self.balance
            quantity = min(quantity, balance[self.pair])
            if quantity > balance[self.pair]:
                quantity = balance[self.pair]
            balance["ZEUR"] += quantity * price
            balance[self.pair] -= quantity
            tmp = pd.Series(balance).to_frame().reset_index()
            tmp.columns = ["name", "quantity"]
            tmp.to_csv(self.balance_path, sep=";", index=False)


class CryptoEmptyLoad:
    """
    to be defined
    """

    pass
