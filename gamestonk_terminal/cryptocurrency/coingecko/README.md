# CoinGecko

This menu aims to explore crypto world, and the usage of the following commands along with an example will be exploited below.

Note that we have added the ability to look at technical analysis in the ta menu.  Data loaded from CoinGecko has no candle data,
so indicators that rely on anything other than close will fail with an error.

[coin](#coin)
* [load](#load)
  * load a given coin, you can use either coin symbol or coin id
* [clear](#clear)
  * clear loaded coin
* [chart](#chart)
  * plot the loaded crypto chart
* [ta](technical_analysis/README.md)
  * open technical analysis menu
* [info](#info)
  * show coin base information
* [market](#market)
  * show market data
* [ath](#ath)
  * show all time high related metrics
* [atl](#atl)
  * show all time low related metrics
* [score](#score)
  * show different scores related to loaded coin
* [web](#web)
  * show websites related to loaded coin
* [social](#social)
  * show social media urls for loaded coin
* [bc](#bc)
  * show block-chain explorers urls for loaded coins
* [dev](#dev)
  * show developers data for loaded coins

[overview](#overview)
* [top](#top)
  * view top coins from coinmarketcap [coinmarketcap.com]
* [global](#global)
  * show global crypto market info
* [coins](#coins)
   * show coins available on CoinGecko
* [defi](#defi)
  * show global DeFi market info
* [trending](#trending)
  * show trending coins on CoinGecko
* [most_voted](#most_voted)
  * show most voted coins on CoinGecko
* [top_volume](#top_volume)
  * show coins with highest volume on CoinGecko
* [recently](#recently)
  * show recently added on CoinGecko
* [sentiment](#sentiment)
  * show coins with most positive sentiment
* [gainers](#gainers)
  * show top gainers - coins which price gained the most in given period
* [losers](#losers)
  * show top losers - coins which price dropped the most in given period
* [stables](#stables)
  * show Stable Coins
* [yfarms](#yfarms)
  * show top Yield Farms
* [top_defi](#top_defi)
  * show top DeFi Protocols
* [top_dex](#top_dex)
  * show top Decentralized Exchanges
* [top_nft](#top_nft)
  * show top Non Fungible Tokens
* [nft_today](#nft_today)
  * show NFT Of The Day
* [nft_market](#nft_market)
  * show NFT Market Status
* [exchanges](#exchanges)
  * show Top Crypto Exchanges
* [ex_rates](#ex_rates)
  * show Coin Exchange Rates
* [platforms](#platforms)
  * show Crypto Financial Platforms
* [products](#products)
  * show Crypto Financial Products
* [indexes](#indexes)
  * show Crypto Indexes
* [derivatives](#derivatives)
  * show Crypto Derivatives
* [categories](#categories)
  * show Crypto Categories
* [hold](#hold)
  * show eth, btc holdings overview statistics
* [hold_comp](#hold_comp)
  * show eth, btc holdings by public companies



# COINGECKO <a name="COINGECKO"></a>
## load  <a name="load"></a>

````
usage: load [-c --coin]
````

Load a given coin vs a given currency. Currently only retrieves price, not volume or MarketCap. The current crypto  data is [Powered by CoinGecko API](#https://www.coingecko.com/en), which is an awesome service that currently requires no API Key!

* -c/--coin The coin you wish to load.  This can either be the symbol or the name.  `load -c btc` and `load -c bitcoin`
  will load.  The -c flag is optional,  the above is equivalent to `load btc`.


## chart <a name="view"></a>

````
usage: chart [-d --days] [--vs]
````

Plot the loaded crypto data.

* -d/--days The number of days to look.  Defaults to 30 days.  As per the API: Minutely data will be used for duration within 1 day,
  Hourly data will be used for duration between 1 day and 90 days, Daily data will be used for duration above 90 days.
* --vs The currency to look against.  Defaults to "usd".

![crypto_view](https://user-images.githubusercontent.com/25267873/115787452-20889a80-a3ba-11eb-9216-f7fd1ffc98cf.png)
