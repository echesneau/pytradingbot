# =================
# Python IMPORTS
# =================
import logging
import os.path
from abc import ABC, abstractmethod
from importlib import resources
from lxml import etree

# =================
# Internal IMPORTS
# =================
from pytradingbot.utils import read_file

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
    def _get_market(self):
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
        # Check if path is file
        if not os.path.isfile(path):
            logging.warning(f"{path} is not a file, cannot set input config parameters")
            return

        # XML Parser
        main = etree.parse(path)

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

    def _get_market(self):
        pass

    def _add_child(self):
        pass

    def update_market(self):
        pass

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
