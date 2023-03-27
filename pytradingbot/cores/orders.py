from abc import ABC

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
        self.child = [] # only condition
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
        data = pd.concat([child.data for child in self.child], axis = 1)
        self.data = data.all()
        
        
class ActionBuy(Action):
    type = "buy"
    
    
class ActionSell(Action):
    type = "sell"
    
    
class Condition(ABC):
    name = "abstract"
    type = "abstract"
    def __init__(self, parent, value):
        self.parent = parent
        self.value = value
        
        pass
    
    def _function():
        return pd.Series() # todo with len of parent
        
    
un order renvoie 1, 0, -1 .
chaque action renvoie 1 ou 0.
un order peut contenir plusieurs action du meme type => or pour les sommer
chaque action contient des conditions (comparaison variables vs valeurs)