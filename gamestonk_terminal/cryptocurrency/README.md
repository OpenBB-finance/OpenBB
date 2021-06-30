# CRYPTOCURRENCY

This menu aims to explore crypto world, and the usage of the following commands along with an example will be exploited below.

Note that we have added the ability to look at technical analysis in the ta menu.  Data loaded from CoinGecko has no candle data,
so indicators that rely on anything other than close will fail with an error.

[COINGECKO standalone menu](/gamestonk_terminal/cryptocurrency/coingecko/)

[COINMARKETCAP](#COINMARKETCAP)
* [top](#top)
  * view top coins from coinmarketcap [coinmarketcap.com]

[BINANCE](#BINANCE)
* [select](#select)
  * select coin/currency to use
* [book](#book)
  * show order book
* [candle](#candle)
  * get klines/candles and plot
* [balance](#balance)
  * show coin balance

# COINMARKETCAP <a name="COINMARKETCAP"></a>

## top <a name="top"></a>

````
top [-n] [-s --sort SORTBY] [--descend]
````

This command displays the top n cryptocurrencies from coinmarketcap.com.

* -n: Number of coins to look at (after sort).  Defaults to 10.
* -s/--sort : Column to sort by. One of {Symbol,CMC_Rank,LastPrice,DayPctChange,MarketCap}. Defaults to sorting by the CMC rank.
* --descend : Flag to change the sorting order.  Sorts in ascending order (since default order is the Rank which starts at 1).

<img width="990" alt="crypto" src="https://user-images.githubusercontent.com/25267873/115787544-4746d100-a3ba-11eb-9433-b7cb9142404a.png">

# BINANCE <a name="BINANCE"></a>

## select  <a name="select"></a>
````
usage: select [-c --coin] [-q --quote] [-i --interval] [-l --limit]
````

Select a coin/currency to the current object and load in the price dataframe.  Note that in binance, the exchange "ticker" is usually COINCURR, such as BTCEUR for BTC to EURO.  There is no USD, but it uses a coin tethered to the USD (USDT), which is the default. Some symbols are a combination of coins, as `ETHBTC` is a valid symbol
* -c/--coin Coin to load. If not specified, BTC will be loaded to prevent errors later.
* -q/--quote  Quote currency.  Defaults to `USDT` (which is 1-to-1 with USD)
* -i/--interval. Interval for candles.  One of [1day,3day,1hour,2hour,4hour,6hour,8hour,12hour,1week,1min,3min,5min,15min,30min,1month]. Defaults to 1day.
* -l/--limit.  Number of candles to get.  Defaults to 100.

## book  <a name="book"></a>
````
usage: book -l/--limit
````

Gets and shows the order book for the given coin/currency.  Shows the cumulative amount of orders.

* -l/--limit Number of orders to get on each side.  One of [5,10,20,50,100,500,1000,5000].  Defaults to 100.

![orderbook](https://user-images.githubusercontent.com/25267873/116886857-84fcf280-ac21-11eb-9803-5baa8bceca05.png)


## candle  <a name="candle"></a>
````
usage: candle
````

Show candle chart for loaded coin/currency.

![candle](https://user-images.githubusercontent.com/25267873/116886993-abbb2900-ac21-11eb-9ff8-b6a8131fdac5.png)


## balance  <a name="balance"></a>
````
usage: balance
````

Shows the current holding balance in your account.
