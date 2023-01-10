# =================
# Python IMPORTS
# =================
import logging
import os.path
import time
from datetime import datetime
from abc import ABC, abstractmethod
from importlib import resources

import numpy as np
from lxml import etree

# =================
# Internal IMPORTS
# =================
from pytradingbot.utils import read_file
from pytradingbot.cores import markets


# =================
# Variables
# =================


class ApiABC(ABC):
    id_config_path = ""
    id = {}
    session = None
    pair = ""
    symbol = ""
    refresh = 60

    def __init__(self):
        self.id_config_path = f"{resources.files('pytradingbot')}/id.config"
        self.id = {}
        self.session = None
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
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_market(self):
        pass

    @abstractmethod
    def _add_child(self):
        pass

    @abstractmethod
    def update_market(self):
        pass

    @abstractmethod
    def _get_all_child(self):
        pass

    @abstractmethod
    def analyse(self):
        pass

    @abstractmethod
    def buy(self):
        pass

    @abstractmethod
    def sell(self):
        pass

    @abstractmethod
    def _get_balance(self):
        pass

    @property
    def mymoney(self):
        return self._get_balance()


class BaseApi(ApiABC):
    market = None

    def __init__(self, inputs=""):
        super().__init__()
        self.inputs_config_path = inputs
        self.set_config(self.inputs_config_path)

    def _get_user_list(self):
        id_config = read_file.read_idconfig(self.id_config_path)
        return id_config['user'].values

    def _set_id(self, user):
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

    def set_config(self, path):
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
            if "format" in node.attrib and \
                node.attrib['format'] in ['pandas']:
                self.oformat = node.attrib['format']
            else:
                logging.warning(f"{node.attrib['format']} is not a good value: set by default to pandas")
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
                logging.warning(f"Refresh time read {node.text} is not a float. Set to default value {self.refresh}")

    def connect(self):
        pass

    def set_market(self, obj: markets.Market):
        self.market = obj

    def run(self, times=np.inf):
        # Init Market
        self.set_market(markets.Market(parent=self, odir=self.odir))

        # Init counter
        count = 0

        # start run
        while count < times:
            t0 = datetime.now()
            self.update_market()
            self.analyse()
            tf = datetime.now()
            wait = self.refresh - (tf - t0).total_seconds()
            if wait > 0:
                time.sleep(self.refresh)
            count += 1

    def get_market(self):
        pass

    def _add_child(self):
        pass

    def update_market(self):
        self.market.update()

    def _get_all_child(self):
        pass

    def analyse(self):
        pass

    def buy(self):
        pass

    def sell(self):
        pass

    def _get_balance(self):
        pass

    def mymoney(self):
        return self._get_balance()

    pass
