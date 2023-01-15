# =================
# Python IMPORTS
# =================
import logging
import pandas as pd

# =================
# Internal IMPORTS
# =================

# =================
# Variables
# =================

def split_time(data, delta=60) :
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