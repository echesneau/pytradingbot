"""
Module containing base of API for market connection
"""

# =================
# Python IMPORTS
# =================
import logging
import os.path
import time
from datetime import datetime
from abc import ABC, abstractmethod

import numpy as np
from lxml import etree

# =================
# Internal IMPORTS
# =================
from pytradingbot.cores import markets
from pytradingbot.utils.market_tools import market_from_file
from pytradingbot.utils import math


# =================
# Variables
# =================


class ApiABC(ABC):
    """
    Abstract class of all API
    """

    id_config_path = ""
    id = {}
    session = None
    pair = ""
    symbol = ""
    refresh = 60

    def __init__(self):
        self.id = {}
        self.session = None
        self.odir = None
        self.oformat = "pandas"

    @abstractmethod
    def _set_id(self, user: str):
        """
        set user as id
        Parameters
        ----------
        user: str
        """
        pass

    @abstractmethod
    def connect(self):
        """connection to API"""
        pass

    @abstractmethod
    def get_market(self):
        """get market value"""
        pass

    @abstractmethod
    def _add_child(self):
        """add child"""
        pass

    @abstractmethod
    def update_market(self):
        """update market with onlive value"""
        pass

    @abstractmethod
    def _get_all_child(self):
        """get all child of market"""
        pass

    @abstractmethod
    def analyse(self):
        """analyse market"""
        pass

    @abstractmethod
    def buy(self):
        """buy action"""
        pass

    @abstractmethod
    def sell(self):
        """sell action"""
        pass

    @abstractmethod
    def _get_balance(self):
        pass

    def mymoney(self):
        """
        get your money
        Returns
        -------
        dict: dict with money available
        """
        return self._get_balance()


class BaseApi(ApiABC):
    """
    Base API class, without specific method
    """

    market = None

    def __init__(self, input_path: str = ""):
        """
        Init method

        Parameters
        ----------
        input_path: str
            path of the input config
        """
        super().__init__()
        self.inputs_config_path = input_path
        self.set_config(self.inputs_config_path)

    def _set_id(self):
        """
        method to set id for the connection
        Parameters
        ----------
        user: str
            username
        """
        api_id = {}
        api_id["user"] = os.getenv("API_USER")
        api_id["key"] = os.getenv("API_KEY")
        api_id["private"] = os.getenv("API_PRIVATE")
        self.id = api_id

    def set_config(self, path: str):
        """
        method to read input config file and to set attributes
        Parameters
        ----------
        path: str
            path to inputs config file
        """
        # TODO: add a read function in utils to return a dict
        # Check if path is file
        if not os.path.isfile(path):
            logging.warning(f"{path} is not a file, cannot set input config parameters")
            return

        # XML Parser
        main = etree.parse(path)

        # Output directory
        self.odir = None
        self.oformat = "pandas"
        for node in main.xpath("/pytradingbot/market/odir"):
            self.odir = node.text
            if "format" in node.attrib and node.attrib["format"] in ["pandas"]:
                self.oformat = node.attrib["format"]
            else:
                logging.warning(
                    f"{node.attrib['format']} is not a good value: "
                    f"set by default to pandas"
                )
                self.oformat = "pandas"
        # Symbol
        for node in main.xpath("/pytradingbot/trading/symbol"):
            self.symbol = node.text

        # Pair
        for node in main.xpath("/pytradingbot/trading/pair"):
            self.pair = node.text

        # Refresh time
        for node in main.xpath("/pytradingbot/trading/refresh"):
            try:
                self.refresh = float(node.text)
            except ValueError:
                logging.warning(
                    f"Refresh time read {node.text} is not a float. "
                    f"Set to default value {self.refresh}"
                )

    def connect(self):
        """
        connection to the API
        """
        pass

    def set_market(self, obj: markets.Market):
        """
        method to set a market as attribute
        Parameters
        ----------
        obj: Market Class
        """
        self.market = obj

    def run(self, times: int = np.inf):
        """
        method to run the analysis of market in real time

        Parameters
        ----------
        times: int
            number of iterations
        """
        # Init Market
        self.set_market(
            markets.Market(
                parent=self, odir=f"{self.odir}/{self.pair}", oformat=self.oformat
            )
        )
        self.market.generate_property_from_xml_config(self.inputs_config_path)
        self.market.generate_order_from_xml_config(self.inputs_config_path)

        # Init counter
        count = 0
        tstart = datetime.now()
        # start run
        while count < times:
            count += 1
            init_time = datetime.now()
            self.update_market()
            self.analyse()
            action = self.market.action
            if action == 1:
                self.buy()
            elif action == -1:
                self.sell()
            self.market.save()
            self.market.clean()
            final_time = datetime.now()
            print(
                f"count={count}: {final_time-init_time}s, (mean={(final_time-tstart)/count})",
                end="\r",
            )
            wait = self.refresh - (final_time - init_time).total_seconds()
            if wait > 0:
                time.sleep(self.refresh)

    def get_market(self):
        pass

    def _add_child(self):
        pass

    def update_market(self):
        """
        method to update the market
        """
        self.market.update()

    def _get_all_child(self):
        pass

    def analyse(self):
        """Method to analyse the market"""
        self.market.analyse()

    def calculate_quantity_buy(self, price: float):
        """Method to calculate quantity to buy in function of a price"""
        precision = 5
        money = self.mymoney
        qtt = math.floor(money / price, precision=precision)
        return qtt

    def buy(self, quantity, price):
        pass

    def sell(self, quantity, price):
        pass

    def _get_balance(self):
        pass

    @property
    def balance(self) -> dict:
        return self._get_balance()

    @property
    def mymoney(self) -> float:
        """
        Method to get your balance
        """
        return self.balance["ZEUR"]


class APILoadData(BaseApi):
    """
    API Class to load data
    """

    def __init__(self, data_file: str = None, fmt: str = "csv"):
        super().__init__()
        self.market = market_from_file(data_file, fmt=fmt)
        for market in self.market:
            market.add_parent("api", self)
