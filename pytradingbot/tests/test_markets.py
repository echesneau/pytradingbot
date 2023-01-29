# =================
# Python IMPORTS
# =================
import os
import shutil
import pandas as pd
import pytest
from datetime import datetime

# =================
# Internal IMPORTS
# =================
from pytradingbot.iolib.crypto_api import KrakenApiDev
from pytradingbot.cores import markets
from pytradingbot.utils.market_tools import market_from_file

# =================
# Variables
# =================


@pytest.mark.order(5)
def test_create_market():
    api = KrakenApiDev()
    api.set_market(markets.Market(parent=api))
    assert len(api.market.dataframe()) == 0
    assert api.market.ask.name == 'ask'
    assert type(api.market.ask.data) == pd.Series
    assert api.market.ask.data.name == 'ask'
    assert api.market.bid.name == 'bid'
    assert type(api.market.bid.data) == pd.Series
    assert api.market.bid.data.name == 'bid'


@pytest.mark.order(6)
def test_update(kraken_user, inputs_config_path):
    # Init API and Market
    api = KrakenApiDev(user=kraken_user, inputs=inputs_config_path)
    api.set_market(markets.Market(parent=api, odir=f"{api.odir}/{api.pair}", oformat=api.oformat))
    api.connect()

    # Check initial state of Market
    assert len(api.market.ask.data) == 0
    assert len(api.market.bid.data) == 0
    assert len(api.market.volume.data) == 0
    assert api.market.bid.data.name == 'bid'
    assert api.market.ask.data.name == 'ask'
    assert api.market.volume.data.name == 'volume'
    assert len(api.market.dataframe()) == 0
    for prop in ['ask', 'bid', 'volume']:
        assert prop in api.market.dataframe().columns

    # Check state after updates
    for i in range(3):
        api.update_market()
        assert len(api.market.ask.data) == i+1
        assert len(api.market.bid.data) == i+1
        assert len(api.market.volume.data) == i+1
        assert api.market.bid.data.name == 'bid'
        assert api.market.ask.data.name == 'ask'
        assert api.market.volume.data.name == 'volume'
        assert len(api.market.dataframe()) == i+1
        for prop in ['ask', 'bid', 'volume']:
            assert prop in api.market.dataframe().columns


def test_save_market(kraken_user, inputs_config_path):
    # Init API and Market
    api = KrakenApiDev(user=kraken_user, inputs=inputs_config_path)

    # remove output if exists
    if os.path.isdir(f"{api.odir}/{api.pair}"):
        shutil.rmtree(f"{api.odir}/{api.pair}")

    # Set market
    api.set_market(markets.Market(parent=api, odir=f"{api.odir}/{api.pair}", oformat=api.oformat))
    api.connect()

    # Check if odir and oformat are correctly set
    assert api.market.odir == f'data/outputs/market/{api.pair}'
    assert api.market.oformat == "pandas"

    # check 3 times
    now = datetime.now().date()
    for i in range(3):
        # Generate file
        api.update_market()
        api.market.save()

        # Check if file exists
        assert os.path.isdir(f"{api.odir}/{api.pair}")
        assert os.path.isfile(f"{api.odir}/{api.pair}/{now}.dat")

        # check length of file
        tmp = pd.read_csv(f"{api.odir}/{api.pair}/{now}.dat", index_col=0, sep=" ")
        assert len(tmp) == i+1


def test_clean_market(kraken_user, inputs_config_path):
    nsteps = 5
    # Init API and Market
    api = KrakenApiDev(user=kraken_user, inputs=inputs_config_path)
    # api.set_market(markets.Market(parent=api, odir=f"{api.odir}/{api.pair}", oformat=api.oformat))
    api.connect()

    # set fast update
    api.refresh = 1

    # Run n steps
    api.run(times=nsteps)

    # set maximum number of rows in Market
    api.market.set_maximum_rows(2)
    assert api.market.nclean == 2

    # check number of rows before cleaning
    assert len(api.market.dataframe()) == nsteps
    last = api.market.dataframe().index[-1]

    # check number of rows after cleaning
    api.market.clean()
    assert len(api.market.dataframe()) == 2
    assert api.market.dataframe().index[-1] == last


def test_load_data(market_one_day_path, market_two_days_list):
    # check read from csv
    df_market = market_from_file(market_one_day_path, fmt="csv")
    assert len(df_market) == 1
    market = df_market[0]
    assert type(market) == markets.MarketLoad
    for prop in ['ask', 'bid', 'volume']:
        assert hasattr(market, prop)
    assert len(market.dataframe()) > 0
    assert (len(market.ask.data) == len(market.bid.data)) & (len(market.ask.data) == len(market.volume.data))
    assert len(market.ask.data) > 0

    # check read from list
    df_market = market_from_file(market_two_days_list, fmt="list")
    assert len(df_market) == 1
    market = df_market[0]
    assert type(market) == markets.MarketLoad
    for prop in ['ask', 'bid', 'volume']:
        assert hasattr(market, prop)
    assert len(market.dataframe()) > 0
    assert (len(market.ask.data) == len(market.bid.data)) & (len(market.ask.data) == len(market.volume.data))
    assert len(market.ask.data) > 0


def test_split_data(market_two_days_missingdata_path):
    df_market = market_from_file(market_two_days_missingdata_path, fmt="csv")
    # check last value and first are different

def test_analyse():
    assert True


if __name__ == "__main__":
    market_one_day_path = 'data/XXBTZEUR_1day.dat'
    market_two_days_missingdata_path = 'data/XXBTZEUR_2days_datamissing.dat'

    test_load_data(market_two_days_missingdata_path)
