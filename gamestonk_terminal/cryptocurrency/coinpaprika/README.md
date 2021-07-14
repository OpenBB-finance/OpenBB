# Coinpaprika

This menu aims to explore crypto world with [Coinpaprika](#https://coinpaprika.com/)
The usage of the following commands along with an example will be exploited below.

Coinpaprika research platform was founded in April 2018. Coinpaprika mission is to provide comprehensive, reliable, transparent
and objective access to information about crypto projects from all around the world. [Source: See https://coinpaprika.com/about-us/]


[COIN](#COIN)
* [find](#find)
  * find similar coin by coin name,symbol or id
* [load](#load)
  * load a given coin, you can use either coin symbol or coin id
* [clear](#clear)
  * clear loaded coin
* [chart](#chart)
  * plot the loaded crypto chart
* [ta](technical_analysis/README.md)
  * open technical analysis menu
* [basic](#basic)
  * show coin basic information
* [ps](#ps)
  * show coin price, supply, market cap related metrics.
* [mkt](#mkt)
  * show all markets for loaded coin
* [ex](#ex)
  * show all exchanges where loaded coin is listed
* [twitter](#twitter)
  * show up to 50 last tweets for loaded coin
* [events](#events )
  * show events related to loaded coin


[OVERVIEW](#OVERVIEW)
* [global](#global)
  * show global crypto market info
* [coins](#coins)
   * show coins available on CoinGecko
* [info](#info)
  * show basic info about all coins available on CoinPaprika
* [markets](#markets)
  * show market related info about all coins available on CoinPaprika
* [search](#search)
  * search for coins, exchanges, people on CoinPaprika
* [exchanges](#exchanges)
  * list all exchanges available on CoinPaprika
* [ex_markets](#ex_markets)
  * show all available markets on given exchange
* [platforms](#platforms)
  * list blockchain platforms/ecosystems eg. ethereum, solana, kusama, terra
* [contracts](#contracts)
  * show all smart contracts for given platform




# COIN <a name="COIN"></a>
## load  <a name="load"></a>

````
usage: load [-c --coin]
````

Load a given coin. The current crypto data is [Powered by Coinpaprika API](#https://coinpaprika.com/en/api/), which is an awesome service that currently requires no API Key!
By loading a coin you will have access to a lot of statistics on that coin like price data, available markets, exchanges where coin is listed and also open access to technical analysis menu


* -c/--coin: The coin you wish to load.  This can either be the symbol or the name.  `load -c BTC` and `load -c btc-bitcoin`
  will load.  The -c flag is optional,  the above is equivalent to `load btc`. If you not sure about coin symbol or coin id. You can use either `search`, `find` or `coins` commands and look for id of coin that you are interested in.


## chart <a name="chart"></a>

````
usage: chart [-d --days] [--vs]
````

Display chart for loaded coin. You can specify currency vs which you want to show chart and also number of days to get data for.
Maximum range for chart is 1 year (365 days). If you use bigger range it will be automatically converted to 365 limit.
By default currency: usd and days: 30. E.g. if you loaded in previous step Bitcoin and you want to see it's price vs USD in last 90 days range use `chart --vs USD --days 90`


* -d/--days: The number of days to look. Maximum 365 days. Default: 30
* --vs: The currency to look against. Available options are: `USD, BTC`. Default: `USD`


## ta <a name="ta"></a>

````
usage: ta [-d --days] [--vs]
````

Open Technical Analysis menu for loaded coin
Loads data for technical analysis. You can specify currency vs which you want to show chart and also number of days to get data for.
E.g. if you loaded in previous step Bitcoin and you want to see it's price vs USDin last 90 days range use `ta --vs USD --days 90`


* -d/--days: The number of days to look. Maximum 365 days. Default: 30
* --vs: The currency to look against. Available options are: `USD, BTC`. Default: `USD`

## basic <a name="basic"></a>

````
usage: basic
````

Shows basic information about loaded coin like: name, symbol, rank, type, description, platform, proof_type, contract, tags, parent


## ps <a name="ps"></a>

````
usage: ps [--vs]
````

Price, supply related data for loaded coin. There you find metrics like:
name, symbol, rank, supply, volume, ath, market cap, price change related metrics


* --vs: The currency to look against. Available options are: `BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK`. Default: USD

## mkt <a name="mkt"></a>

````
usage: mkt [--vs] [-t --top] [-s --sort] [--descend] [-l --links]
````

Get all markets found for given coin.

* --vs: The currency to look against. Available options are: `BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK`. Default: USD
* -t/--top - number of markets to display. To display top 10 markets: `mkt --top 10 --sort trust_score`
* -s/--sort - sort by given column. You can chose on from `pct_volume_share, exchange, pair, trust_score, volume,price`.
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `mkt --links`

## ex <a name="ex"></a>

````
usage: ex [-t --top] [-s --sort] [--descend]
````

Get all exchanges found for given coin.

* -t/--top: Number of exchanges to display. To display top 10 exchanges: `ex --top 10 --sort fiats`
* -s/--sort: Sort by given column. You can chose on from `id, name, adjusted_volume_24h_share, fiats`.
* --descend: Flag to sort in descending order (lowest first)

## twitter <a name="twitter"></a>

````
usage: twitter [-t --top] [-s --sort] [--descend]
````

Show last tweets for given coin.

* -t/--top: Number of tweets to display. To display top 10 tweets: `twitter --top 10 --sort date`
* -s/--sort: Sort by given column. You can chose on from `date, user_name, status, retweet_count, like_count`.
* --descend: Flag to sort in descending order (lowest first)

## events <a name="events"></a>

````
usage: events [-t --top] [-s --sort] [--descend] [-l --links]
````

Show information about most important coins events.

* -t/--top:  Number of events to display. To display top 10 events: `events --top 10 --sort date`
* -s/--sort:  Sort by given column. You can chose on from `date, date_to, name, description, is_conference`.
* --descend:  Flag to sort in descending order (lowest first)
* -l/--links:  Flag to show urls. Using this flag will add additional column with urls e.g. `events --links`. If you will use this flag url column will be displayed.

## clear <a name="clear"></a>

````
usage: clear
````

Just remove previously loaded coin. (set coin = None)


## find <a name="find"></a>

````
usage: find [-c --coin] [-t --top] [-k --key]
````

Find similar coin by coin name,symbol or id. If you don't remember exact name or id of the Coin at Coinpaprika, you can use this command to display coins with similar name, symbol or id to your search query.
Example of usage: coin name is something like `polka`. So you can try: `find -c polka -k name -t 25`
It will search for coin that has similar name to polka and display top 25 matches.

* -c, --coin: Stands for coin - you provide here your search query
* -k, --key: It's a searching key. You can search by symbol, id or name of coin
* -t, --top: It displays top N number of records.

![image](https://user-images.githubusercontent.com/275820/125335645-150b9680-e34d-11eb-8ab4-6d1de1d9ab84.png)


# OVERVIEW <a name="OVERVIEW"></a>

## global <a name="global"></a>

````
usage: global
````

Show most important global crypto statistics like: market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date, market_cap_change_24h, volume_24h_change_24h, last_updated

## coins <a name="coins"></a>

````
usage: coins [-s --skip] [-t --top] [-l --letter] [-k --key]
````

Display all available coins in coinpaprika. You can search with pagination mechanism with `coins --skip [num] --top [num]` or you can just search by letter like
`coins --letter d --key name --top 10` it will display top 10 matches for coins which name starts with letter `d` and search will be done in column `name`

* -s/--skip: Number of records to skip.  Default is 0. There are thousands of coins, so there is mechanism to paginate through them.
e.q if you want to see only records from 500-750 you should use `coins --skip 500 --top 250` or if you want to see 1200-1880 you should use `coins --skip 1200 --top 680`.
* -t/--top: Number of news to display. One page of news contains 25 news, so to get 250 news script needs to scrape 10 pages (it can take some time). Default 100. E.g `news --top 150`
* -l/--letter: First letters of coin by which you want to search
* -k/--key: Search key. With this parameter you can specify in which column you would like to search. Choose on from `name, id, symbol`

## info <a name="info"></a>

````
usage: info [-t --top] [-s --sort] [--descend]
````
Show basic coin information for all coins from CoinPaprika

* --vs: The currency to look against. Available options are: `BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK`. Default: USD
* -t/--top: Number of coins to display. To display top 10 coins: `info --top 10 --sort rank`
* -s/--sort: Sort by given column. You can chose on from `rank, name, symbol, price, volume_24h, circulating_supply, total_supply, max_supply, ath_price,market_cap, beta_value`.
* --descend: Flag to sort in descending order (lowest first)

## markets <a name="markets"></a>

````
usage: markets [--vs] [-t --top] [-s --sort] [--descend]
````

Show market related (price, supply, volume) coin information for all coins on CoinPaprika

* --vs: The currency to look against. Available options are: `BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK`. Default: USD
* -t/--top: Number of coins to display. To display top 10 coins: `markets --top 10 --sort rank`
* -s/--sort: Sort by given column. You can chose on from `rank, name, symbol, price, volume_24h, mcap_change_24h, pct_change_1h, pct_change_24h, ath_price, pct_from_ath`.
* --descend: Flag to sort in descending order (lowest first)

## exchanges <a name="exchanges"></a>

````
usage: exchanges [--vs] [-t --top] [-s --sort] [--descend]
````

Show all exchanges from CoinPaprika

* --vs: The currency to look against. Available options are: `BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK`. Default: USD
* -t/--top: Number of coins to display. To display top 10 coins: `exchanges --top 10 --sort rank`
* -s/--sort: Sort by given column. You can chose on from `rank, name, currencies, markets, fiats, confidence, volume_24h, volume_7d, volume_30d, sessions_per_month`.
* --descend: Flag to sort in descending order (lowest first)

## ex_markets <a name="ex_markets"></a>

````
usage: ex_markets [-e --exchange] [-t --top] [-s --sort] [--descend] [-l --links]
````

Get all exchange markets found for given exchange

* -e/--exchange: Identifier of exchange e.g for Binance Exchange: `binance`
* -t/--top: Number of markets to display. To display top 10 markets: `ex_markets --top 10 --sort reported_volume_24h_share`
* -s/--sort: Sort by given column. You can chose on from `pair , base_currency_name, quote_currency_name, category, reported_volume_24h_share, trust_score, market_url`.
* --descend: Flag to sort in descending order (lowest first)
* -l/--links: Flag to show urls. Using this flag will add additional column with urls e.g. `ex_markets --links`. If you will use this flag url column will be displayed.

## platforms <a name="platforms"></a>

````
usage: platforms
````

List all smart contract platforms like ethereum, solana, cosmos, eos


## contracts <a name="contracts"></a>

````
usage: contracts [-p --platform] [-t --top] [-s --sort] [--descend]
````

Gets all contract addresses for given blockchain platform

* -p/--platform: smart contract platform id. Available coins:
```
btc-bitcoin, eos-eos, eth-ethereum, xrp-xrp, bch-bitcoin-cash, xem-nem, neo-neo, xlm-stellar, etc-ethereum-classic,
qtum-qtum, zec-zcash, bts-bitshares, waves-waves, nxt-nxt, act-achain, ubq-ubiq, xcp-counterparty, etp-metaverse-etp,
burst-burst, omni-omni, trx-tron, bnb-binance-coin, ardr-ardor, ht-huobi-token, blvr-believer, cake-pa
ncakeswap, fsxu-flashx-ultra, chik-chickenkebab-finance, jgn-juggernaut7492, crx-cryptex, whirl-whirl-finance,
 eubi-eubi-token, swam-swapmatic-token, shells-shells
```
* -t/--top: Number of smart contracts to display. To display 10 smart contracts: `contracts -p eth-ethereum --top 10 --sort index`
* -s/--sort: Sort by given column. You can chose on from `index, id, type, active, address`.
* --descend: Flag to sort in descending order (lowest first)

## search <a name="search"></a>

````
usage: search [-q --query] [-c --cat] [-s --sort] [-t --top] [--descend]
````

Search over CoinPaprika API

* -q/--query: Phrase for search
* -c/--cat: Categories to search: currencies|exchanges|icos|people|tags|all. Default: all
* -t/--top: Number of found records to display.
* -s/--sort: Sort by given column. You can chose on from `category, id, name`.
* --descend: Flag to sort in descending order (lowest first)

![image](https://user-images.githubusercontent.com/275820/125336200-c7435e00-e34d-11eb-965f-16856f4d9913.png)

