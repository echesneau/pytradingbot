# =================
# Python IMPORTS
# =================
from typing import Dict, Any
import pandas as pd
from abc import ABC, abstractmethod

# =================
# Internal IMPORTS
# =================

# =================
# Variables
# =================


class PropertiesABC(ABC):
    """
    Abstract class for properties
    """
    parents: Dict[Any, Any] = {}
    child = []
    function: callable = None
    data = pd.Series()
    param: Dict[Any, Any] = {}

    def __init__(self):
        pass

    def update(self):
        """
        Update values of the properties in function of parent values
        """
        if self.function is not None and len(self.parents) > 0 and \
                len(self.parents.values()[0]) != len(self.data):
            self.data = self.function(self.parents, self.param)

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
        if len(self.data) > nrows:
            self.data = self.data.iloc[-nrows:]


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
