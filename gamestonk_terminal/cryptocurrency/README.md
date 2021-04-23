# CRYPTOCURRENCY

This menu aims to explore crypto world, and the usage of the following commands along with an example will be exploited below.

* [load](#load)
  * load a given coin vs a given currency [CoinGecko]
* [view](#view)
  * plot the loaded crypto data
* [top](#top)
  * view top coins from coinmarketcap [coinmarketcap.com] 


## load  <a name="load"></a>

````
usage: load [-c --coin] [-d --days] [--vs]
````

Load a given coin vs a given currency. Currently only retrieves price, not volume or MarketCap. The current crypto  data is [Powered by CoinGecko API](#https://www.coingecko.com/en), which is an awesome service that currently requires no API Key! 

* -c/--coin The coin you wish to load.  This can either be the symbol or the name.  `load -c btc` and `load -c bitcoin` 
  will load.  The -c flag is optional,  the above is equivalent to `load btc`.
* -d/--days The number of days to look.  Defaults to 30 days.  As per the API: Minutely data will be used for duration within 1 day, 
  Hourly data will be used for duration between 1 day and 90 days, Daily data will be used for duration above 90 days.
* --vs The currency to look against.  Defaults to "usd".


## view  <a name="view"></a>

````
usage: view
````

Plot the loaded crypto data.

![crypto_view](https://user-images.githubusercontent.com/25267873/115787452-20889a80-a3ba-11eb-9216-f7fd1ffc98cf.png)


## top <a name="top"></a>

````
top [-n] [-s --sort SORTBY] [--descend]
````

This command displays the top n cryptocurrencies from coinmarketcap.com.

* -n: Number of coins to look at (after sort).  Defaults to 10.
* -s/--sort : Column to sort by. One of {Symbol,CMC_Rank,LastPrice,DayPctChange,MarketCap}. Defaults to sorting by the CMC rank.
* --descend : Flag to change the sorting order.  Sorts in ascending order (since default order is the Rank which starts at 1).

<img width="990" alt="crypto" src="https://user-images.githubusercontent.com/25267873/115787544-4746d100-a3ba-11eb-9433-b7cb9142404a.png">

