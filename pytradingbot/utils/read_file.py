"""
Module containing function to read file
"""
# =================
# Python IMPORTS
# =================
import os.path
import logging
import pandas as pd
from lxml import etree

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
    root_dir = os.path.dirname(__file__)
    if not os.path.isfile(path):
        logging.warning(f"{path} is not a file, market is not loaded")
        return None

    data_df = pd.DataFrame()
    with open(path) as files:
        for file in files:
            if len(file) > 0:
                if os.path.isfile(file):
                    data_df = pd.concat([data_df, read_csv_market(file)], axis=0)
                elif os.path.isfile(f"{root_dir}/..tests/{file}"):
                    print(f"{root_dir}/../tests/{file}")
                    data_df = pd.concat([data_df, read_csv_market(f"{root_dir}/../tests/{file}")], axis=0)
                else:
                    print(f"{root_dir}/../tests/{file}")
                    logging.warning(f"{file} is not a file, file skipped")
    data_df.sort_index(axis=0)
    return data_df


def read_input_analysis_config(path: str) -> list:
    """function to read the analysis part of input xml file

    Parameters
    ----------
    path: str
        path if the xml file

    Returns
    -------
    list of properties: properties are stored in a dict
    """
    properties = []
    if not os.path.isfile(path):
        logging.warning(f"{path} is not a file, cannot set input config parameters")
        return properties

    # XML Parser
    main = etree.parse(path)

    # Read properties
    for prop in main.xpath("/pytradingbot/analysis/properties"):
        pass

    return properties


def read_input_config():
    """Not ready"""
    pass
