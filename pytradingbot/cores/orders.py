"""
Module containing all classes and functions for market Orders
"""

from abc import ABC
import logging
import pandas as pd
import numpy as np
from pytradingbot.cores.properties import PropertiesABC, generate_property_by_name


class Condition(ABC):
    """Condition Class"""

    name = "abstract"
    type = "abstract"

    def __init__(self, parent: PropertiesABC, value: float):
        """Initialisation method"""
        self.parent = parent
        self.value = value
        self.data = pd.Series(dtype=bool)

    def _function(self) -> pd.Series:
        """Condition function"""
        return pd.Series(data=[0] * len(self.parent.data), dtype=bool)

    def update(self, force: bool = False):
        """Update method"""
        if (len(self.data) < len(self.parent.data)) or force:
            self.data = self._function()


class Order(ABC):
    """Market Order class"""

    type = "abstract"  # should be buy or sell

    def __init__(self, market=None):
        self.child = []
        self.parents = {}
        self.data = pd.Series(dtype=int)
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

    def get_all_data_by_type(self, atype: str) -> list:
        """
        Method to get all actions of a specific type

        Parameters
        ----------
        atype: str
            Action type: sell or buy

        Returns
        -------
        list of Action object
        """
        child = self.find_actions_by_type(atype)
        return [c.data for c in child]

    def find_actions_by_type(self, atype):
        """
        Method to get all actions of a specific type

        Parameters
        ----------
        atype: str
            Action type: sell or buy

        Returns
        -------
        list of Action object
        """
        return [child for child in self.child if child.type == atype]

    def update(self, force: bool = False):
        """
        Method to update order data value.
        Do the update of all actions
        Parameters
        ----------
        force: Bool
            arguments to force the analysis evenif the shape of data is the same
        """
        for child in self.child:
            child.update(force=force)

        if force:
            update = True
        elif "market" in self.parents and len(self.data) < len(
            self.parents["market"].dataframe()
        ):
            update = True
        elif len(self.child) > 0 and len(self.data) < len(self.child[0].data):
            update = True
        else:
            update = False

        if update:
            buy_child = self.find_actions_by_type("buy")
            if len(buy_child) > 0:
                buy_data = pd.concat(self.get_all_data_by_type("buy"), axis=1).any(
                    axis=1
                )
            elif "market" in self.parents:
                buy_data = pd.Series(
                    data=[0] * len(self.parents["market"].ask.data),
                    index=self.parents["market"].ask.data.index,
                )
            else:
                buy_data = pd.Series(data=[0])

            sell_child = self.find_actions_by_type("sell")
            if len(sell_child) > 0:
                sell_data = pd.concat(self.get_all_data_by_type("sell"), axis=1).any(
                    axis=1
                )
            else:
                sell_data = pd.Series(data=[0] * len(buy_data), index=buy_data.index)

            # generate self.data by merging  conditions
            # -1 if sell, +1 buy, 0 if both are true
            self.data = buy_data.astype(int) - sell_data.astype(int)

    @property
    def action(self):
        """
        Method to get the action to do at the last line of market (for a use in a production mode)

        Returns
        -------
        int: -1, 0 or 1
            -1 to sell
            0 to do nothing
            1 to buy

        """
        # check if update
        self.update()
        if len(self.data) > 0:
            return self.data.values[-1]
        else:
            return 0
        # return action to do

    def simulate_trading(
        self,
        imoney: float = 100,
        fees: float = 0.1,
        cost_no_action: float = 100,
        min_order_per_day=0,
        verbose=1,
    ):
        """
        Method to simulate a trading for the Order.
        Use with MarketLoad

        Parameters
        ----------
        imoney: float
            initial money
        fees: float
            trading fees
        cost_no_action: float
            cost if no trade
        min_order_per_day:
            minimum amount of trades per day
        verbose: bool
            verbose mode

        Returns
        -------
        tuple: money win, number of win, number of loose
        """
        # Update order
        self.update()
        # Init variable
        list_buy: list = []  # list of buy action
        list_sell: list = []  # list of sell action
        list_fees_buy: list = []
        list_fees_sell: list = []
        money: float = imoney
        balance_action: float = 0  # action in balance
        action: int = 1  # buy: 1, sell: -1
        counter: int = 0  # last position in array
        if "market" in self.parents:
            market = self.parents["market"]
        else:
            logging.warning("No market specify in Order, cannot simulate trading")
            return None, None, None

        # Number of days in market
        market_time = market.ask.data.index
        market_duration = market_time[-1] - market_time[0]
        ndays = market_duration.total_seconds() / 3600 / 24

        # simulate
        while True:
            i = np.where(self.data == action)[0]  # array of index where action
            i = i[np.where(i > counter)[0]]  # first item upper than last action
            if i.shape[0] == 0:
                break  # Stop if no more occurrence
            else:
                i = i[0]
            if action == 1:  # if buy
                if money < 0:
                    break  # Stop if no more money
                balance_action += money / market.ask.data.iloc[i]
                # remove action corresponding to fees
                fee = money * fees / 100
                balance_action -= fee / market.ask.data.iloc[i]
                list_buy.append([balance_action, market.ask.data.iloc[i]])
                list_fees_buy.append(fee)
                money -= list_buy[-1][0] * list_buy[-1][1]
                money -= fee
                if verbose == 1:
                    print(
                        f"{market.ask.data.index[i]} : BUY : {list_buy[-1][0]} @ {list_buy[-1][1]}"
                    )
                    print(f"{market.ask.data.index[i]} : MONEY = {money}")
                action = -1
                counter = i
            elif action == -1:
                list_sell.append([list_buy[-1][0], market.bid.data.iloc[i]])
                balance_action -= list_buy[-1][0]
                money += list_sell[-1][0] * list_sell[-1][1]
                fee = list_sell[-1][0] * list_sell[-1][1] * fees / 100
                money -= fee
                list_fees_sell.append(fee)
                if verbose == 1:
                    print(
                        f"{market.bid.data.index[i]} : SELL : "
                        f"{list_sell[-1][0]} @ {list_sell[-1][1]}"
                    )
                    print(f"{market.bid.data.index[i]} : MONEY = {money}")
                action = 1
                counter = i
        if len(list_buy) > len(list_sell):
            money += list_buy[-1][0] * list_buy[-1][1] + list_fees_buy[-1]
            list_buy = list_buy[:-1]  # remove last buy if end with a buy
        if len(list_buy) > 0:
            array_buy = np.array(list_buy)
            array_sell = np.array(list_sell)
            tmp = np.zeros(array_buy.shape)
            tmp[:, 0] = array_buy[:, 0] * array_buy[:, 1]  # buy list
            tmp[:, 1] = (
                array_sell[:, 0] * array_sell[:, 1]
            )  # - np.array(list_cost)  # sell list
            win = np.count_nonzero(np.any(np.diff(tmp, axis=1) > 0, axis=1))
            loose = np.count_nonzero(np.any(np.diff(tmp, axis=1) < 0, axis=1))
        else:
            win, loose = 0, 0
            money -= cost_no_action
        if win + loose > min_order_per_day * ndays:
            return money, win, loose
        else:
            penalty = (win + loose) - (min_order_per_day * ndays)
            return money + penalty, win, loose


