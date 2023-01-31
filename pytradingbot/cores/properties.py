# =================
# Python IMPORTS
# =================
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
    def __init__(self):
        self.parents: Dict[Any, Any] = {}
        self.child = []
        self.data = pd.Series()
        self.param: Dict[Any, Any] = {}

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
    name = 'ask'

    def __init__(self, parent=None):
        """

        Parameters
        ----------
        parent: parent object
        """
        super().__init__()
        self.add_parent('market', parent)
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
    name = 'bid'


class Volume(Ask):
    """
    volume value of the market
    """
    name = 'volume'


class AskLoad(Ask):
    def __init__(self, parent=None, data: pd.Series = pd.Series()):
        super().__init__(parent=parent)
        self.data = data


class BidLoad(AskLoad):
    name = 'bid'


class VolumeLoad(AskLoad):
    """
    volume value of the market
    """
    name = 'volume'


class Derivative(PropertiesABC):
    # function = functions.derivative
    name = '_deriv'

    def __init__(self, market=None, parent=None):
        super().__init__()
        if parent is not None:
            self.add_parent('data', parent)
            self.name = f"{self.parents['data'].name}{self.name}"
        if market is not None:
            self.add_parent('market', market)
        self.data = self.data.rename(self.name)

    def _function(self):
        return functions.derivative(self.parents['data'].data)


class MovingAverage(PropertiesABC):
    def __init__(self, market=None, parent=None, param: dict = {}):
        super().__init__()
        self.name = "_MA"
        if parent is not None:
            self.add_parent('data', parent)
            self.name = f"{self.parents['data'].name}{self.name}"
        if market is not None:
            self.add_parent('market', market)
        self.data = self.data.rename(self.name)
        self.param = param

    def _function(self):
        return functions.MA(self.parents['data'].data, k=self.param["k"])


class ExponentialMovingAverage(PropertiesABC):
    def __init__(self, market=None, parent=None, param: dict = {}):
        super().__init__()
        self.name = "_EMA"
        if parent is not None:
            self.add_parent('data', parent)
            self.name = f"{self.parents['data'].name}{self.name}"
        if market is not None:
            self.add_parent('market', market)
        self.data = self.data.rename(self.name)
        self.param = param

    def _function(self):
        return functions.EMA(self.parents['data'].data, k=self.param['k'])


class StandardDeviation(PropertiesABC):
    def __init__(self, market=None, parent=None, param: dict = {}):
        super().__init__()
        self.name = "_std"
        if parent is not None:
            self.add_parent('data', parent)
            self.name = f"{self.parents['data'].name}{self.name}"
        if market is not None:
            self.add_parent('market', market)
        self.data = self.data.rename(self.name)
        self.param = param

    def _function(self):
        return functions.standard_deviation(self.parents['data'].data, k=self.param['k'])

