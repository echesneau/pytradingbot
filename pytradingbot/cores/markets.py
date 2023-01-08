# =================
# Python IMPORTS
# =================
import pandas as pd


# =================
# Internal IMPORTS
# =================
import properties

# =================
# Variables
# =================


class Market:
    parents = {}
    child = []

    def __init__(self, parent=None):
        self.dataframe = pd.DataFrame()
        self.add_parent('api', parent)
        self.ask = properties.Ask(parent=self)
        self.bid = properties.Bid(parent=self)
        # self.add_child(self.ask)
        # self.add_child(self.bid)

    def update(self):
        if 'market' in self.parents.keys():
            values = self.parents['market'].get_market()
            self.ask.add_value(index=values['time'], value=values['ask'])


    def analyse(self):
        for prop in self.child:
            prop.update()

    def add_parent(self, name, obj):
        self.parents[name] = obj

    def add_child(self, obj):
        if obj not in self.child:
            self.child.append(obj)

    def dataframe(self):
        return pd.concat([self.ask.data, self.bid.data]+[prop.data for prop in self.child], axis=1)
