from abc import ABC
import pandas as pd

from pytradingbot.cores.properties import PropertiesABC


class Order(ABC):
    type = "abstract" # should be buy or sell
    def __init__(self, market: object = None):
        self.child = []
        self.parents = {}
        self.data = pd.Series()
        if market is not None:
            self.parents["market"] = market
        
    def update(self):
        for child in self.child:
            child.update()
        
        buy_child = [child for child in self.child if child.type == "buy"]
        buy_data = pd.concat([buy_child], axis = 1).any()
        
        sell_child = [child for child in self.child if child.type == "sell"]
        sell_data = pd.concat([sell_child], axis = 1).any()
        
        # generate self.data by merging  conditions
        pass
        
    def action(self):
        # check if update
        
        return self.data.values[-1]
        
        # return action to do
        
        
class Action(ABC):
    type = "abstract"

    def __init__(self, parents=None,  market=None):
        self.parents = {}
        self.child = []  # only condition
        self.data = pd.Series()
        
        if market is not None:
            self.add_parent("market", market)
        
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
        
    def update(self):
        for child in self.child:
            child.update()
        data = pd.concat([child.data for child in self.child], axis=1)
        self.data = data.all()
        
        
class ActionBuy(Action):
    type = "buy"
    
    
class ActionSell(Action):
    type = "sell"
    
    
class Condition(ABC):
    name = "abstract"
    type = "abstract"

    def __init__(self, parent: PropertiesABC, value: float):
        self.parent = parent
        self.value = value
        self.data = pd.Series(dtype=bool)
    
    def _function(self) -> pd.Series:
        return pd.Series(data=[0]*len(self.parent.data), dtype=bool)

    def update(self):
        if len(self.data) < len(self.parent.data):
            self.data = self._function()


class ConditionUpper(Condition):
    name = "greater_than"
    type = ">"

    def __init__(self, parent: PropertiesABC, value: float):
        super().__init__(parent, value)

    def _function(self) -> pd.Series:
        return greater_than(self.parent.data, self.value)


class ConditionLower(Condition):
    name = "lower_than"
    type = "<"

    def __init__(self, parent: PropertiesABC, value: float):
        super().__init__(parent, value)

    def _function(self) -> pd.Series:
        return lower_than(self.parent.data, self.value)


class ConditionCrossUp(Condition):
    name = "cross_up"
    type = "+="

    def __init__(self, parent: PropertiesABC, value: float):
        super().__init__(parent, value)

    def _function(self) -> pd.Series:
        return cross_up(self.parent.data, self.value)


class ConditionCrossDown(Condition):
    name = "cross_down"
    type = "-="

    def __init__(self, parent: PropertiesABC, value: float):
        super().__init__(parent, value)

    def _function(self) -> pd.Series:
        return cross_down(self.parent.data, self.value)


def greater_than(data: pd.Series, value: float) -> pd.Series:
    return data > value


def lower_than(data: pd.Series, value: float) -> pd.Series:
    return data < value


def cross_up(data: pd.Series, value: float) -> pd.Series:
    if len(data) > 1:
        test_sup = data >= value
        test_inf = data < value
        return (test_sup + test_inf.shit(1)) == 2
    else:
        return pd.Series(data=[None]*len(data))


def cross_down(data: pd.Series, value: float) -> pd.Series:
    if len(data) > 1:
        test_inf = data <= value
        test_sup = data > value
        return (test_inf + test_sup.shit(1)) == 2
    else:
        return pd.Series(data=[None]*len(data))
    
# un order renvoie 1, 0, -1 .
# chaque action renvoie 1 ou 0.
# un order peut contenir plusieurs action du meme type => or pour les sommer
# chaque action contient des conditions (comparaison variables vs valeurs)
