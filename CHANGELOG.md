# Versions
## HEAD
- Add a complete CI
- Add badge in README
This version does not use anymore the id_config file. Now secrets to connect to the api are store
 as environment variables. 
- API_USER
- API_KEY
- API_PRIVATE

## v0.3.2
Fix bug on cross_up_last_n and cross_down_last_n function

## v0.3.1
This version included new conditions:
- CrossUp10
- CroosUp5  
- CrossDown10
- CroosDown5  

These conditions return True if the cross up or the cross down happened in last n (5 or 10) steps.  

## v0.3.0
This version included Order objects to analyse and to decide to buy or sell on a market.
Different object are created : Order, Action and Condition

## v0.2.1
This version add an exception in get_market method to avoid unexpected crash.

## v0.2.0
This version included properties to analyse the market.  
A market could be real time, or loaded.  

## v0.1.0
This version allows to get market via Kraken API in real time and to save it in a CSV file.