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

    def _get_balance(self) -> dict:
        """
        Method to request balance of Kraken account
        Returns
        -------
        dict: balance: keys: symbol, value: quantity
        """
        result = self.session.query_private("Balance")
        if len(result["error"]) > 0:
            print(f"Warning: error getting balance. \n{';'.join(result['error'])}")
            balance = {"ZEUR": 0}
        else:
            balance = result["result"]
        balance = {key: float(value) for key, value in balance.items()}
        return balance

    def buy(self, quantity: float, price: float):
        pass

    def sell(self, quantity: float, price: float):
        pass

    def cancel_order_by_id(self, order_id: str):
        pass

    def _get_open_orders(self) -> dict:
        """
        Method to get all opened orders and format results in JSON

        Returns
        -------
        dict: JSON stucture: json[order_type][pair] = [list of id]
        """
        out = {"buy": {}, "sell": {}}
        result = self.session.query_private("OpenOrders")
        if len(result["error"]) > 0:
            print(
                f"Warning: error getting opened orders. \n{';'.join(result['error'])}"
            )
            opened_orders = {}
        else:
            opened_orders = result["result"]["open"]
        for order_id, order_info in opened_orders.items():
            order_descr = order_info["descr"]
            order_type = order_descr["type"]
            order_pair = order_descr["pair"]
            if order_type not in out:
                out[order_type] = {}
            if order_pair not in out[order_type]:
                out[order_type][order_pair] = []
            out[order_type][order_pair] += [order_id]
        return out

    def open_orders(self, type: str = None, pair: str = None) -> list:
        """
        Method to return list of order's ids opened. Could be filtered by type (sell or buy) and by symbol.

        Parameters
        ----------
        type: str
            type of order: sell or buy. If None: return both
        pair: str
            pair in order. (XXBTZEUR for example). If None: return all pair

        Returns
        -------
        list of id
        """
        ids = []
        open_orders = self._get_open_orders()
        # filtering on type
        order_types = [type] if type is not None else list(open_orders.keys())
        for o_type in order_types:
            if o_type not in open_orders:
                continue
            # Filtering on pair
            pairs = [pair] if pair is not None else list(open_orders[o_type].keys())
            for p in pairs:
                if p not in open_orders[o_type]:
                    continue
                ids += open_orders[o_type][p]
        return ids


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
            balance = self.balance_dict
            return self.balance_dict
        else:
            balance = pd.read_csv(self.balance_path, sep=";", index_col="name").squeeze(
                axis=1
            )
            balance = balance.to_dict()
        balance = {key: float(value) for key, value in balance.items()}
        return balance


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
