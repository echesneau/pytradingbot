"""
Module containing all market objects
"""
# =================
# Python IMPORTS
# =================
import os
import logging
import numpy as np
import pandas as pd

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
        self.parents = {}
        self.child = []
        self.add_parent('api', parent)
        self.ask = properties.Ask(market=self)
        self.bid = properties.Bid(market=self)
        self.volume = properties.Volume(market=self)
        for prop in [self.ask, self.bid, self.volume]:
            self.add_child(prop)
        self.odir = odir
        self.oformat = oformat
        if self.odir is not None and not os.path.isdir(self.odir):
            os.makedirs(self.odir)
        self.nclean: int = 300  # maximum number of row in dataframe

    def __call__(self, *args, **kwargs):
        return self.dataframe()

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
            logging.warning("api is not defined in parents: available parents: "
                            f"{self.parents.keys()}")

    def analyse(self):
        """
        Method to analyse market value
        """
        update_func = [prop.update for prop in self._get_all_child()]
        for update in update_func:
            update()

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
        # return pd.concat([self.ask.data, self.bid.data, self.volume.data]
        #                  + [prop.data for prop in self.child], axis=1)
        return pd.concat([prop.data for prop in self._get_all_child()], axis=1)
    def save(self):
        """
        Method to save market in a file
        """
        data = self.dataframe()
        days = data.index.normalize()
        # TODO: stop writing the first day when nothing is done
        for day in days.unique():
            ofile = f"{self.odir}/{str(day.date())}.dat"
            if not os.path.isfile(ofile):
                odata = data[data.index.date == day.date()]
            else:
                odata = pd.read_csv(ofile, index_col=0, sep=" ")
                odata.index = pd.to_datetime(odata.index)

                mask = np.logical_and(~np.isin(data.index, odata.index),
                                      data.index.date == day.date())
                odata = pd.concat([odata, data[mask]], axis=0)
            odata.sort_index(inplace=True)
            odata.to_csv(path_or_buf=ofile, sep=" ", index_label="time")

    def set_maximum_rows(self, nrows: int):
        """
        set maximum number of rows in the DataFrame (before cleaning)

        Parameters
        ----------
        nrows: int
            number of rows
        """
        self.nclean = nrows

    def clean(self):
        """
        Method to clean the market
        """
        if len(self.ask.data) > self.nclean:
            print("Market cleaned")
            # TODO: get maximum K value in properties
            nrows = 1

            # clean all properties
            self.ask.clean(nrows=nrows)
            self.bid.clean(nrows=nrows)
            self.volume.clean(nrows=nrows)
            for prop in self.child:
                prop.clean(nrows=nrows)
                
    def _get_all_child(self):
        child = self.child
        tmp = child
        while len(tmp) != 0:
            tmp = [prop for c in tmp for prop in c.child if prop not in child]
            child += tmp
        return child


class MarketLoad(Market):
    """
    Class Market where initial data is not empty
    """
    def __init__(self, ask: pd.Series, bid: pd.Series, volume: pd.Series):
        super().__init__()
        self.child = []
        self.ask = properties.AskLoad(data=ask, market=self)
        self.bid = properties.BidLoad(data=bid, market=self)
        self.volume = properties.VolumeLoad(data=volume, market=self)
        for prop in [self.ask, self.bid, self.volume]:
            self.add_child(prop)