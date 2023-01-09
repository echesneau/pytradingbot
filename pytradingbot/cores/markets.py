# =================
# Python IMPORTS
# =================
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
    parents = {}
    child = []

    def __init__(self, parent=None):
        self.add_parent('api', parent)
        self.ask = properties.Ask(parent=self)
        self.bid = properties.Bid(parent=self)
        self.volume = properties.Volume(parent=self)

    def update(self):
        if 'api' in self.parents.keys():
            values = self.parents['api'].get_market()
            self.ask.add_value(index=[values['time']], value=[values['ask']])
            self.bid.add_value(index=[values['time']], value=[values['bid']])
            self.volume.add_value(index=[values['time']], value=[values['volume']])
        else:
            logging.warning(f"api is not defined in parents: available parents: {self.parents.keys()}")

    def analyse(self):
        for prop in self.child:
            prop.update()

    def add_parent(self, name, obj):
        self.parents[name] = obj

    def add_child(self, obj):
        if obj not in self.child:
            self.child.append(obj)

    def dataframe(self):
        return pd.concat([self.ask.data, self.bid.data, self.volume.data]+[prop.data for prop in self.child], axis=1)

    def save(self):
        pass
