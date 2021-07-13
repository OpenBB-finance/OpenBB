# Backtesting

This menu aims to apply backtesting strategies regarding a pre-loaded ticker, and the usage of the following commands along with an example will be exploited below. Note that this is currently just a simple logic (i.e price comparisons).  These strategies should not be used immediately and should be researched, improved and further tested on your own.  

* [ema](#ema)
  * buy when price exceeds EMA(l)
* [ema_cross](#ema_cross)    
  * buy when EMA(short) > EMA(long) 
* [rsi](#rsi)
  * buy when RSI < low and sell when RSI > high

NOTE: The current implementation uses the [bt](#http://pmorissette.github.io/bt/index.html) library.

### ema <a name="ema"></a>
````
usage: ema [-l] [--spy] [--no_bench]
````

This strategy buys when price > EMA(l).
* -l: Period of EMA to use.  Default = 20.
* [--spy]: Flag that overlays the results if you buy and hold SPY
* [--no_bench]: Flag that removes the benchmark comparison of just buy and hold the stock.

![ema](https://user-images.githubusercontent.com/25267873/116769584-1eb37c80-aa35-11eb-898b-efa36d4a8f5c.png)
<img width="983" alt="ema2" src="https://user-images.githubusercontent.com/25267873/116769582-1d824f80-aa35-11eb-94bd-ecd4abe3b415.png">


### ema_cross <a name="ema_cross"></a>
````
usage: ema_cross [-l] [-s] [--spy] [--no_bench] [--no_short] 
````

This strategy goes long when EMA(short) > EMA(long) and goes short when EMA(short) < EMA(long). It provides the option to go long only through the --no_short flag.
* -l/--long: Long period of EMA to use. Default = 50.
* -s/--short: Short period of EMA to use. Default = 20.
* [--spy]: Flag that overlays the results if you buy and hold SPY
* [--no_bench]: Flag that removes the benchmark comparison of just buy and hold the stock.
* [--no_short]: Flag that removes the shortable option.  Will just be long positions when short > long EMAs.

![ema_cross](https://user-images.githubusercontent.com/25267873/116769581-1ce9b900-aa35-11eb-85e9-133b3c0b09ad.png)
<img width="979" alt="ema_cross2" src="https://user-images.githubusercontent.com/25267873/116769583-1e1ae600-aa35-11eb-9732-9fda8eb2a8b1.png">


### rsi <a name="rsi"></a>
````
usage: rsi [-u] [-l] [-p] [--spy] [--no_bench] [--no_short] 
````

This strategy goes long when the RSI is "oversold" - defined as the low parameter.  It goes short when the RSI is "overbought" - defined as the high (upper) parameter
* -u/--high: High (upper) value  to consider overbought.  Default = 70
* -s/--short: Short period of EMA to use.  Default = 30
* -p/--periods: Periods to use for RSI calculation.  Default = 14.
* [--spy]: Flag that overlays the results if you buy and hold SPY
* [--no_bench]: Flag that removes the benchmark comparison of just buy and hold the stock.
* [--no_short]: Flag that removes the shortable option.  Will just be long positions when short > long EMAs.

![rsi](https://user-images.githubusercontent.com/25267873/116769576-19eec880-aa35-11eb-9e60-f77a31e51db0.png)
<img width="980" alt="rsi2" src="https://user-images.githubusercontent.com/25267873/116769579-1c512280-aa35-11eb-928b-aa4e8b90c1ec.png">
