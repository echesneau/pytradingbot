"""
Module containing all properties
"""
# =================
# Python IMPORTS
# =================
import logging
from typing import Dict, Any
from abc import ABC
import pandas as pd

# =================
# Internal IMPORTS
# =================
from pytradingbot.properties_functions import functions

# =================
# Variables
# =================


class PropertiesABC(ABC):
    """
    Abstract class for properties
    """
    type = ""

    def __init__(self, parent=None,
                 market: object = None,
                 param: Dict[str, Any] = None):

        self.child = []
        self.data = pd.Series(dtype=float)

        self.parents: Dict[str, object] = {}
        if isinstance(parent, dict):
            self.parents = parent
        # elif parent is not None and type(type(parent)) == type:  # Check is parent is an object created from a class
        elif parent is not None:
            self.add_parent('data', parent)
        # elif parent is not None:
        #     logging.warning(f"type of {parent} is unexpected, skipped")

        if market is not None:  # TODO: check is market is an object with upper class Market
            self.add_parent('market', market)

        self.param: Dict[str, Any] = {}
        if isinstance(param, dict):
            self.param = param
        elif param is not None:
            logging.warning(f"type of {param} is unexpected, skipped")

        self.name = f"{self.type}"
        self.data = self.data.rename(self.name)

    def __call__(self, *args, **kwargs):
        return self.data

    def _function(self) -> pd.Series:
        return self.data

    def update(self):
        """
        Update values of the properties in function of parent values
        """
        # Update parents and check if update is needed
        update = False
        for key, value in self.parents.items():
            if key != "market":
                value.update()
                if len(value.data) > len(self.data):
                    update = True

        # update data
        if update:
            self.data = self._function()
            self.data = self.data.rename(self.name)

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
        obj.add_child(self)

    def add_child(self, obj):
        """
        Method to add a child

        Parameters
        ----------
        obj: child object
        """
        if obj not in self.child:
            self.child.append(obj)

    def clean(self, nrows: int = 0):
        """
        Method to clean data
        Parameters
        ----------
        nrows: int
            maximum number of rows in the pd.Series
        """
        if len(self.data) > nrows:
            self.data = self.data.iloc[-nrows-1:]


class Ask(PropertiesABC):
    """
    Ask value of the market
    """
    type = "market"

    def __init__(self, market=None):
        """

        Parameters
        ----------
        market: parent object
        """
        super().__init__(market=market)
        self.add_parent('market', market)
        self.name = "ask"
        self.data = self.data.rename(self.name)

    def add_value(self, index=None, value=None):
        """
        Add value to the pd.Series
        Parameters
        ----------
        index: list
            list of index for pd.Series
        value: list
            list of float for pd.Series values
        """
        row = pd.Series(index=index, data=value, name=self.name)
        self.data = pd.concat([self.data, row], axis=0)


class Bid(Ask):
    """
    Bid value of the market
    """
    def __init__(self, market=None):
        """

        Parameters
        ----------
        market: market object
        """
        super().__init__(market=market)
        self.name = "bid"
        self.data = self.data.rename(self.name)


class Volume(Ask):
    """
    volume value of the market
    """
    def __init__(self, market=None):
        """

        Parameters
        ----------
        market: parent object
        """
        super().__init__(market=market)
        self.name = "volume"
        self.data = self.data.rename(self.name)


class AskLoad(Ask):
    """
    Ask value loaded
    """
    def __init__(self, market=None, data: pd.Series = pd.Series(dtype=float)):
        super().__init__(market=market)
        self.data = data


class BidLoad(Bid):
    """
    Bid value loaded
    """
    def __init__(self, market=None, data: pd.Series = pd.Series(dtype=float)):
        super().__init__(market=market)
        self.data = data


class VolumeLoad(Volume):
    """
    volume value of the market
    """
    def __init__(self, market=None, data: pd.Series = pd.Series(dtype=float)):
        super().__init__(market=market)
        self.data = data


class Derivative(PropertiesABC):
    """
    Derivative
    """
    type = 'deriv'

    def __init__(self, market=None, parent=None):
        super().__init__(market=market, parent=parent)
        if 'data' in self.parents.keys():
            self.name = f"{self.type}_{self.parents['data'].name}"
        self.data = self.data.rename(self.name)

    def _function(self):
        return functions.derivative(self.parents['data'].data)