class Action(ABC):
    """
    Action class
    Compile Conditions for a type of Action
    """

    type = "abstract"

    def __init__(self, market=None):
        self.parents = {}
        self.child = []  # only condition
        self.data = pd.Series(dtype=int)

        if market is not None:
            self.add_parent("market", market)

    def add_child(self, obj: Condition):
        """
        Method to add a child

        Parameters
        ----------
        obj: Condition
            child object
        """
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

    def update(self, force: bool = False):
        """
        Method to update Action data value.
        Do the update of all conditions
        """
        for child in self.child:
            child.update(force=force)
        data = pd.concat([child.data for child in self.child], axis=1)
        self.data = data.all(axis=1)


class ActionBuy(Action):
    """
    Action class to buy
    Compile Conditions for action "buy"
    """

    type = "buy"


class ActionSell(Action):
    """
    Action class to sell
    Compile Conditions for action "sell"
    """

    type = "sell"


class ConditionUpper(Condition):
    """Condition Class with greater than function"""

    name = "greater_than"
    type = ">"

    def _function(self) -> pd.Series:
        return greater_than(self.parent.data, self.value)


class ConditionLower(Condition):
    """Condition Class with lower than function"""

    name = "lower_than"
    type = "<"

    def _function(self) -> pd.Series:
        return lower_than(self.parent.data, self.value)


