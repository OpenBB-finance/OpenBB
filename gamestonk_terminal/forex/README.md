# Forex

This menu utilizes oanda to enable support for trading forex.

* [summary](#summary)
	* Display a summary of your account
* [calendar](#calendar)
	* Get information about past or upcoming events which may impact the price
* [list](#list)
	* List your order history
* [pending](#pending)
	* Get information about pending orders
* [cancel](#cancel)
	* Cancel a pending order by ID
* [positions](#positions)
	* Get information about your positions
* [trades](#trades)
	* See a list of open trades
* [closetrade](#closetrade)
	* Close a trade by ID
* [load](#load)
	* Specify an instrument to use
* [candles](#candles)
	* Get a candlestick chart for the forex instrument
* [price](#price)
	* Show the current price for the forex instrument
* [order](#order)
	* Place a limit order
* [orderbook](#orderbook)
	* Display the orderbook if Oanda provides one for the forex instrument
* [positionbook](#positionbook)
 * Display the positionbook if Oanda provides one for the forex instrument

## summary <a name ="summary"></a>
 ```text
 usage: summary
 ```

 Displays current balance, net asset value, unrealized P/L, total P/L, count of open trades, how much margin is available, how much margin you've used, the margin call value, the percent of margin until closeout, and the total position value.

## calendar <a name="calenar"></a>

```text
usage: calendar [-d DAYS]
```

Display information about past or upcoming events up to 30 days before or from todays date. The information includes the Title of the event, the time the event is scheduled, the rated impact, Oanda's forecast, the market forecast, the currency involved, the region from which the event originates, the actual value (for events that have finished), and the previous value.

* -d : The number of days to search (7 is the default, 30 is the maximum that information is provided for). Use a positive value to search for upcoming events and a negative value to search for past events.

## list <a name="list"></a>
```text
usage: list [-s STATE] [-c COUNT]
```

Retrieves a list of orders you've made. It includes the ID, the instrument, the number of units, the price, the state of the order, and the type of order.

* -s : The state of the orders to filter. You can specify: pending, filled, triggered, canceled or all. (default=all)
* -c : The number of orders to retrieve. (default = 20)

## pending <a name="pending"></a>
```text
usage: pending
```
A shortcut to list the pending orders for your account. It includes the ID, the instrument, the price, the number of units, the time the order was created and the time in force.

## cancel <a name="cancel"></a>
```text
usage: cancel [-i ORDERID]
```

Cancel a pending order by its order ID.

* -i : Specify the order ID. You don't need to include this, simply include the order number.

##positions <a name="positions"></a>
```text
usage: positions
```

Lists your open positions. The information includes the instrument, the current number of long units, the total profit/loss from long positions for the account, the unrealized profit/loss from long positions, the current number of short units, the total profit/loss from short positions for the account, and the unrealized profit/loss from short positions.

##trades <a name="trades"></a>
```text
usage: trades
```

Lists the current open trades for your account. The information includes the ID, the instrument, the initial units opened for the trade, the current number of units open for the trade, it's entry price, and the unrealized profit/loss for the trade.

##closetrade <a name="closetrade"></a>
```text
usage: closetrade [-i ORDERID] [-u UNITS]
```

Closes a trade by ID. Displays the order ID closed, the instrument, the number of units that were closed, the price, and the profit/loss

* -i : Specify the order ID. You don't need to include this, simply include the order number.
* -u : Specify the number of units to close for that trade. (default=all)

##load <a name="load"></a>
```text
usage: load [-i INSTRUMENT]
```

Specify the instrument to use in the format EUR_USD

* -i : Specify the instrument. You don't need to include this, simply include the instrument.

##candles <a name="candles"></a>
```text
usage: candles [-g GRANULARITY] [-c CANDLECOUNT]
```

Retrieve a candlestick chart for the currently loaded instrument. Not a live chart.

* -g : Specify the granularity, which is the timeframe each candle represents. The available granularities are Seconds: S5, S10, S15, S30 Minutes: M1, M2, M4, M5, M10, M15, M30 Hours: H1, H2, H3, H4, H6, H8, H12 Day: D, Week: W Month: M. (default=D)
* -c : Specify the number of candles to retrieve. (default=180)

##price <a name="price"></a>
```text
usage: price
```

Gets the current price for the currently loaded instrument

##order <a name="order"></a>
```text
usage: order -u UNITS -p PRICE
```

Places a limit order for the specified number of units at the specified price. Both arguments are required.

* -u : Specify the number of units for the order.
* -p : Specify the price for the limit order.

##orderbook <a name="orderbook"></a>
```text
usage: orderbook
```
Plots the current orderbook for loaded instrument if one is provided by Oanda. Not a live chart.

##positionbook <a name="positionbook"></a>
```text
usage: positionbook
```
Plots the current positionbook for the loaded instrument if one is provided by Oanda. Not a live chart.
