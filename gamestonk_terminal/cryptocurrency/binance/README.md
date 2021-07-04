# BINANCE

Binance is the largest cryptocurrency exchange in the world in terms of trading volume.
This menu aims to explore Binance API and display data like order book, candles chart, account balance.

## load  <a name="load"></a>
````
usage: load [-c --coin] [-q --quote] [-i --interval] [-l --limit]
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

## ta <a name="ta"></a>

````
usage: ta
````

Open Technical Analysis menu for loaded coin. [technical analysis](/gamestonk_terminal/cryptocurrency/coinmarketcap/)
