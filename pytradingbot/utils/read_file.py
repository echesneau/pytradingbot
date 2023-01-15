# =================
# Python IMPORTS
# =================
import os.path
import logging
import pandas as pd

# =================
# Internal IMPORTS
# =================
from pytradingbot.utils.market_tools import split_time

# =================
# Variables
# =================


def read_idconfig(path: str) -> pd.DataFrame:
    """
    Function to read the id.config file

    Parameters
    ----------
    path: str
        Path of the id.config file

    Returns
    -------
    pd.DataFrame : DataFrame containing all ids.
    """
    if os.path.isfile(path):
        data = pd.read_csv(path, delimiter=" ")
        data.columns = ["user", "key", "private"]
        return data
    else:
        logging.error(f"{path} is not a file.")
        return pd.DataFrame(columns=["user", "key", "private"])


def read_csv_market(path: str):
    if not os.path.isfile(path):
        logging.warning(f"{path} is not a file, market is not loaded")
        return None

    # Read the file
    df_market = pd.read_csv(path, sep=" ", index_col=0, parse_dates=True)

    # Split
    df_market.sort_index(axis=0)
    list_market = split_time(df_market, delta=120)

    # Create market class

    # Create all properties

    return df_market