class MovingAverage(PropertiesABC):
    """
    Moving average
    """
    type = 'MA'

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys():
            self.name = f"{self.type}_{self.parents['data'].name}"
        self.data = self.data.rename(self.name)
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param}")
            if 'data' in self.parents.keys():
                self.name = f"{self.type}_{self.parents['data'].name}"
        else:
            if 'data' in self.parents.keys():
                self.name = f"{self.type}_k-{param['k']}_{self.parents['data'].name}"

    def _function(self):
        return functions.MA(self.parents['data'].data, k=self.param["k"])


class ExponentialMovingAverage(PropertiesABC):
    """
    Exponential moving average
    """
    type = "EMA"

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys():
            self.name = f"{self.type}_{self.parents['data'].name}"
        self.data = self.data.rename(self.name)
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param}")
            if 'data' in self.parents.keys():
                self.name = f"{self.type}_{self.parents['data'].name}"
        else:
            if 'data' in self.parents.keys():
                self.name = f"{self.type}_k-{param['k']}_{self.parents['data'].name}"

    def _function(self):
        return functions.EMA(self.parents['data'].data, k=self.param['k'])


class StandardDeviation(PropertiesABC):
    """
    Standard deviation
    """
    type = "std"

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys():
            self.name = f"{self.type}_{self.parents['data'].name}"
        self.data = self.data.rename(self.name)
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param}")
            if 'data' in self.parents.keys():
                self.name = f"{self.type}_{self.parents['data'].name}"
        else:
            if 'data' in self.parents.keys():
                self.name = f"{self.type}_k-{param['k']}_{self.parents['data'].name}"

    def _function(self):
        return functions.standard_deviation(self.parents['data'].data, k=self.param['k'])


class Variation(PropertiesABC):
    """
    Variation
    """
    type = "variation"

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys():
            self.name = f"{self.type}_{self.parents['data'].name}"
        self.data = self.data.rename(self.name)
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param}")
            if 'data' in self.parents.keys():
                self.name = f"{self.type}_{self.parents['data'].name}"
        else:
            if 'data' in self.parents.keys():
                self.name = f"{self.type}_k-{param['k']}_{self.parents['data'].name}"

    def _function(self):
        return functions.variation(self.parents['data'].data, k=self.param['k'])


class RSI(PropertiesABC):
    """
    RSI
    """
    type = 'rsi'

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys():
            self.name = f"{self.type}_k-{param['k']}_{self.parents['data'].name}"
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param}")
            if 'data' in self.parents.keys():
                self.name = f"{self.type}_{self.parents['data'].name}"
        else:
            if 'data' in self.parents.keys():
                self.name = f"{self.type}_k-{param['k']}_{self.parents['data'].name}"
        self.data = self.data.rename(self.name)

    def _function(self):
        return functions.rsi(self.parents['data'].data, k=self.param['k'])


class MACD(PropertiesABC):
    """
    MACD
    """
    type = 'macd'

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'short' in self.parents.keys() and 'long' in self.parents.keys():
            if 'k' in self.param:
                self.name = f"{self.type}_k-{param['k']}_long_{self.parents['long'].name}_" \
                            f"short_{self.parents['short'].name}"
        if 'k' not in self.param:
            logging.warning(f"k is not defined in parameters: {param}")
        self.data = self.data.rename(self.name)

    def _function(self):
        return functions.macd(self.parents['short'].data, self.parents['long'].data,
                              k=self.param['k'])

    def update(self):
        update = False
        if len(self.parents) > 0:
            if 'short' in self.parents and 'long' in self.parents and \
                    len(self.parents['short'].data) > len(self.data):
                update = True
            elif 'market' in self.parents and len(self.parents['market'].ask.data) > len(self.data):
                update = True

        # update data
        if update:
            self.data = self._function()
            self.data = self.data.rename(self.name)


class Bollinger(PropertiesABC):
    """
    Bollinger
    """
    type = 'bollinger'

    def __init__(self, market=None, parent=None, param=None):
        super().__init__(market=market, parent=parent, param=param)
        if 'data' in self.parents.keys() and 'mean' in self.parents.keys() and \
                'std' in self.parents.keys():
            if 'k' not in param:
                logging.warning("k is not defined in param, set to 2")
                param['k'] = 2
            self.name = f"{self.type}_k-{param['k']}_data_{self.parents['data'].name}_" \
                        f"mean_{self.parents['mean'].name}_std_{self.parents['std'].name}"
        else:
            logging.warning("Missing parent values")
            self.name = self.type
        self.data = self.data.rename(self.name)

    def _function(self):
        return functions.bollinger(self.parents['data'].data, self.parents['mean'].data,
                                   self.parents['std'].data, self.param['k'])


