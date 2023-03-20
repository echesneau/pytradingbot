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
from pytradingbot.cores import properties

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


@pytest.mark.order(7)
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


@pytest.mark.order(8)
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


@pytest.mark.order(9)
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


@pytest.mark.order(10)
def test_split_data(market_two_days_missingdata_path):
    df_market = market_from_file(market_two_days_missingdata_path, fmt="csv")
    assert len(df_market) == 2

    # check last value and first are different
    tend = df_market[0].dataframe().iloc[-1].name  # to get the index of the dataframe
    tstart = df_market[1].dataframe().iloc[0].name
    assert tend != tstart

    # Check delta
    for market in df_market:
        delta = market.dataframe().index.to_series().diff().dt.total_seconds().fillna(0)
        assert delta.max() < 120


@pytest.mark.order(20)
def test_analyse():
    assert True
    

@pytest.mark.order(21)
def test_get_all_child(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    prop_1 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 7})
    prop_2 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 13})
    prop_3 = properties.Derivative(market=market, parent=prop_1)
    child = market._get_all_child()
    
    assert len(child) == 6
    assert isinstance(child[0], properties.AskLoad)
    assert isinstance(child[1], properties.BidLoad)
    assert isinstance(child[2], properties.VolumeLoad)
    
    
@pytest.mark.order(23)
def test_analyse(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    size = len(market.ask.data)
    prop_1 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 7})
    prop_2 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 13})
    prop_3 = properties.Derivative(market=market, parent=prop_1)
    market.analyse()
    
    for prop in market._get_all_child():
        assert len(prop.data) == size


@pytest.mark.order(22)
def test_find_property_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    prop_1 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 7})
    prop_2 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 13})
    assert market.find_property_by_name("EMA_k-7_ask") == prop_1
    assert market.find_property_by_name("EMA_k-7_ask") != prop_2
    assert market.find_property_by_name("EMA_k-13_ask") == prop_2
    assert market.find_property_by_name("EMA_k-13_ask") != prop_1


@pytest.mark.order(23)
def test_is_property(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    prop_1 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 7})
    prop_2 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 13})
    assert market.is_property(prop_1)
    assert market.is_property(prop_2)


@pytest.mark.order(24)
def test_is_property_by_name(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    prop_1 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 7})
    prop_2 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 13})
    assert market.is_property_by_name("EMA_k-7_ask")
    assert market.is_property_by_name("EMA_k-13_ask")
    assert not market.is_property_by_name("EMA_k-20_ask")


@pytest.mark.order(25)
def test_find_property_by_type(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    prop_1 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 7})
    prop_2 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 13})
    assert market.find_property_by_type("EMA") in [prop_1, prop_2]
    assert market.find_property_by_type("market") in [market.volume, market.ask, market.bid]


@pytest.mark.order(26)
def test_find_properties_by_type(market_one_day_path):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    prop_1 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 7})
    prop_2 = properties.ExponentialMovingAverage(market=market, parent=market.ask, param={'k': 13})
    assert len(market.find_properties_by_type('EMA')) == 2
    assert len(market.find_properties_by_type('MA')) == 0
    assert len(market.find_properties_by_type('market')) == 3

def test_generate_properties_from_inputs_file(inputs_config_path, market_one_day_path, caplog):
    market = market_from_file(market_one_day_path, fmt='csv')[0]
    market.generate_property_from_xml_config(inputs_config_path)
    assert len(market._get_all_child()) > 3
    for property in ["deriv_EMA_k-20_ask", "macd_k-5_long_MA_k-13_ask_short_MA_k-7_ask",
                     "bollinger_k-2_data_ask_mean_MA_k-10_ask_std_std_k-10_ask"]:
        assert market.is_property_by_name(property)