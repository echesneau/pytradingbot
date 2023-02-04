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
        # merge all actions
        
        # return action to do
        
        
class Action(ABC):
    type = "abstract"
    def __init__(self, parents=None,  market=None):
        self.parents = 
        pass
        
    def update(self):
        pass
        
        
class ActionBuy(Action):
    type = "buy"
    
    
class ActionSell(Action):
    type = "sell"
    
    
class Condition(ABC):
    pass