def generate_derivative_by_name(name: str, market):
    words = name.split("_")
    parent_str = "_".join(words[1:])
    parent_prop = generate_property_by_name(parent_str, market)
    return Derivative(market=market, parent=parent_prop)


def generate_moving_average_by_name(name: str, market):
    words = name.split("_")
    param = {}
    if words[1].startswith("k-"):
        param["k"] = int(words[1].split("-")[-1])
    parent_str = "_".join(words[2:])
    parent_prop = generate_property_by_name(parent_str, market)
    return MovingAverage(market=market, parent=parent_prop, param=param)


def generate_exponential_moving_average_by_name(name: str, market):
    words = name.split("_")
    param = {}
    if words[1].startswith("k-"):
        param["k"] = int(words[1].split("-")[-1])
    parent_str = "_".join(words[2:])
    parent_prop = generate_property_by_name(parent_str, market)
    return ExponentialMovingAverage(market=market, parent=parent_prop, param=param)


def generate_standard_deviation_by_name(name: str, market):
    words = name.split("_")
    param = {}
    if words[1].startswith("k-"):
        param["k"] = int(words[1].split("-")[-1])
    parent_str = "_".join(words[2:])
    parent_prop = generate_property_by_name(parent_str, market)
    return StandardDeviation(market=market, parent=parent_prop, param=param)


def generate_variation_by_name(name: str, market):
    words = name.split("_")
    param = {}
    if words[1].startswith("k-"):
        param["k"] = int(words[1].split("-")[-1])
    parent_str = "_".join(words[2:])
    parent_prop = generate_property_by_name(parent_str, market)
    return Variation(market=market, parent=parent_prop, param=param)


def generate_rsi_by_name(name: str, market):
    words = name.split("_")
    param = {}
    if words[1].startswith("k-"):
        param["k"] = int(words[1].split("-")[-1])
    parent_str = "_".join(words[2:])
    parent_prop = generate_property_by_name(parent_str, market)
    return RSI(market=market, parent=parent_prop, param=param)


def generate_macd_by_name(name: str, market):
    words = name.split("_")
    param = {}
    if words[1].startswith("k-"):
        param["k"] = int(words[1].split("-")[-1])
    ishort = words.index("short")
    ilong = words.index("long")
    parent_long_str = "_".join(words[ilong + 1:ishort])
    parent_short_str = "_".join(words[ishort + 1:])
    parent_long = generate_property_by_name(parent_long_str, market)
    parent_short = generate_property_by_name(parent_short_str, market)
    return MACD(market=market, param=param, parent={"short": parent_short, "long": parent_long})


def generate_bollinger_by_name(name: str, market):
    words = name.split("_")
    param = {}
    if words[1].startswith("k-"):
        param["k"] = int(words[1].split("-")[-1])
    idata = words.index("data")
    imean = words.index("mean")
    istd = words.index("std")
    parent_data_str = "_".join(words[idata + 1:imean])
    parent_mean_str = '_'.join(words[imean + 1:istd])
    parent_std_str = "_".join(words[istd + 1:])
    parent_data = generate_property_by_name(parent_data_str, market)
    parent_mean = generate_property_by_name(parent_mean_str, market)
    parent_std = generate_property_by_name(parent_std_str, market)
    return Bollinger(market=market, param=param,
                     parent={'data': parent_data, "mean": parent_mean, "std": parent_std})


def generate_property_by_name(name: str, market) -> [PropertiesABC, None]:
    if market.is_property_by_name(name):
        return market.find_property_by_name(name)
    words = name.split("_")
    if len(words) > 1:
        if words[0] == "deriv":
            return generate_derivative_by_name(name, market)
        elif words[0] == "MA":
            return generate_moving_average_by_name(name, market)
        elif words[0] == "EMA":
            return generate_exponential_moving_average_by_name(name, market)
        elif words[0] == "std":
            return generate_standard_deviation_by_name(name, market)
        elif words[0] == "variation":
            return generate_variation_by_name(name, market)
        elif words[0] == "rsi":
            return generate_rsi_by_name(name, market)
        elif words[0] == "macd":
            return generate_macd_by_name(name, market)
        elif words[0] == "bollinger":
            return generate_bollinger_by_name(name, market)
        else:
            logging.warning(f"unknow property type {name}")
            return None

    else:
        logging.warning(f"unknown property format name : {name}")


