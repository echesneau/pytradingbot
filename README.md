# pytradingbot
A Python Trading bot  
This project is in development : not stable yet

# Versions
## v0.1
This version allows to get market via Kraken API in real time and to save it in a CSV file.

# Installation
all required packages are listed in the setup file and in requierements.txt file.  
Tradingbot module and all required package are installed by
>pip install -e . --user  
To verify that installation is correctly done please run all tests. All of them should pass.  
More informations about tests are available in tests section of this file.  

# Documentation
Some documentations are available in the docs directory.  
To generate the file use:
>make htlm  

# Tests
Few tests are creating to check the normal comportment of the code.  
Please run all of them before using pytradingbot.  
To run tests, you should modify the conftest.py file to specify your username for the connection.  
You should also give a id.config file in the project directory. More informations about this file are available in the id.config section.  

# id.config
This file contains users and password to use in order to connect to the trading service.
The format of this file could be found in data/inputs/id.config.example.  
It contains a username and the private key for kraken connection.  
The username is then use in API classes to establish connection.  

# config.xml
This file contains all parameters used for the trading.  
An example are available in inputs directory.

# Exemples
To have some usage examples, you can see all tests of api and market.  
The script launch_get_market.py is an example of script to get market in real time and to save it in a CSV file.
