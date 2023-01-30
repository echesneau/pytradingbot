# =================
# Python IMPORTS
# =================
import numpy as np
import pandas as pd

# =================
# Internal IMPORTS
# =================

# =================
# Variables
# =================


def derivative(data: pd.Series) -> pd.Series:
    # Difference
    odata = data.diff()

    # normalize to minute
    time = data.index.to_series().diff().dt.total_seconds()/60
    odata /= time

    # normalize in %
    odata = odata / data * 100
    return odata
