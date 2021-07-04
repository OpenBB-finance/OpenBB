# CoinGecko

This menu aims to explore crypto world with [CoinGecko](#https://www.coingecko.com/en)
The usage of the following commands along with an example will be exploited below.

Note that we have added the ability to look at technical analysis in the ta menu.  Data loaded from CoinGecko has no candle data,
so indicators that rely on anything other than close will fail with an error.

[COIN](#COIN)
* [load](#load)
  * load a given coin, you can use either coin symbol or coin id
* [find](#find)
  * find similar coin by coin name,symbol or id
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

[OVERVIEW](#OVERVIEW)
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
By loading a coin you will have access to a lot of statistics on that coin like price data, coin development stats, social media and many others. Loading coin also will open access to technical analysis menu


* -c/--coin The coin you wish to load.  This can either be the symbol or the name.  `load -c btc` and `load -c bitcoin`
  will load.  The -c flag is optional,  the above is equivalent to `load btc`.


## chart <a name="chart"></a>

````
usage: chart [-d --days] [--vs]
````

Display chart for loaded coin. You can specify currency vs which you want to show chart and also number of days to get data for.
By default currency: usd and days: 30. E.g. if you loaded in previous step Bitcoin and you want to see it's price vs ethereum in last 90 days range use `chart --vs eth --days 90`


* -d/--days The number of days to look.  Defaults to 30 days.  As per the API: Minutely data will be used for duration within 1 day,
  Hourly data will be used for duration between 1 day and 90 days, Daily data will be used for duration above 90 days.
* --vs The currency to look against.  Defaults to "usd".

![crypto_view](https://user-images.githubusercontent.com/25267873/115787452-20889a80-a3ba-11eb-9216-f7fd1ffc98cf.png)


## ta <a name="ta"></a>

````
usage: ta [-d --days] [--vs]
````

Open Technical Analysis menu for loaded coin
Loads data for technical analysis. You can specify currency vs which you want to show chart and also number of days to get data for.
E.g. if you loaded in previous step Bitcoin and you want to see it's price vs ethereum in last 90 days range use `ta --vs eth --days 90`


* -d/--days The number of days to look.  Defaults to 30 days.  As per the API: Minutely data will be used for duration within 1 day,
  Hourly data will be used for duration between 1 day and 90 days, Daily data will be used for duration above 90 days.
* --vs The currency to look against.  Defaults to "usd".

## info <a name="info"></a>

````
usage: info
````

Shows basic information about loaded coin like: id, name, symbol, asset_platform, description, contract_address, market_cap_rank, public_interest_score, total_supply, max_supply, price_change_percentage_24h, price_change_percentage_7d, price_change_percentage_30d, current_price_btc, current_price_eth, current_price_usd

![image](https://user-images.githubusercontent.com/275820/123523774-48e88a00-d6c6-11eb-97cf-71529fb209ca.png)

## market <a name="market"></a>

````
usage: market
````

Market data for loaded coin. There you find metrics like: market_cap_rank, total_supply, max_supply, circulating_supply, price_change_percentage_24h, price_change_percentage_7d, price_change_percentage_30d, price_change_percentage_60d, price_change_percentage_1y, market_cap_change_24h, market_cap_btc, market_cap_eth, market_cap_usd, total_volume_btc, total_volume_eth, total_volume_usd, high_24h_btc, high_24h_eth, high_24h_usd, low_24h_btc, low_24h_eth, low_24h_usd

![image](https://user-images.githubusercontent.com/275820/123523943-708c2200-d6c7-11eb-97f4-6fb4f7e12c04.png)

## ath <a name="ath"></a>

````
usage: ath
````

All time high data for loaded coin. You can find there most important metrics regarding ath of coin price like: current_price_btc, current_price_eth, current_price_usd, ath_btc, ath_eth, ath_usd, ath_date_btc, ath_date_eth, ath_date_usd, ath_change_percentage_btc, ath_change_percentage_btc, ath_change_percentage_eth, ath_change_percentage_usd

![image](https://user-images.githubusercontent.com/275820/123523988-b648ea80-d6c7-11eb-9b08-7d8afecf9231.png)

## atl <a name="atl"></a>

````
usage: atl
````

All time low data for loaded coin. You can find there most important metrics regarding atl of coin price like: current_price_btc, current_price_eth, current_price_usd, atl_btc, atl_eth, atl_usd, atl_date_btc, atl_date_eth, atl_date_usd, atl_change_percentage_btc, atl_change_percentage_btc, atl_change_percentage_eth, atl_change_percentage_usd

![image](https://user-images.githubusercontent.com/275820/123523993-c4970680-d6c7-11eb-89ab-3637155e00a9.png)

## score <a name="score"></a>

````
usage: score
````

In this view you can find different kind of scores for loaded coin. Those scores represents different rankings, sentiment metrics, some user stats and other, like:  coingecko_rank, coingecko_score, developer_score, community_score, liquidity_score, sentiment_votes_up_percentage, sentiment_votes_down_percentage, public_interest_score, facebook_likes, twitter_followers, reddit_average_posts_48h, reddit_average_comments_48h, reddit_subscribers, reddit_accounts_active_48h, telegram_channel_user_count, alexa_rank, bing_matches

![image](https://user-images.githubusercontent.com/275820/123524080-3707e680-d6c8-11eb-96e0-106b7a9c00c2.png)

## dev <a name="dev"></a>

````
usage: dev
````

Developers data for loaded coin. If the development data is available you can see how the code development of given coin is going on.
There are some statistics that shows number of stars, forks, subscribers, pull requests, commits, merges, contributors on github.

![image](https://user-images.githubusercontent.com/275820/123524107-60c10d80-d6c8-11eb-8217-cc767f82d7d9.png)

## web <a name="web"></a>

````
usage: web
````

Websites found for given Coin. You can find there urls to homepage, forum, announcement site and others.

![image](https://user-images.githubusercontent.com/275820/123524127-720a1a00-d6c8-11eb-9a63-ec4cef42c43f.png)

## social <a name="social"></a>

````
usage: social
````

Display social media corresponding to loaded coin. You can find there name of telegram channel, urls to twitter, reddit, bitcointalk, facebook and discord.

![image](https://user-images.githubusercontent.com/275820/123524140-949c3300-d6c8-11eb-9fb7-1d7a3a084c88.png)

## bc <a name="bc"></a>

````
usage: bc
````

Blockchain explorers URLs for loaded coin. Those are sites like etherescan.io or polkascan.io in which you can see all blockchain data e.g. all txs, all tokens, all contracts...

![image](https://user-images.githubusercontent.com/275820/123524154-b5fd1f00-d6c8-11eb-9ec0-1fd1803db422.png)

## clear <a name="clear"></a>

````
usage: clear
````

Just remove previously loaded coin. (set coin = None)

## find <a name="find"></a>

````
usage: find [-c --coin] [-t --top] [-k --key]
````

Find similar coin by coin name,symbol or id. If you don't remember exact name or id of the Coin at CoinGecko, you can use this command to display coins with similar name, symbol or id to your search query.
Example of usage: coin name is something like "polka". So you can try: `find -c polka -k name -t 25`
It will search for coin that has similar name to polka and display top 25 matches.
* -c, --coin stands for coin - you provide here your search query
* -k, --key it's a searching key. You can search by symbol, id or name of coin
* -t, --top it displays top N number of records.

![image](https://user-images.githubusercontent.com/275820/124304806-8a64b380-db64-11eb-8df1-71d8032b0345.png)


# OVERVIEW <a name="OVERVIEW"></a>
## global  <a name="global"></a>

````
usage: global
````

Display global statistics about Crypto Market like: active_cryptocurrencies, upcoming_icos, ongoing_icos, ended_icos, markets, market_cap_change_percentage_24h,  eth_market_cap_in_pct, btc_market_cap_in_pct, altcoin_market_cap_in_pct

![image](https://user-images.githubusercontent.com/275820/123538175-d1514400-d733-11eb-9634-09c341f63cb9.png)

## news  <a name="news"></a>

````
usage: news [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows latest news from https://www.coingecko.com/en/news. Display columns: index, title, author, posted columns. You can sort by each of column above, using `--sort` parameter and also do it descending with `--descend` flag. It's also possible to display urls to news with `--links` flag. If you want to display top 75 news, sorted by author use `news -t 75 -s author` if you want to see urls to source of the news use `news -t 75 -l`

* -t/--top - number of news to display. One page of news contains 25 news, so to get 250 news script needs to scrape 10 pages (it can take some time). Default 100. E.g `news --top 150`
* -s/--sortby - sort by given column. You can chose on from `index, title, author, posted`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls and display only `index, url` columns

![image](https://user-images.githubusercontent.com/275820/124304537-1e824b00-db64-11eb-946d-4eb28a37bd18.png)

## coins <a name="coins"></a>

````
usage: coins [-s --skip] [-t --top] [-l --letter] [-k --key]
````

Display all available coins in coingecko. You can search with pagination mechanism with `news --skip [num] --top [num]` or you can just search by letter like
`news --letter d --key name --top 10` it will display top 10 matches for coins which name starts with letter `d` and search will be done in column `name`

* -s/--skip - number of records to skip.  Default is 0. There are thousands of coins, so there is mechanism to paginate through them.
e.q if you want to see only records from 500-750 you should use `coins --skip 500 --top 250` or if you want to see 1200-1880 you should use `coins --skip 1200 --top 680`.
* -t/--top - number of news to display. One page of news contains 25 news, so to get 250 news script needs to scrape 10 pages (it can take some time). Default 100. E.g `news --top 150`
* -l/--letter - first letters of coin by which you want to search
* -k/--key - search key. With this parameter you can specify in which column you would like to search. Choose on from `name, id, symbol`

![image](https://user-images.githubusercontent.com/275820/123538885-26428980-d737-11eb-9418-e3f80511786d.png)


## defi <a name="defi"></a>

````
usage: defi
````

Shows global DeFi statistics. DeFi or Decentralized Finance refers to financial services that are built on top of distributed networks with no central intermediaries. Displays metrics like: defi_market_cap, eth_market_cap, defi_to_eth_ratio, trading_volume_24h, defi_dominance, top_coin_name, top_coin_defi_dominance.

![image](https://user-images.githubusercontent.com/275820/123538414-188c0480-d735-11eb-8395-f9bd2f1ef96c.png)


## trending <a name="trending"></a>

````
usage: trending [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows most trending coins on CoinGecko.

* -t/--top - number of coins to display. To display top 10 coins: `trending --top 10`
* -s/--sortby - sort by given column. You can chose on from `rank, name, price_usd, price_btc`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `trending --top 10 --links`

![image](https://user-images.githubusercontent.com/275820/124305015-c8fa6e00-db64-11eb-81de-4e8b943c6c0d.png)

## most_voted <a name="most_voted"></a>

````
usage: most_voted [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows most voted coins on CoinGecko.

* -t/--top - number of coins to display. To display top 10 coins: `most_voted --top 10`
* -s/--sortby - sort by given column. You can chose on from `rank, name, price_usd, price_btc`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `most_voted --top 10 --links`

![image](https://user-images.githubusercontent.com/275820/123538516-8cc6a800-d735-11eb-85ee-e3f2141a54fb.png)

## most_visited <a name="most_visited"></a>

````
usage: most_visited [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows most visited coins on CoinGecko.

* -t/--top - number of coins to display. To display top 10 coins: `most_visited --top 10`
* -s/--sortby - sort by given column. You can chose on from `rank, name, price_usd, price_btc`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `most_visited --top 10 --links`


![image](https://user-images.githubusercontent.com/275820/123538524-9cde8780-d735-11eb-9827-c02ea8bd5db7.png)

## sentiment <a name="sentiment"></a>

````
usage: sentiment [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows coins with the most positive sentiment on CoinGecko

* -t/--top - number of coins to display. To display top 10 coins: `sentiment --top 10`
* -s/--sortby - sort by given column. You can chose on from `rank, name, price_usd, price_btc`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `sentiment --top 10 --links`


![image](https://user-images.githubusercontent.com/275820/123538553-c5ff1800-d735-11eb-9fef-ef490184c6d8.png)

## recently <a name="recently"></a>

````
usage: recently [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows coins which were recently added on CoinGecko

* -t/--top - number of coins to display. To display top 10 coins: `recently --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can chose on from `rank, name, symbol, price, change_24h, change_1h, added`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `recently --top 10 --links`

![image](https://user-images.githubusercontent.com/275820/124305122-f47d5880-db64-11eb-9048-b495248723d3.png)

## top_volume <a name="top_volume"></a>

````
usage: top_volume [-t --top] [-s --sortby] [--descend]
````

Shows coins with the highest transactions volume on CoinGecko

* -t/--top - number of coins to display. To display top 10 coins: `top_volume --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can chose on from `rank, name, symbol, price, change_1h, change_24h, change_7d , volume_24h`
* --descend - flag to sort in descending order (lowest first)

![image](https://user-images.githubusercontent.com/275820/124305188-0a8b1900-db65-11eb-953f-febc32500ff9.png)


## gainers <a name="gainers"></a>

````
usage: gainers [-p --period] [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows largest gainers - coins which gain the most in given period.

* -p/--period - time period in which coins gained the most in price. One from `1h, 24h, 7d, 14d, 30d, 60d, 1y`. If you want to see top gainers in last 24h `gainers -p 24h` or top gainers in last 60days `gainers -p 60d`
* -t/--top - number of coins to display. To display top 10 coins: `gainers --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can chose on from `rank, name, symbol, price, change, volume`.
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `gainers --period 24h --links`

![image](https://user-images.githubusercontent.com/275820/124305218-137bea80-db65-11eb-914c-865b56cf33ea.png)

## losers <a name="losers"></a>

````
usage: losers [-p --period] [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows largest losers - coins which lost the most in given period.

* -p/--period - time period in which coins lost the most in price. One from `1h, 24h, 7d, 14d, 30d, 60d, 1y`. If you want to see top losers in last 24h `losers -p 24h` or top losers in last 60days `losers -p 60d`
* -t/--top - number of coins to display. To display top 10 coins: `losers --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can chose on from `rank, name, symbol, price, change, volume`.
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `losers --period 24h --links`

![image](https://user-images.githubusercontent.com/275820/124305327-3ad2b780-db65-11eb-9922-7783b740312c.png))

## stables <a name="stables"></a>

````
usage: stables [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows stablecoins by market capitalization. Stablecoins are cryptocurrencies that attempt to peg their market value to some external reference
like the U.S. dollar or to a commodity's price such as gold.

* -t/--top - number of coins to display. To display top 10 coins: `stables --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can sort data by `rank, name, symbol, price, change_24h, exchanges, market_cap, change_30d`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `stables --links`. If you will use this flag `rank, name, symbol, url` columns will be displayed.

![image](https://user-images.githubusercontent.com/275820/124305427-62298480-db65-11eb-9216-02cf9690c958.png)


## yfarms <a name="yfarms"></a>

````
usage: yfarms [-t --top] [-s --sortby] [--descend]
````

Shows Top Yield Farming Pools by Value Locked from https://www.coingecko.com/en/yield-farming
Yield farming, also referred to as liquidity mining, is a way to generate rewards with cryptocurrency holdings.
In simple terms, it means locking up cryptocurrencies and getting rewards.

* -t/--top - number of yield farms to display. To display top 10 yield farms: `yfarms --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can sort data by `rank, name, value_locked, return_year`
* --descend - flag to sort in descending order (lowest first)


![image](https://user-images.githubusercontent.com/275820/124305461-6ce41980-db65-11eb-9c82-648f4ff905e8.png)

## top_defi <a name="top_defi"></a>

````
usage: top_defi [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows Top DeFi Coins by Market Capitalization from https://www.coingecko.com/en/defi
DeFi or Decentralized Finance refers to financial services that are built on top of distributed networks with no central intermediaries.

* -t/--top - number of defi coins to display. To display top 10 defi coins: `top_defi --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can sort data by `rank, name, symbol, price, change_24h, change_1h, change_7d`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `top_defi --links`.

![image](https://user-images.githubusercontent.com/275820/124305508-7c636280-db65-11eb-8ae7-38389ac72770.png)

## top_dex <a name="top_dex"></a>

````
usage: top_dex [-t --top] [-s --sortby] [--descend]
````

Shows Top Decentralized Exchanges on CoinGecko by Trading Volume from https://www.coingecko.com/en/dex
Decentralized exchanges or DEXs are autonomous decentralized applications (DApps) that allow cryptocurrency buyers or
sellers to trade without having to give up control over their funds to any intermediary or custodian. Source: [coinmarketcap](#https://coinmarketcap.com/alexandria/article/what-are-decentralized-exchanges-dex)

* -t/--top - number of Decentralized Exchanges to display. To display top 10 DEX: `top_dex --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can sort data by `rank, name, volume_24h, n_coins, n_pairs, visits, most_traded, market_share_by_vol most_traded_pairs, market_share_by_volume`
* --descend - flag to sort in descending order (lowest first)

![image](https://user-images.githubusercontent.com/275820/124305536-84230700-db65-11eb-82bf-ad2d0878135c.png)

## top_nft <a name="top_nft"></a>

````
usage: top_nft [-t --top] [-s --sortby] [--descend] [-l --links]
````

Shows Top 100 NFT Coins by Market Capitalization from https://www.coingecko.com/en/nft
NFT (Non-fungible Token) refers to digital assets with unique characteristics.
Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

* -t/--top - number of NFT to display. To display top 10 NFT Coins: `top_nft --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can sort data by `rank, name, symbol, price, change_24h, change_1h, change_7d, volume_24h, market_cap`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `top_nft --links`.


![image](https://user-images.githubusercontent.com/275820/124305553-8be2ab80-db65-11eb-92a8-86485d2b7ef8.png)

## nft_today <a name="nft_today"></a>

````
usage: nft_today
````
Get Non-fungible Token of the Day. Everyday on CoinGecko there is chosen new NFT. NFT (Non-fungible Token) refers to digital assets with unique characteristics. Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
`nft_today` command you will display: author, description, url, img url.

![image](https://user-images.githubusercontent.com/275820/123539455-2abc7180-d73a-11eb-9b58-160f11d99b44.png)

## nft_market <a name="nft_market"></a>

````
usage: nft_market
````
Get current state of NFTs market. NFT (Non-fungible Token) refers to digital assets with unique characteristics.
Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
`nft_market` will display: NFT Market Cap, 24h Trading Volume, NFT Dominance vs Global market, Theta Network NFT Dominance.

![image](https://user-images.githubusercontent.com/275820/123539514-7838de80-d73a-11eb-8e22-ef3f250d3003.png)


## exchanges <a name="exchanges"></a>

````
usage: exchanges [-t --top] [-s --sortby] [--descend] [-l --links]
````
Shows top crypto exchanges base on trust score.

* -t/--top - number of exchanges to display. To display top 10 exchanges by trust_score: `exchanges --top 10 --sortby trust_score --descend`
* -s/--sortby - sort by given column. You can sort data by `rank, trust_score, id, name, country, established, trade_volume_24h_btc`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `exchanges --links`. Using `links` parameter will display only `rank, name, url` columns

![image](https://user-images.githubusercontent.com/275820/123539542-98689d80-d73a-11eb-9561-2de524d329d0.png)

## ex_rates <a name="ex_rates"></a>

````
usage: ex_rates [-t --top] [-s --sortby] [--descend]
````

Shows list of crypto, fiats, commodity exchange rates from CoinGecko
* -t/--top - number of exchanges to display. To display top 10 exchanges by trust_score: `ex_rates --top 10 --sortby name --descend`
* -s/--sortby - sort by given column. You can sort by `index,name,unit, value, type`
* --descend - flag to sort in descending order (lowest first)

![image](https://user-images.githubusercontent.com/275820/124305586-969d4080-db65-11eb-8cc9-7024ae06758a.png)

## platforms <a name="platforms"></a>

````
usage: platforms [-t --top] [-s --sortby] [--descend]
````
Shows Top Crypto Financial Platforms in which you can borrow or lend your crypto e.g. Celsius, Nexo, Crypto.com, Aave and others.

* -t/--top - number of crypto platforms to display. To display top 10 platforms: `platforms --top 10 --sortby name`
* -s/--sortby - sort by given column. You can sort data by `rank, name, category, centralized`
* --descend - flag to sort in descending order (lowest first)


![image](https://user-images.githubusercontent.com/275820/123539607-e1205680-d73a-11eb-9ab4-b8998ef37731.png)


## products <a name="products"></a>

````
usage: products [-t --top] [-s --sortby] [--descend]
````
Shows Top Crypto Financial Products with which you can earn yield, borrow or lend your crypto.

* -t/--top - number of crypto products to display. To display top 10 products: `products --top 10 --sortby name`
* -s/--sortby - sort by given column. You can sort data by `rank, platform, identifier, supply_rate_percentage, borrow_rate_percentage`
* --descend - flag to sort in descending order (lowest first)

![image](https://user-images.githubusercontent.com/275820/124305624-a583f300-db65-11eb-819d-4bd9961d2a08.png)

## indexes <a name="indexes"></a>

````
usage: indexes [-t --top] [-s --sortby] [--descend]
````

Shows list of crypto indexes from CoinGecko.Each crypto index is made up of a selection of cryptocurrencies, grouped together and weighted by market cap.
* -t/--top - number of crypto indexes to display. To display top 10 indexes: `indexes --top 10 --sortby name`
* -s/--sortby - sort by given column. You can sort data by `rank, name, id, market, last, is_multi_asset_composite`
* --descend - flag to sort in descending order (lowest first)

![image](https://user-images.githubusercontent.com/275820/124305656-afa5f180-db65-11eb-91fc-a9b57e99e690.png)

## derivatives <a name="derivatives"></a>

````
usage: derivatives [-t --top] [-s --sortby] [--descend]
````
Shows list of crypto derivatives from CoinGecko. Crypto derivatives are secondary contracts or financial tools that derive their value from a primary
underlying asset. In this case, the primary asset would be a cryptocurrency such as Bitcoin. The most popular crypto derivatives are crypto futures, crypto options, and perpetual contracts.
* -t/--top - number of crypto derivatives to display. To display top 10 derivatives: `derivatives --top 10 --sortby symbol`
* -s/--sortby - sort by given column. You can sort by `rank, market, symbol, price, pct_change_24h, contract_type, basis, spread, funding_rate, volume_24h`
* --descend - flag to sort in descending order (lowest first)


![image](https://user-images.githubusercontent.com/275820/124305694-b896c300-db65-11eb-9a15-dfd2d1e5832f.png)

## categories <a name="categories"></a>

````
usage: categories [-t --top] [-s --sortby] [--descend] [-l --links]
````
Shows top cryptocurrency categories by market capitalization from https://www.coingecko.com/en/categories
It includes categories like: stablecoins, defi, solana ecosystem, polkadot ecosystem and many others.

* -t/--top - number of crypto categories to display. To display top 10 crypto categories: `categories --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can sort by `rank, name, change_1h, change_24h, change_7d, market_cap, volume_24h, n_of_coins`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `categories --links`. Using `links` parameter will display only `rank, name, url` columns

![image](https://user-images.githubusercontent.com/275820/124305739-c51b1b80-db65-11eb-9f35-6dd1fceb731d.png)


## hold <a name="hold"></a>

````
usage: hold [-c --coin]
````

Shows overview of public companies that holds ethereum or bitcoin
Displays most important metrics like: Total Bitcoin/Ethereum Holdings, Total Value (USD), Public Companies Bitcoin/Ethereum Dominance, Companies.

* -c/--coin - chose a coin. Only available for ethereum or bitcoin. If you want to see overview of public companies that holds ethereum use `hold --coin ethereum` for bitcoin `hold --coin bitcoin`

![image](https://user-images.githubusercontent.com/275820/123539842-f77ae200-d73b-11eb-9d6c-feb2fbd98c01.png)


## hold_comp <a name="hold_comp"></a>

````
usage: hold_comp [-c --coin] [- --links]
````

Shows Ethereum/Bitcoin Holdings by Public Companies. Track publicly traded companies around the world that are buying ethereum as part of corporate treasury

* -c/--coin - chose a coin. Only available for ethereum or bitcoin. List of public companies that holds ethereum  `hold_comp --coin ethereum` for bitcoin `hold_comp --coin bitcoin`
* -l/--links - You can use additional flag `--links` to see urls to announcement about buying btc or eth by given company. In this case of usage `links` only columns `rank, company, url` will be displayed

![image](https://user-images.githubusercontent.com/275820/124305825-e419ad80-db65-11eb-85b4-35f2e163f3fd.png)

