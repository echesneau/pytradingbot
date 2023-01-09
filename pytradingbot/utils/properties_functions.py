# =================
# Python IMPORTS
# =================
import pandas as pd

# =================
# Internal IMPORTS
# =================

# =================
# Variables
# =================


def do_nothing(data: dict) -> pd.Series:
    return data.values()[0]
