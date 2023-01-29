# =================
# Python IMPORTS
# =================
import logging
import pandas as pd
import os.path

# =================
# Internal IMPORTS
# =================
from pytradingbot.utils.read_file import read_csv_market, read_list_market
from pytradingbot.cores.markets import MarketLoad
# =================
# Variables
# =================


def split_time_df(data, delta=60):
    # create timestep between two rows
    data["delta"] = data.index.to_series().diff().dt.total_seconds().fillna(0)
    # where timestep is higher than user defined limit
    idx = data.index[data['delta'] > delta]
    # create output list 
    odata = []
    last_value = 0
    if len(idx) == 0:
        odata.append(data.drop(columns=["delta"]))
        last_value = 0
    for i, value in enumerate(idx):
        if i == 0:
            odata.append(data[:value].drop(columns=["delta"]).iloc[:-1])
        if i == len(idx) - 1:
            if i != 0:
                odata.append(data[last_value:value].drop(columns=["delta"]).iloc[:-1])
            odata.append(data[value:].drop(columns=["delta"]))
        elif i != 0:
            odata.append(data[last_value:value].drop(columns=["delta"]).iloc[:-1])
        last_value = value
    return odata


def df2market(df: pd.DataFrame):
    test = True
    for prop in ['bid', 'ask', 'volume']:
        if prop not in df.columns:
            test = False
    if test:
        return MarketLoad(df['ask'], df['bid'], df['volume'])
    else:
        return None


def market_from_file(ifile: str, fmt="csv"):
    fmt_choices = ["csv", "list"]
    if not os.path.isfile(ifile):
        logging.warning(f"{ifile} is not a file, market is not loaded")
        return None
    if fmt == "csv":
        df = read_csv_market(ifile)
    elif fmt == "list":
        df = read_list_market(ifile)
    else:
        logging.warning(f"{fmt} is not an accepted format, market is not loaded. Possible choices: {fmt_choices}")
        return None

    # split dataframe if timedelta is too high
    list_df = split_time_df(df, delta=120)  # Todo: auto defined the delta time from the data

    # Create market class
    list_market = []
    for i, data in enumerate(list_df):
        if 'ask' in data.columns and 'bid' in data.columns and "volume" in data.columns:
            list_market.append(df2market(data))
        else:
            logging.warning(f"ask and/or bid property missing in dataframe {i}, skipped")

    # Create all properties
    # TODO: add option to add other properties than bid / ask in the market

    return list_market