class ConditionCrossUp(Condition):
    """Condition Class with cross up function"""

    name = "cross_up"
    type = "+="

    def _function(self) -> pd.Series:
        return cross_up(self.parent.data, self.value)


class ConditionCrossUp5(Condition):
    """Condition Class with cross up last ten function"""

    name = "cross_up_last_five"
    type = "+=5"

    def _function(self) -> pd.Series:
        return cross_up_last_n(self.parent.data, self.value, n=5)


class ConditionCrossUp10(Condition):
    """Condition Class with cross up last ten function"""

    name = "cross_up_last_ten"
    type = "+=10"

    def _function(self) -> pd.Series:
        return cross_up_last_n(self.parent.data, self.value, n=10)


class ConditionCrossDown(Condition):
    """Condition Class with cross down function"""

    name = "cross_down"
    type = "-="

    def _function(self) -> pd.Series:
        return cross_down(self.parent.data, self.value)


class ConditionCrossDown5(Condition):
    """Condition Class with cross down last 5 steps function"""

    name = "cross_down_last_five"
    type = "-=5"

    def _function(self) -> pd.Series:
        return cross_down_last_n(self.parent.data, self.value, n=5)


class ConditionCrossDown10(Condition):
    """Condition Class with cross down last 10 steps function"""

    name = "cross_down_last_ten"
    type = "-=10"

    def _function(self) -> pd.Series:
        return cross_down_last_n(self.parent.data, self.value, n=10)


def greater_than(data: pd.Series, value: float) -> pd.Series:
    """
    Function to check if data are greater than a value

    Parameters
    ----------
    data: Series
        Series to compare
    value: float
        target value

    Returns
    -------
    Series of bool
    """
    return data > value


def lower_than(data: pd.Series, value: float) -> pd.Series:
    """
    Function to check if data are lower than a value

    Parameters
    ----------
    data: Series
        Series to compare
    value: float
        target value

    Returns
    -------
    Series of bool
    """
    return data < value


def cross_up(data: pd.Series, value: float) -> pd.Series:
    """
    function to detect a cross up

    Parameters
    ----------
    data: Series
        data where to check the cross up
    value: float
        target value of cross up

    Returns
    -------
    Series of bool
    """
    if len(data) > 1:
        test_sup = data >= value
        test_inf = data < value
        return (test_sup + test_inf.shift(1)) == 2
    else:
        return pd.Series(data=[None] * len(data))


def cross_up_last_n(data: pd.Series, value: float, n: int = 5) -> pd.Series:
    """
    function to detect a cross up in previous last n step
    Parameters
    ----------
    data: Series
        data where to check the cross up
    value: float
        target value of cross up
    n: int
        number to step to check

    Returns
    -------
    Series of bool
    """
    cross_up_data = cross_up(data, value)
    index = list(data.index)
    idx_cross_up = list(cross_up_data[cross_up_data == True].index)
    i_cross_up = [index.index(i) for i in idx_cross_up]
    idx_new = [
        index[i]
        for j in i_cross_up
        for i in range(j, j + n + 1)
        if i < len(cross_up_data)
    ]
    cross_up_data[cross_up_data.index.isin(idx_new)] = True
    # cross_up_data.iloc[idx_new] = True
    return cross_up_data


def cross_down(data: pd.Series, value: float) -> pd.Series:
    """
    function to detect a cross down

    Parameters
    ----------
    data: Series
        data where to check the cross down
    value: float
        target value of cross down

    Returns
    -------
    Series of bool
    """
    if len(data) > 1:
        test_inf = data <= value
        test_sup = data > value
        return (test_inf + test_sup.shift(1)) == 2
    else:
        return pd.Series(data=[None] * len(data))


