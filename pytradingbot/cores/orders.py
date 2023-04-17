from abc import ABC
import pandas as pd
import logging

from pytradingbot.cores.properties import PropertiesABC, generate_property_by_name


class Condition(ABC):
    name = "abstract"
    type = "abstract"

    def __init__(self, parent: PropertiesABC, value: float):
        self.parent = parent
        self.value = value
        self.data = pd.Series(dtype=bool)

    def _function(self) -> pd.Series:
        return pd.Series(data=[0] * len(self.parent.data), dtype=bool)

    def update(self):
        if len(self.data) < len(self.parent.data):
            self.data = self._function()


class Order(ABC):
    type = "abstract"  # should be buy or sell

    def __init__(self, market: object = None):
        self.child = []
        self.parents = {}
        self.data = pd.Series(dtype=bool)
        if market is not None:
            self.parents["market"] = market

    def add_child(self, obj):
        """
        Method to add a child

        Parameters
        ----------
        obj: child object
        """
        if obj is not None and obj not in self.child:
            self.child.append(obj)

    def _get_all_child(self):
        return [child for child in self.child]

    def get_all_data_by_type(self, atype):
        child = self.find_actions_by_type(atype)
        return [c.data for c in child]

    def find_actions_by_type(self, atype):
        return [child for child in self.child if child.type == atype]

    def update(self):
        for child in self.child:
            child.update()

        buy_child = self.find_actions_by_type("buy")
        if len(buy_child) > 0:
            buy_data = pd.concat(self.get_all_data_by_type("buy"), axis=1).any(axis=1)
        elif "market" in self.parents:
            buy_data = pd.Series(data=[0] * len(self.parents["market"].ask.data),
                                 index=self.parents["market"].ask.data.index)
        else:
            buy_data = pd.Series(data=[0])

        sell_child = self.find_actions_by_type("sell")
        if len(sell_child) > 0:
            sell_data = pd.concat(self.get_all_data_by_type("sell"), axis=1).any(axis=1)
        else:
            sell_data = pd.Series(data=[0] * len(buy_data), index=buy_data.index)

        # generate self.data by merging  conditions
        # -1 if sell, +1 buy, 0 if both are true
        self.data = buy_data.astype(int) - sell_data.astype(int)

    @property
    def action(self):
        # check if update

        return self.data.values[-1]
        # return action to do

    def simulate_action(self, imoney=100):
        pass


class Action(ABC):
    type = "abstract"

    def __init__(self, parents=None, market=None):
        self.parents = {}
        self.child = []  # only condition
        self.data = pd.Series(dtype=int)

        if market is not None:
            self.add_parent("market", market)

    def add_child(self, obj: Condition):
        if isinstance(obj, Condition):
            if obj not in self.child:
                self.child.append(obj)
        else:
            logging.warning(f"Wrong object type : {type(obj)}, skipped")

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
        self.data = data.all(axis=1)


class ActionBuy(Action):
    type = "buy"


class ActionSell(Action):
    type = "sell"


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
        return (test_sup + test_inf.shift(1)) == 2
    else:
        return pd.Series(data=[None] * len(data))


def cross_down(data: pd.Series, value: float) -> pd.Series:
    if len(data) > 1:
        test_inf = data <= value
        test_sup = data > value
        return (test_inf + test_sup.shift(1)) == 2
    else:
        return pd.Series(data=[None] * len(data))


def generate_condition_from_dict(cond_dict: dict, market=None) -> Condition:
    if "function" in cond_dict and \
            "value" in cond_dict and \
            "property" in cond_dict.keys():
        if cond_dict['function'] == "<":
            return ConditionLower(generate_property_by_name(cond_dict['property'], market=market), cond_dict['value'])
        elif cond_dict['function'] == ">":
            return ConditionUpper(generate_property_by_name(cond_dict['property'], market=market), cond_dict['value'])
        elif cond_dict['function'] == "-=":
            return ConditionCrossDown(generate_property_by_name(cond_dict['property'], market=market),
                                      cond_dict['value'])
        elif cond_dict['function'] == "+=":
            return ConditionCrossUp(generate_property_by_name(cond_dict['property'], market=market), cond_dict['value'])
        else:
            logging.warning(f"Unknown function: {cond_dict['function']}")
            return None
    else:
        logging.warning("Invalid dictionary keys: should contain function, value and property keys")
        return None


def generate_action_from_dict(action_dict: dict, market):
    if "type" in action_dict.keys() and "conditions" in action_dict.keys():
        if action_dict['type'] == "buy":
            action = ActionBuy(market=market)
        elif action_dict['type'] == "sell":
            action = ActionSell(market=market)
        else:
            logging.warning(f"Unknown action type {action_dict['type']}")
            return None
        if isinstance(action_dict['conditions'], list):
            for condition in action_dict['conditions']:
                condition_tmp = generate_condition_from_dict(condition, market=market)
                if condition_tmp is not None:
                    action.add_child(condition_tmp)
                else:
                    logging.warning(f"Cannot generate condition : {condition}")
            return action
        else:
            logging.warning(f"Conditions of action should be a list, {type(action_dict['conditions'])} found")
            return None
    else:
        logging.warning("Invalid dictionary keys to generate action: should contain type and condition keys")
        return None

# un order renvoie 1, 0, -1 .
# chaque action renvoie 1 ou 0.
# un order peut contenir plusieurs action du meme type => or pour les sommer
# chaque action contient des conditions (comparaison variables vs valeurs)
