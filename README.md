# pytradingbot
A Python Trading bot  
This project is in development : not stable yet

# Status and coverage
| branche | CI status                                                                                                            | Coverage                                                                                                                                                      |  
|---------|----------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| main    | ![Statut CI](https://github.com/echesneau/pytradingbot/actions/workflows/ci.yml/badge.svg?branch=main)               | [![Couverture de code](https://codecov.io/gh/echesneau/pytradingbot/branch/main/graph/badge.svg)](https://codecov.io/gh/echesneau/pytradingbot)               |
| dev     | ![Statut CI](https://github.com/echesneau/pytradingbot/actions/workflows/ci.yml/badge.svg?branch=dev)                | [![Couverture de code](https://codecov.io/gh/echesneau/pytradingbot/branch/dev/graph/badge.svg)](https://codecov.io/gh/echesneau/pytradingbot)                |

# Versions
## last stable
Code is not stable yet

## Code updates
All updates are listed in CHANGELOG.md
 
# Installation
all required packages are listed in the setup file and in requierements.txt file.  
Tradingbot module and all required package are installed by
>pip install -e . --user  

To verify that installation is correctly done please run all tests. All of them should pass.  
More informations about tests are available in tests section of this file.  

# Documentation
Some documentations are available in the docs directory.  
To generate the file use:
>make html

# Tests
Few tests are creating to check the normal comportment of the code.  
Please run all of them before using pytradingbot.  
To run tests, you should modify the conftest.py file to specify your username for the connection.  
You should also give a id.config file in the project directory. More informations about this file are available in the id.config section.

## Activate warnings
> -p no:logging -s  

in the configuration

## Tests coverage 
94% of lines for v0.3.2
94% of lines for v0.3.1
94% of lines for v0.3.0
93% of lines for v0.2.0 

# Environment variables
Users and password to use in order to connect to the trading service are stored in 3 environment variables:
- API_USER: username (optional)
- API_KEY: kraken public key
- API_PRIVATE: kraken private key

# config.xml
This file contains all parameters used for the trading.  
An example are available in inputs directory.
## template
````
<pytradingbot>
    <trading>
        <symbol>XXBT</symbol>
        <pair>XXBTZEUR</pair> <!-- traiding pair -->
        <refresh>5</refresh> <!-- Time (in seconds) between two market update -->
    </trading>
    <market>
        <clean>300</clean> <!-- Maximum number of rows in memory -->
        <odir format="pandas">data/outputs/market</odir> <!-- ouptut directory -->
    </market>
    <analysis>
        <properties>deriv_EMA_k-20_ask</properties> <!-- No format -->
        <properties format="name">macd_k-5_long_MA_k-13_ask_short_MA_k-7_ask</properties>
        <properties format="name">bollinger_k-2_data_ask_mean_MA_k-10_ask_std_std_k-10_ask</properties>
        <properties format="name">MA_k-10_ask</properties>
    </analysis>
    <order>
        <action type="sell">
            <condition function=">" value="0">macd_k-5_long_MA_k-13_ask_short_MA_k-7_ask</condition>
        </action>
        <action type="buy">
            <condition function=">" value="0">macd_k-5_long_MA_k-13_ask_short_MA_k-7_ask</condition>
            <condition function="+=" value="0">deriv_macd_k-5_long_MA_k-13_ask_short_MA_k-7_ask</condition>
            <condition function="<" value="0">deriv_macd_k-5_long_MA_k-13_ask_short_MA_k-7_ask</condition>
        </action>
    </order>
</pytradingbot>
````
# Exemples of uses
To have some usage examples, you can see all tests of api and market.  
The script launch_get_market.py is an example of script to get market in real time and to save it in a CSV file.

# Properties available
## Derivative
Function to calculate derivative of data, normalize to % and to per minute.  
**name format**: deriv_{parent_name}  
where parent name is the name of data on which function is applied.  

## Moving average
Function to calculate moving average of data on a window of size k.  
**name format**: MA_k-{k}_{parent_name}  
where parent name is the name of data on which function is applied and k the size of the window.  

## Exponential moving average
Function to calculate exponential moving average of data on a window of size k.  
**name format**: EMA_k-{k}_{parent_name}  
where parent name is the name of data on which function is applied and k the size of the window.  

## Standard deviation
Function to calculate standard deviation of data on a window of size k.  
**name format**: std_k-{k}_{parent_name}  
where parent name is the name of data on which function is applied and k the size of the window.  

## Variation
Function to calculate variation of data (in percentage) on a window of size k.  
**name format**: variation_k-{k}_{parent_name}  
where parent name is the name of data on which function is applied and k the size of the window.  

## RSI
Function to calculate RSI on a window of size k.  
**name format**: rsi_k-{k}_{parent_name}  
where parent name is the name of data on which function is applied and k the size of the window.  

## MACD
Function to calculate MACD on a window of size k.  
**name format**: macd_k-{k}_long_{parent_long_name}_short_{parent_short_name}  
where parent name is the name of data on which function is applied and k the size of the window.  

## Bollinger
Function to calculate bollinger on a window of size k.  
**name format**: bollinger_k-{k}_data_{parent_name}_mean_{parent_mean_name}_std_{parent_std_name}  
where parent name is the name of data on which function is applied.  

# How to generate properties
## create from class
It is possible to generate property directly calling the class:  
> deriv = Derivative(market=market_obj, parent=Properties)  
> 
> macd = MACD(market=market_obj, parent={"short": parent_short_obj, "long":parent_long_obj}, param={"k": k})

## create from name
Another way to generate properties is to use the function `generate_property_by_name` of properties module.  
> generate_property_by_name(property_name, market_obj)  

This function return of Properties object, but the properties is automatically add to child of market.  

## From input xml file
All properties in the analysis section of the xml input file will be generated and add to market.  