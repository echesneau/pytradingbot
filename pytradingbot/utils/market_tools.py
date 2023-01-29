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
# =================
# Variables
# =================


def split_time_df(data, delta=60):
    # create timestep between two rows
    data["delta"] = data.index.to_series().diff().dt.total_seconds().fillna(0)
    # where timestep is higher than user defined limit
    idx = data.index[ data['delta']> delta ]
    # create output list 
    odata = [] 
    if len(idx) == 0:
        odata.append(data.drop(columns=["delta"]))
        last_value = 0
    for i, value in enumerate(idx):
        if i ==0:
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
    pass
    
def market_from_file(ifile: str, format="csv"):
    fmt_choices = ["csv", "list"]
    if not os.path.isfile(ifile):
        logging.warning(f"{path} is not a file, market is not loaded")
        return None
    if format == "csv":
        df = read_csv_market(ifile)
    elif format == "list":
        df = read_list_market(ifile)
    else:
        logging.warning(f"{format} is not an accepted format, market is not loaded. Possible choices: {fmt_choices}")
        return None
    
    # split dataframe if timedelta is too high
    list_df = split_time_df(df, delta=120)
    
    # Create market class
    for data in list_df:
        pass

    # Create all properties

    
        
        
    
def split_time_old(data, delta=60) :
    data['delta'] = (data['time']-data['time'].shift())\
        .fillna(pd.Timedelta(seconds=0)).dt.total_seconds()
    idx = data.index[ data['delta']> delta ].tolist()
    odata = []
    if len(idx) == 0 :
        odata.append(data.drop(columns=['delta']).set_index('time'))
    for i in range(0, len(idx)) :
        if i == 0 :
            odata.append(data.iloc[:idx[i]].drop(columns=['delta']).set_index('time'))
        if i == len(idx)-1 :
            if i != 0 :
                odata.append(data.iloc[idx[i-1]:idx[i]].drop(columns=['delta']).set_index('time'))
            odata.append(data.iloc[idx[-1]:].drop(columns=['delta']).set_index('time'))
        elif i!=0 :
            odata.append(data.iloc[idx[i-1]:idx[i]].drop(columns=["delta"]).set_index('time'))
    return odata