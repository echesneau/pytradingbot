# =================
# Python IMPORTS
# =================
from typing import Dict, Any
import pandas as pd

# =================
# Internal IMPORTS
# =================

# =================
# Variables
# =================


class PropertiesABC:
    parents: Dict[Any, Any] = {}
    child = []
    function: callable = None
    data = pd.Series()
    param: Dict[Any, Any] = {}

    def __init__(self):
        pass

    def update(self):
        if self.function is not None and len(self.parents) > 0 and \
                len(self.parents.values()[0]) != len(self.data):
            self.data = self.function(self.parents, self.param)

    def add_parent(self, name, obj):
        self.parents[name] = obj

    def add_child(self, obj):
        if obj not in self.child:
            self.child.append(obj)


class Ask(PropertiesABC):
    name = 'ask'

    def __init__(self, parent=None):
        super().__init__()
        self.add_parent('market', parent)
        self.data = self.data.rename(self.name)

    def add_value(self, index=None, value=None):
        row = pd.Series(index=index, data=value)
        self.data = pd.concat([self.data, row], axis=0)


class Bid(Ask):
    name = 'bid'
