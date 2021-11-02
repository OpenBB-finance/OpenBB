# BROKERS

This page shows the available brokers for loading your holdings.  If yours is not listed, please submit a new issue and
we will look into adding it.

Current brokers:

* rh : Robinhood
* ally: Ally
* dg : Degiro

Once this screen is accessed, the first command to be run is

```text
login [brokers]
```

The brokers should just be your brokers from the list shown on the first menu.  To login to Robinhood, the command is

```text
login rh
```

To login to both robinhood and alpaca:

```text
login rh alp
```

After logging in, the help menu will display which brokers you logged into.

Your  login information should be stored as environment variables in [config file](/gamestonk_terminal/config_terminal.py),
but check each individual section for specifics.

[ROBINHOOD](#ROBINHOOD)

* [rhhold](#rhhold)
  * Look at current (stock only) holdings
* [rhhist](#rhhist)
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

**NOTE** THAT LOGGING IN WILL SAVE A TOKEN TO `os.path.expanduser("~")/.tokens` WHICH CAN BE USED TO LOGIN EVEN IF USER
CREDENTIALS ARE INCORRECT.

In order to login, the [config file](/gamestonk_terminal/config_terminal.py) requires two variables:

* "GT_RH_USERNAME"
* "GT_RH_PASSWORD"

### rhhold <a name="rhhold"></a>

Displays current holdings to the console:

```text
usage: rhhold
```

There are no additional flags.  This just prints all current stonks, their last price, previous close, your equity and
the % change from previous close.

Example:

![hold](https://user-images.githubusercontent.com/18151143/111685384-3c6ab080-87fe-11eb-80ce-9b256c396bf2.png)

### rhhist <a name="rhhist"></a>

Display your RH portfolio based on provided interval and span.  Based on the API data availability, plotted as a
candlestick chart.

```text
usage: rhhist [-s --span] [-i --interval]
```

* -s/--span : How long to look back.  Defaults to the day. Options:
  * [day, week, month, 3month, year, 5year, all]
* -i/--interval: Data resolution. Defaults to 10minute intervals. Options:
  * [5minute, 10minute, hour, day, week]

Example Default Output:

![rhhist](https://user-images.githubusercontent.com/18151143/111718919-36da8e00-8831-11eb-99e1-957c8eccb583.png)

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

```text
usage : allyhold
```

No additional flags.

## Merge <a name="Merge"></a>

When logged into 1 or more brokers - this option is available.  Currently, this allows for
viewing holding across all platforms.  The PnL is shown for all time (Market Value and your Cost Basis)

### hold <a name = "hold"></a>

Show holdings across all brokers that are logged in.

```text
usage: hold
```

Currently no additional flags.  If not all brokers are represented, double check that they are logged in.
