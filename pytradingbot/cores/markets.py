# =================
# Python IMPORTS
# =================
import os
import pandas as pd
import logging

# =================
# Internal IMPORTS
# =================
from pytradingbot.cores import properties

# =================
# Variables
# =================


class Market:
    """
    Class containing value of market
    """
    parents = {}
    child = []

    def __init__(self, parent=None, odir=None, oformat='pandas'):
        """

        Parameters
        ----------
        parent: API class
        odir: str
            output directory
        oformat: str
            output format
        """
        self.add_parent('api', parent)
        self.ask = properties.Ask(parent=self)
        self.bid = properties.Bid(parent=self)
        self.volume = properties.Volume(parent=self)
        self.odir = odir
        self.oformat = oformat
        if self.odir is not None and not os.path.isdir(self.odir):
            os.makedirs(self.odir)

    def update(self):
        """
        method to update market values
        """
        if 'api' in self.parents.keys():
            values = self.parents['api'].get_market()
            self.ask.add_value(index=[values['time']], value=[values['ask']])
            self.bid.add_value(index=[values['time']], value=[values['bid']])
            self.volume.add_value(index=[values['time']], value=[values['volume']])
        else:
            logging.warning(f"api is not defined in parents: available parents: {self.parents.keys()}")

    def analyse(self):
        """
        Method to analyse market value
        """
        for prop in self.child:
            prop.update()

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

    def dataframe(self):
        """
        Method to return the DataFrame containing all values of all properties

        Returns
        -------
            pd.DataFrame
        """
        return pd.concat([self.ask.data, self.bid.data, self.volume.data]+[prop.data for prop in self.child], axis=1)

    def save(self):
        """
        Method to save market in a file
        """
        pass
