# PORTFOLIO

This page shows the available brokers for loading in data.  If yours is not listed, please submit a new issue and we will look at adding it.


Once this screen is accessed, the first command to be run is 
````
login
````
Which will use your  login information, which should be stored as environment variables in [config file](/gamestonk_terminal/config_terminal.py)

[ROBINHOOD](#ROBINHOOD)
* [hold](#hold)
    * Look at current (stock only) holdings
* [rhhist](#rhhist)
    * Get and plot historical portfolio

## ROBINHOOD <a name="ROBINHOOD"></a>

### hold <a name="hold"></a>

Displays current holdings to the console:

````
usage: hold
````
There are no additional flags.  This just prints all current stonks, their last price, previous close, your equity and
the % change from previous close.

Example:

![hold](https://user-images.githubusercontent.com/18151143/111685384-3c6ab080-87fe-11eb-80ce-9b256c396bf2.png)

### rhhist <a name="rhhist"></a>
Display your RH portfolio based on provided interval and span.  Based on the API data availablility, plotted as a candlestick chart.
````
usage: rhhist [-s --span] [-i --interval]
````
* -s/--span : How long to look back.  Defaults to the day. Options:
    * [day, week, month, 3month, year, 5year, all]
* -i/--interval: Data resolution. Defaults to 10minute intervals. Options:
    * [5minute, 10minute, hour, day, week]
    
Example Default Output:

![rhhist](https://user-images.githubusercontent.com/18151143/111718919-36da8e00-8831-11eb-99e1-957c8eccb583.png)