def cross_down_last_n(data: pd.Series, value: float, n: int = 5) -> pd.Series:
    """
    function to detect a cross down in previous last n step
    Parameters
    ----------
    data: Series
        data where to check the cross down
    value: float
        target value of cross down
    n: int
        number to step to check

    Returns
    -------
    Series of bool
    """
    cross_down_data = cross_down(data, value)
    index = list(data.index)
    idx_cross_down = list(cross_down_data[cross_down_data == True].index)
    i_cross_down = [index.index(i) for i in idx_cross_down]
    idx_new = [
        index[i]
        for j in i_cross_down
        for i in range(j, j + n + 1)
        if i < len(cross_down_data)
    ]
    # cross_down_data.iloc[idx_new] = True
    cross_down_data[cross_down_data.index.isin(idx_new)] = True
    return cross_down_data


def generate_condition_from_dict(cond_dict: dict, market=None) -> [None, Condition]:
    """
    function to generate conditions from a dictionary.
    dictionary should have function, value and property keys

    Parameters
    ----------
    cond_dict: dict
        dict keys: function (<,>,-=,+=), value (float) and property (str of the property name)
    market: Market object

    Returns
    -------
    Condition if succeed, else None
    """
    if (
        "function" in cond_dict
        and "value" in cond_dict
        and "property" in cond_dict.keys()
    ):
        if cond_dict["function"] == "<":
            return ConditionLower(
                generate_property_by_name(cond_dict["property"], market=market),
                cond_dict["value"],
            )
        elif cond_dict["function"] == ">":
            return ConditionUpper(
                generate_property_by_name(cond_dict["property"], market=market),
                cond_dict["value"],
            )
        elif cond_dict["function"] == "-=":
            return ConditionCrossDown(
                generate_property_by_name(cond_dict["property"], market=market),
                cond_dict["value"],
            )
        elif cond_dict["function"] == "+=":
            return ConditionCrossUp(
                generate_property_by_name(cond_dict["property"], market=market),
                cond_dict["value"],
            )
        elif cond_dict["function"] == "+=5":
            return ConditionCrossUp5(
                generate_property_by_name(cond_dict["property"], market=market),
                cond_dict["value"],
            )
        elif cond_dict["function"] == "+=10":
            return ConditionCrossUp10(
                generate_property_by_name(cond_dict["property"], market=market),
                cond_dict["value"],
            )
        elif cond_dict["function"] == "-=5":
            return ConditionCrossDown5(
                generate_property_by_name(cond_dict["property"], market=market),
                cond_dict["value"],
            )
        elif cond_dict["function"] == "-=10":
            return ConditionCrossDown10(
                generate_property_by_name(cond_dict["property"], market=market),
                cond_dict["value"],
            )
        else:
            logging.warning(f"Unknown function: {cond_dict['function']}")
            return None
    else:
        logging.warning(
            "Invalid dictionary keys: should contain function, value and property keys"
        )
        return None


def generate_action_from_dict(action_dict: dict, market) -> [Action, None]:
    """
    function to generate Action from a dictionary.
    dictionary should have type and conditions keys

    Parameters
    ----------
    action_dict: dict
        dict keys: type (sell or buy), conditions (list of dict to generate conditions)
    market: Market object

    Returns
    -------
    Action if succeed, else None
    """
    if "type" in action_dict.keys() and "conditions" in action_dict.keys():
        if action_dict["type"] == "buy":
            action = ActionBuy(market=market)
        elif action_dict["type"] == "sell":
            action = ActionSell(market=market)
        else:
            logging.warning(f"Unknown action type {action_dict['type']}")
            return None
        if isinstance(action_dict["conditions"], list):
            for condition in action_dict["conditions"]:
                condition_tmp = generate_condition_from_dict(condition, market=market)
                if condition_tmp is not None:
                    action.add_child(condition_tmp)
                else:
                    logging.warning(f"Cannot generate condition : {condition}")
            return action
        else:
            logging.warning(
                f"Conditions of action should be a list, {type(action_dict['conditions'])} found"
            )
            return None
    else:
        logging.warning(
            "Invalid dictionary keys to generate action: should contain type and condition keys"
        )
        return None
