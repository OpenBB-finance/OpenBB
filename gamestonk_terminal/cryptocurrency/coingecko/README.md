# CoinGecko

This menu aims to explore crypto world with [CoinGecko](#https://www.coingecko.com/en)
The usage of the following commands along with an example will be exploited below.

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



# COIN <a name="COIN"></a>
## load  <a name="load"></a>

````
usage: load [-c --coin]
````

Load a given coin vs a given currency. Currently only retrieves price, not volume or MarketCap. The current crypto  data is [Powered by CoinGecko API](#https://www.coingecko.com/en), which is an awesome service that currently requires no API Key!

* -c/--coin The coin you wish to load.  This can either be the symbol or the name.  `load -c btc` and `load -c bitcoin`
  will load.  The -c flag is optional,  the above is equivalent to `load btc`.


## chart <a name="chart"></a>

````
usage: chart [-d --days] [--vs]
````

Plot the loaded crypto data.

* -d/--days The number of days to look.  Defaults to 30 days.  As per the API: Minutely data will be used for duration within 1 day,
  Hourly data will be used for duration between 1 day and 90 days, Daily data will be used for duration above 90 days.
* --vs The currency to look against.  Defaults to "usd".

![crypto_view](https://user-images.githubusercontent.com/25267873/115787452-20889a80-a3ba-11eb-9216-f7fd1ffc98cf.png)


## ta <a name="ta"></a>

````
usage: ta [-d --days] [--vs]
````

Open Technical Analysis menu for loaded coin

* -d/--days The number of days to look.  Defaults to 30 days.  As per the API: Minutely data will be used for duration within 1 day,
  Hourly data will be used for duration between 1 day and 90 days, Daily data will be used for duration above 90 days.
* --vs The currency to look against.  Defaults to "usd".

## info <a name="info"></a>

````
usage: info
````

Display basic coin information

![image](https://user-images.githubusercontent.com/275820/123523774-48e88a00-d6c6-11eb-97cf-71529fb209ca.png)

## market <a name="market"></a>

````
usage: market
````

Display coin market basic metrics

![image](https://user-images.githubusercontent.com/275820/123523943-708c2200-d6c7-11eb-97f4-6fb4f7e12c04.png)

## ath <a name="ath"></a>

````
usage: ath
````

Display all time high for loaded coin

![image](https://user-images.githubusercontent.com/275820/123523988-b648ea80-d6c7-11eb-9b08-7d8afecf9231.png)

## atl <a name="atl"></a>

````
usage: atl
````

Display all time low for loaded coin

![image](https://user-images.githubusercontent.com/275820/123523993-c4970680-d6c7-11eb-89ab-3637155e00a9.png)

## score <a name="score"></a>

````
usage: score
````

Display different scores for loaded coin

![image](https://user-images.githubusercontent.com/275820/123524080-3707e680-d6c8-11eb-96e0-106b7a9c00c2.png)

## dev <a name="dev"></a>

````
usage: dev
````

Display coin development stats

![image](https://user-images.githubusercontent.com/275820/123524107-60c10d80-d6c8-11eb-8217-cc767f82d7d9.png)

## web <a name="web"></a>

````
usage: web
````

Display found websites for loaded coin

![image](https://user-images.githubusercontent.com/275820/123524127-720a1a00-d6c8-11eb-9a63-ec4cef42c43f.png)

## social <a name="social"></a>

````
usage: social
````

Display social media for loaded coin

![image](https://user-images.githubusercontent.com/275820/123524140-949c3300-d6c8-11eb-9fb7-1d7a3a084c88.png)

## bc <a name="bc"></a>

````
usage: bc
````

Display blockchain explorers urls for loaded coin

![image](https://user-images.githubusercontent.com/275820/123524154-b5fd1f00-d6c8-11eb-9ec0-1fd1803db422.png)


# OVERVIEW <a name="OVERVIEW"></a>
## global  <a name="global"></a>

````
usage: global
````

Shows basic statistics about crypto market like: market cap change, number of markets, icos, number of active crypto, market_cap_pct

![image](https://user-images.githubusercontent.com/275820/123538175-d1514400-d733-11eb-9634-09c341f63cb9.png)


## coins <a name="coins"></a>

````
usage: coins [-s --skpi] [--l --limit]
````

Display all available coins in coingecko

* -s/--skip The number of records to skip.  Defaults to 0. There are thousands of coins, so there is mechanism to paginate through them. e.q if you want to see only records from 500-750 you should use `coins --skip 500 --limit 250` or if you want to see 1200-1880 you should use `coins --skip 1200 --limit 680`. In future there will be option to search by letter.
* -l/--limit Limit of records to display. Default 500. 

![image](https://user-images.githubusercontent.com/275820/123538885-26428980-d737-11eb-9418-e3f80511786d.png)


## defi <a name="defi"></a>

````
usage: defi
````

Shows basic statistics about Decentralized Finance crypto space. 

![image](https://user-images.githubusercontent.com/275820/123538414-188c0480-d735-11eb-8395-f9bd2f1ef96c.png)


## trending <a name="trending"></a>

````
usage: trending
````

Shows most trending coins on CoinGecko

![image](https://user-images.githubusercontent.com/275820/123538474-5e48cd00-d735-11eb-9619-31e50a677033.png)

## most_voted <a name="most_voted"></a>

````
usage: most_voted
````

Shows most voted coins on CoinGecko 

![image](https://user-images.githubusercontent.com/275820/123538516-8cc6a800-d735-11eb-85ee-e3f2141a54fb.png)

## most_visited <a name="most_visited"></a>

````
usage: most_visited
````

Shows most visited coins on CoinGecko

![image](https://user-images.githubusercontent.com/275820/123538524-9cde8780-d735-11eb-9827-c02ea8bd5db7.png)

## sentiment <a name="sentiment"></a>

````
usage: sentiment
````

Shows coins with the most positive sentiment on CoinGecko 

![image](https://user-images.githubusercontent.com/275820/123538553-c5ff1800-d735-11eb-9fef-ef490184c6d8.png)

## recently <a name="recently"></a>

````
usage: recently
````

Shows coins which were recenlty added on CoinGecko

![image](https://user-images.githubusercontent.com/275820/123538777-a9171480-d736-11eb-9950-efa4946f4be9.png)

## top_volume <a name="top_volume"></a>

````
usage: top_volume
````

Shows coins with the highest transactions volume on CoinGecko

![image](https://user-images.githubusercontent.com/275820/123538841-fa270880-d736-11eb-9f64-d972c648da58.png)


## gainers <a name="gainers"></a>

````
usage: gainers [-p --period]
````

Shows largest gainers - coins which gain the most in given period. Available time priods are: "1h", "24h", "7d", "14d", "30d", "60d", "1y". 
For example if you want to see top gainers in last 24h: `gainers --period 24h`, or in last 60 days: `gainers --period 60d`

![image](https://user-images.githubusercontent.com/275820/123538914-50944700-d737-11eb-896c-b1173b2ab972.png)

## losers <a name="losers"></a>

````
usage: losers [-p --period]
````

Shows largest losers - coins which lost the most in given period. Available time priods are: "1h", "24h", "7d", "14d", "30d", "60d", "1y". 
For example if you want to see top losers in last 24h: `losers --period 24h`, or in last 60 days: `losers --period 60d`

![image](https://user-images.githubusercontent.com/275820/123539004-cdbfbc00-d737-11eb-908a-a0bce9c0b5a4.png)

## stables <a name="stables"></a>

````
usage: stables
````

Shows stable coins information

![image](https://user-images.githubusercontent.com/275820/123539032-fe9ff100-d737-11eb-9518-ebf3e1190c5b.png)


## yfarms <a name="yfarms"></a>

````
usage: yfarms
````

Shows Top Yield Farming Pools by Value Locked from https://www.coingecko.com/en/yield-farming

![image](https://user-images.githubusercontent.com/275820/123539067-2db66280-d738-11eb-811e-70256c82da00.png)

## top_defi <a name="top_defi"></a>

````
usage: top_defi
````

Shows Top 100 DeFi Coins by Market Capitalization from https://www.coingecko.com/en/defi
DeFi or Decentralized Finance refers to financial services that are built on top of distributed networks with no central intermediaries.

![image](https://user-images.githubusercontent.com/275820/123539104-58a0b680-d738-11eb-9f4c-6f4e4ccb03c0.png)

## top_dex <a name="top_dex"></a>

````
usage: top_dex
````

Shows Top Decentralized Exchanges on CoinGecko by Trading Volume from https://www.coingecko.com/en/dex

![image](https://user-images.githubusercontent.com/275820/123539124-6eae7700-d738-11eb-9e74-c4542883a762.png)

## top_nft <a name="top_nft"></a>

````
usage: top_nft
````

Shows Top 100 NFT Coins by Market Capitalization from https://www.coingecko.com/en/nft
NFT (Non-fungible Token) refers to digital assets with unique characteristics.
Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

![image](https://user-images.githubusercontent.com/275820/123539187-b7fec680-d738-11eb-99b6-2f6a0a9673c1.png)

