# =================
# Python IMPORTS
# =================
import logging
from typing import Dict, Any
import pandas as pd
from abc import ABC

# =================
# Internal IMPORTS
# =================
from pytradingbot.properties_functions import functions

# =================
# Variables
# =================


class PropertiesABC(ABC):
    """
    Abstract class for properties
    """
    type = ""

    def __init__(self, parent=None,
                 market: object = None,
                 param: Dict[str, Any] = None):

        self.child = []
        self.data = pd.Series()

        self.parents: Dict[str, object] = {}
        if type(parent) == dict:
            self.parents = parent
        # elif parent is not None and type(type(parent)) == type:  # Check is parent is an object created from a class
        if parent is not None:
            self.add_parent('data', parent)
        # elif parent is not None:
        #     logging.warning(f"type of {parent} is unexpected, skipped")

        if market is not None:  # TODO: check is market is an object with upper class Market
            self.add_parent('market', market)

        self.param: Dict[str, Any] = {}
        if type(param) is dict:
            self.param = param
        elif param is not None:
            logging.warning(f"type of {param} is unexpected, skipped")

        self.name = f"{self.type}"
        self.data = self.data.rename(self.name)

    def __call__(self, *args, **kwargs):
        return self.data

    def _function(self):
        pass

    def update(self):
        """
        Update values of the properties in function of parent values
        """
        # Check if an update is needed
        update = False
        if len(self.parents) > 0:
            if 'data' in self.parents and len(self.parents['data'].data) > len(self.data):
                update = True
            elif 'market' in self.parents and len(self.parents['market'].ask.data) > len(self.data):
                update = True

        # update data
        if update:
            self.data = self._function()

    def add_parent(self, name, obj):
        """
        Method to add a parent

        Parameters
        ----------
        name: str
            key of parent in the dict
        obj: parent object
        """
        self.parents[name] = obj

    def add_child(self, obj):
        """
        Method to add a child

        Parameters
        ----------
        obj: child object
        """
        if obj not in self.child:
            self.child.append(obj)

    def clean(self, nrows: int = 0):
        """
        Method to clean data
        Parameters
        ----------
        nrows: int
            maximum number of rows in the pd.Series
        """
        if len(self.data) > nrows:
            self.data = self.data.iloc[-nrows-1:]


class Ask(PropertiesABC):
    """
    Ask value of the market
    """
    type = "market"

    def __init__(self, market=None):
        """

        Parameters
        ----------
        market: parent object
        """
        super().__init__(market=market)
        self.add_parent('market', market)
        self.name = "ask"
        self.data = self.data.rename(self.name)

    def add_value(self, index=None, value=None):
        """
        Add value to the pd.Series
        Parameters
        ----------
        index: list
            list of index for pd.Series
        value: list
            list of float for pd.Series values
        """
        row = pd.Series(index=index, data=value, name=self.name)
        self.data = pd.concat([self.data, row], axis=0)


class Bid(Ask):
    """
    Bid value of the market
    """
    def __init__(self, market=None):
        """

        Parameters
        ----------
        market: market object
        """
        super().__init__(market=market)
        self.name = "bid"
        self.data = self.data.rename(self.name)


class Volume(Ask):
    """
    volume value of the market
    """
    def __init__(self, market=None):
        """

        Parameters
        ----------
        market: parent object
        """
        super().__init__(market=market)
        self.name = "volume"
        self.data = self.data.rename(self.name)


class AskLoad(Ask):
    def __init__(self, market=None, data: pd.Series = pd.Series()):
        super().__init__(market=market)
        self.data = data


class BidLoad(Bid):
    def __init__(self, market=None, data: pd.Series = pd.Series()):
        super().__init__(market=market)
        self.data = data


class VolumeLoad(Volume):
    """
    volume value of the market
    """
    def __init__(self, market=None, data: pd.Series = pd.Series()):
        super().__init__(market=market)
        self.data = data


class Derivative(PropertiesABC):
    # function = functions.derivative
    type = 'deriv'

    def __init__(self, market=None, parent=None):
        super().__init__(market=market, parent=parent)
        if 'data' in self.parents.keys():
            self.name = f"{self.parents['data'].name}_{self.type}"
        self.data = self.data.rename(self.name)

    def _function(self):
        return functions.derivative(self.parents['data'].data)


class MovingAverage(PropertiesABC):
    type = 'MA'

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys():
            self.name = f"{self.parents['data'].name}_{self.type}"
        self.data = self.data.rename(self.name)
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param=}")
            if 'data' in self.parents.keys():
                self.name = f"{self.parents['data'].name}_{self.type}"
        else:
            if 'data' in self.parents.keys():
                self.name = f"{self.parents['data'].name}_{self.type}_k-{param['k']}"

    def _function(self):
        return functions.MA(self.parents['data'].data, k=self.param["k"])


class ExponentialMovingAverage(PropertiesABC):
    type = "EMA"

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys():
            self.name = f"{self.parents['data'].name}_{self.type}"
        self.data = self.data.rename(self.name)
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param=}")
            if 'data' in self.parents.keys():
                self.name = f"{self.parents['data'].name}_{self.type}"
        else:
            if 'data' in self.parents.keys():
                self.name = f"{self.parents['data'].name}_{self.type}_k-{param['k']}"

    def _function(self):
        return functions.EMA(self.parents['data'].data, k=self.param['k'])


class StandardDeviation(PropertiesABC):
    type = "std"

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys():
            self.name = f"{self.parents['data'].name}_{self.type}"
        self.data = self.data.rename(self.name)
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param=}")
            if 'data' in self.parents.keys():
                self.name = f"{self.parents['data'].name}_{self.type}"
        else:
            if 'data' in self.parents.keys():
                self.name = f"{self.parents['data'].name}_{self.type}_k-{param['k']}"

    def _function(self):
        return functions.standard_deviation(self.parents['data'].data, k=self.param['k'])


class Variation(PropertiesABC):
    type = "variation"

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys():
            self.name = f"{self.parents['data'].name}_{self.type}"
        self.data = self.data.rename(self.name)
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param=}")
            if 'data' in self.parents.keys():
                self.name = f"{self.parents['data'].name}_{self.type}"
        else:
            if 'data' in self.parents.keys():
                self.name = f"{self.parents['data'].name}_{self.type}_k-{param['k']}"

    def _function(self):
        return functions.variation(self.parents['data'].data, k=self.param['k'])


class RSI(PropertiesABC):
    type = 'rsi'

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys():
            self.name = f"{self.parents['data'].name}_{self.type}"
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param=}")
            if 'data' in self.parents.keys():
                self.name = f"{self.parents['data'].name}_{self.type}"
        else:
            if 'data' in self.parents.keys():
                self.name = f"{self.parents['data'].name}_{self.type}_k-{param['k']}"
        self.data = self.data.rename(self.name)

    def _function(self):
        return functions.rsi(self.parents['data'].data, k=self.param['k'])

