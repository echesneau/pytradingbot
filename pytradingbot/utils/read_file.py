"""
Module containing function to read file
"""
# =================
# Python IMPORTS
# =================
import os.path
import logging
import pandas as pd

# =================
# Internal IMPORTS
# =================
# from pytradingbot.utils.market_tools import split_time_df

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
    """
    function to read market from csv file
    Parameters
    ----------
    path: str
        path of input file

    Returns
    -------
    pd.Dataframe

    """
    if not os.path.isfile(path):
        logging.warning(f"{path} is not a file, market is not loaded")
        return None

    # Read the file
    df_market = pd.read_csv(path, sep=" ", index_col=0, parse_dates=True)

    return df_market


def read_list_market(path: str):
    """
    function to read market from a list of file
    Parameters
    ----------
    path: str
        path of input file

    Returns
    -------
    pd.DataFrame

    """
    if not os.path.isfile(path):
        logging.warning(f"{path} is not a file, market is not loaded")
        return None

    data_df = pd.DataFrame()
    with open(path) as files:
        for file in files:
            if len(file) > 0 and os.path.isfile(file):
                data_df = pd.concat([data_df, read_csv_market(file)], axis=0)
            elif len(file) > 0:
                logging.warning(f"{file} is not a file, file skipped")
    data_df.sort_index(axis=0)
    return data_df


def read_input_config():
    """Not ready"""
    pass
