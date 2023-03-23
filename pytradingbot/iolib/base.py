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
from pytradingbot.utils import read_file
from pytradingbot.cores import markets
from pytradingbot.utils.market_tools import market_from_file


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
        root_dir = os.path.dirname(__file__)
        self.id_config_path = f"{root_dir}/../id.config"
        self.id = {}
        self.session = None
        self.odir = None
        self.oformat = 'pandas'
        # if not id_config is None and user != "":
        #     self.user = user
        #     self.id = id_config.loc[id_config['user'] == user]
        # print(id_config)

        # else:
        #     self.id = read_file.read_idconfig(id_config)
        # self.parent = []
        # self.child = []
        # self.money = 0
        # self.session = None

    @abstractmethod
    def _set_id(self, user):
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

    def __init__(self, inputs=""):
        """
        Init method

        Parameters
        ----------
        inputs: str
            path of the input config
        """
        super().__init__()
        self.inputs_config_path = inputs
        self.set_config(self.inputs_config_path)

    def _get_user_list(self):
        """
        method to get available user name
        Returns
            list: list of users
        -------

        """
        id_config = read_file.read_idconfig(self.id_config_path)
        return id_config['user'].values

    def _set_id(self, user: str):
        """
        method to set id for the connection
        Parameters
        ----------
        user: str
            username
        """
        id_config = read_file.read_idconfig(self.id_config_path)
        if id_config is None:
            self.id = {}
        else:
            ids = id_config.loc[id_config['user'] == user]
            if len(ids) == 0:
                logging.warning(f"No user found with name {user}")
                self.id = {}
            else:
                ids = ids.to_dict('records')
                if len(ids) > 1:
                    logging.warning(f"More than one user found with name {user}. First is selected")
                self.id = ids[0]

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
        self.oformat = 'pandas'
        for node in main.xpath("/pytradingbot/market/odir"):
            self.odir = node.text
            if "format" in node.attrib and node.attrib['format'] in ['pandas']:
                self.oformat = node.attrib['format']
            else:
                logging.warning(f"{node.attrib['format']} is not a good value: "
                                f"set by default to pandas")
                self.oformat = 'pandas'
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
                logging.warning(f"Refresh time read {node.text} is not a float. "
                                f"Set to default value {self.refresh}")

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
        self.set_market(markets.Market(parent=self, odir=f"{self.odir}/{self.pair}",
                                       oformat=self.oformat))
        self.market.generate_property_from_xml_config(self.inputs_config_path)

        # Init counter
        count = 0
        tstart = datetime.now()
        # start run
        while count < times:
            count += 1
            init_time = datetime.now()
            self.update_market()
            self.analyse()
            self.market.save()
            self.market.clean()
            final_time = datetime.now()
            print(f"{count=}: {final_time-init_time}s, (mean={(final_time-tstart)/count})", end="\r")
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
        self.market.analyse()

    def buy(self):
        pass

    def sell(self):
        pass

    def _get_balance(self):
        pass

    def mymoney(self):
        """
        Method to get your balance
        """
        return self._get_balance()


class APILoadData(BaseApi):
    """
    API Class to load data
    """
    def __init__(self, data_file: str = None, fmt: str = 'csv'):
        super().__init__()
        self.market = market_from_file(data_file, fmt=fmt)
        for market in self.market:
            market.add_parent('api', self)
