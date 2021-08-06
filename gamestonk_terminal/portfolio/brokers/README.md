# BROKERS

This page shows the available brokers for loading your holdings.  If yours is not listed, please submit a new issue and we will look into adding it.

Current brokers:
* rh : Robinhood
* alp : Alpaca
* ally: Ally
* dg : Degiro


Once this screen is accessed, the first command to be run is
````
login [brokers]
````

The brokers should just be your brokers from the list shown on the first menu.  To login to Robinhood, the command is
````
login rh
````
To login to both robinhood and alpaca:
````
login rh alp
````
After logging in, the help menu will display which brokers you logged into.

Your  login information should be stored as environment variables in [config file](/gamestonk_terminal/config_terminal.py), but check each individual section for specifics.

[ROBINHOOD](#ROBINHOOD)
* [rhhold](#rhhold)
    * Look at current (stock only) holdings
* [rhhist](#rhhist)
    * Get and plot historical portfolio

[ALPACA](#ALPACA)
* [alphold](#alphold)
    * Look at current (stock only) holdings
* [alphist](#rhhist)
    * Get and plot historical portfolio

[ALLY](#ALLY)
* [allyhold](#allyhold)
  * Look at Ally Invest Holdings

[DEGIRO standalone menu](/gamestonk_terminal/brokers/degiro/)

[Merge](#Merge)
* [hold](#hold)
  * View holdings across all brokers


## ROBINHOOD <a name="ROBINHOOD"></a>
Robinhood has Two Factor Authentication, so you will likely be prompted to enter a code that is texted/emailed to you.
###NOTE THAT LOGGING IN WILL SAVE A TOKEN TO `os.path.expanduser("~")/.tokens` WHICH CAN BE USED TO LOGIN EVEN IF USER CREDENTIALS ARE INCORRECT.

In order to login, the [config file](/gamestonk_terminal/config_terminal.py) requires two variables:
* "GT_RH_USERNAME"
* "GT_RH_PASSWORD"

### rhhold <a name="rhhold"></a>

Displays current holdings to the console:

````
usage: rhhold
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


## ALPACA <a name="ALPACA"></a>

Alpaca has a nicely maintained python API that is used here.  To login, the best approach is to just save the following environment variables:
* "APCA_API_BASE_URL"
* "APCA_API_KEY_ID"
* "APCA_API_SECRET_KEY"

If these are defined, then the login command does not explicitly need to be run, but the login command verifies all those keys are defined.

Note that alpaca does support paper trading, so if your base_url is "https://paper-api.alpaca.markets", then this will be importing
your paper trading account.

### alphold <a name="alphold"></a>

Displays current holdings to the console.  Same as rhhold

````
usage: alphold
````
There are no additional flags.  This just prints all current stonks, their last price, previous close, your equity and
the % change from previous close.

Example Output:
![](https://user-images.githubusercontent.com/18151143/112039340-536d1380-8b1a-11eb-99d1-44d1edd4d54a.png)

### alphist <a name="alphist"></a>
Plots historical portfolio.  The output plot in this case will not be a candle, as the api provides your equity at a gven time,
unlike the robin_stocks, which gives high/low at a given time.

````
usage: alphist [-p --period] [-t --timeframe]
````

* -p/--period The duration of the data in \<number> + \<unit>, such as 1D, where <unit> can be D for day, W for week, M for month and A for year. Defaults to 1M
* -t/--timeframe The resolution of time window. 1Min, 5Min, 15Min, 1H, or 1D. If omitted, 1Min for less than 7 days period, 15Min for less than 30 days, or otherwise 1D.


## ALLY <a name="ALLY"></a>

In order to access your Ally Invest account through the API, you must first acquire a key from
[your Ally Invest Account](#https://www.ally.com/api/invest/documentation/getting-started/).

Once you have this, you want to load in the following environment variables (similar to alpaca, the api will access these
directly from the environment)
* ALLY_CONSUMER_KEY
* ALLY_CONSUMER_SECRET
* ALLY_OAUTH_TOKEN
* ALLY_OAUTH_SECRET
* ALLY_ACCOUNT_NBR
  * This is obtained from your actual account - not through the api application.

As of writing this, the ally API does not provide historical portfolio data, so only a holdings option is provided.
### allyhold <a name="allyhold"></a>
Show all Ally Invest holdings:
````
usage : allyhold
````
No additional flags.


## Merge <a name="Merge"></a>

When logged into 1 or more brokers - this option is available.  Currently, this allows for
viewing holding across all platforms.  The PnL is shown for all time (Market Value and your Cost Basis)

### hold <a name = "hold"></a>

Show holdings across all brokers that are logged in.
````
usage: hold
````
Currently no additional flags.  If not all brokers are represented, double check that they are logged in.
