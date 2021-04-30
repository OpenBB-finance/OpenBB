# Backtesting
The goal of this menu is to allow super simple research into potential strategies.

We currently provides a couple basic options for starting with backtesting strategies.  Note that this is currently just a 
simple logic (i.e price comparisons).  Obviously these strategies should not be used immediately and should be researched, 
improved and further tested on your own.  

The current implementation uses the [bt](#http://pmorissette.github.io/bt/index.html) library.

Current strategies are:
* [Simple EMA](#SimpleEMA)
  * Buys the stock when `price > EMA(l)`
    
* [EMA Cross](#EMA Cross)    
    * Buys when EMA(short) > EMA(long) and sells when the opposite is true
    
* [RSI](#RSI)
    * Momentum strategy that longs when RSI < threshold (oversold) and shorts when

### SimpleEMA <a name="SimpleEMA"></a>
This strategy buys when price > EMA(l)
````
usage: ema [-l] [--spy] [--no_bench]
````
* -l: Period of EMA to use.  Default = 20.
* [--spy]: Flag that overlays the results if you buy and hold SPY
* [--no_bench]: Flag that removes the benchmark comparison of just buy and hold the stock.

im:

### EMA Cross <a name="EMA Cross"></a>
This strategy goes long when EMA(short) > EMA(long) and goes short when 
EMA(short) < EMA(long).  I provide the option to go long only through the --no_short flag

````
usage: ema_cross [-l] [-s] [--spy] [--no_bench] [--no_short] 
````
* -l/--long: Long period of EMA to use. Default = 50.
* -s/--short: Short period of EMA to use. Default = 20.
* [--spy]: Flag that overlays the results if you buy and hold SPY
* [--no_bench]: Flag that removes the benchmark comparison of just buy and hold the stock.
* [--no_short]: Flag that removes the shortable option.  Will just be long positions when short > long EMAs.

im
### RSI <a name="RSI"></a>
This strategy goes long when the RSI is "oversold" - defined as the low parameter.  It goes short when
the RSI is "overbought" - defined as the high (upper) parameter
````
usage: rsi [-u] [-l] [-p] [--spy] [--no_bench] [--no_short] 
````
* -u/--high: High (upper) value  to consider overbought.  Default = 70
* -s/--short: Short period of EMA to use.  Default = 30
* -p/--periods: Periods to use for RSI calculation.  Default = 14.
* [--spy]: Flag that overlays the results if you buy and hold SPY
* [--no_bench]: Flag that removes the benchmark comparison of just buy and hold the stock.
* [--no_short]: Flag that removes the shortable option.  Will just be long positions when short > long EMAs.



