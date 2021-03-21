# PORTFOLIO

This page shows the available brokers for loading in data.  If yours is not listed, please submit a new issue and we will look at adding it.

Current brokers:
* Robinhood


Once this screen is accessed, the first command to be run is 
````
login [brokers]
````

The brokers should just be your brokers from the list shown on the first menu.  To login to Robinhood, the command is 
````
login rh
````
When td is added, the command will be 
````
login rh td
````
After logging in, the help menu will display which brokers you logged into.

Your  login information should be stored as environment variables in [config file](/gamestonk_terminal/config_terminal.py)

Robinhood has Two Factor Authentication, so you will likely be prompted to enter a code that is texted/emailed to you.
###NOTE THAT LOGGING IN WILL SAVE A TOKEN TO `os.path.expanduser("~")/.tokens` WHICH CAN BE USED TO LOGIN EVEN IF USER CREDENTIALS ARE INCORRECT.

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