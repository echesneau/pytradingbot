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
    if not os.path.isfile(path):
        logging.warning(f"{path} is not a file, market is not loaded")
        return None
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # get the directory of the module
    data_df = pd.DataFrame()
    with open(path) as files:
        directory = root_dir
        for line in files:
            if line.startswith("DIR"):
                words = line.split()
                if len(words) == 3:
                    if os.path.isdir(words[2]):
                        directory = words[2]
                    elif os.path.isdir(f"{root_dir}/{words[2]}"):
                        directory = f"{root_dir}/{words[2]}"
                    else:
                        logging.warning(f"{words[2]} is not a directory: {directory} is used")
                else:
                    logging.warning("Uncorrected format for directory, please use format: DIR = your/path/")
            elif len(line) > 0:
                file = f"{directory}/{line.rstrip()}"
                if os.path.isfile(file):
                    data_df = pd.concat([data_df, read_csv_market(file)], axis=0)
                else:
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
        if "format" in prop.attrib:
            fmt = prop.attrib['format']
        else:
            fmt = "name"
        if fmt in ['name']:
            properties.append({"format": fmt, "value": prop.text})
        else:
            logging.warning(f"Unknown property format: {fmt}: {prop.text} skipped")
    return properties


def read_input_config():
    """Not ready"""
    pass
