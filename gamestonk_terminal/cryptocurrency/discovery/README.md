# DISCOVERY CRYPTO

This menu aims to discover crypto currencies. You can find the most trending coins, top nfts, best defi tokens and many
others. The usage of the following commands along with an example will be exploited below.

[CoinGecko](#CoinGecko)

* [cg_coins](#cg_coins)
  * show coins available on CoinGecko
* [cg_trending](#cg_trending)
  * show trending coins on CoinGecko
* [cg_most_voted](#cg_most_voted)
  * show most voted coins on CoinGecko
* [cg_top_volume](#cg_top_volume)
  * show coins with highest volume on CoinGecko
* [cg_recently](#cg_recently)
  * show recently added on CoinGecko
* [cg_sentiment](#cg_sentiment)
  * show coins with most positive sentiment
* [cg_gainers](#cg_gainers)
  * show top gainers - coins which price gained the most in given period
* [cg_losers](#cg_losers)
  * show top losers - coins which price dropped the most in given period
* [cg_yfarms](#cg_yfarms)
  * show top Yield Farms
* [cg_top_defi](#cg_top_defi)
  * show top DeFi Protocols
* [cg_top_dex](#cg_top_dex)
  * show top Decentralized Exchanges
* [cg_top_nft](#cg_top_nft)
  * show top Non Fungible Tokens

[CoinPaprika](#CoinPaprika)

* [cp_coins](#cp_coins)
  * show coins available on CoinPaprika
* [cp_search](#cp_search)
  * show search on CoinPaprika

[CoinMarketCap](#CoinMarketCap)

* [cmc_top](#cmc_top)
  * show top coin from coinmarketcap.com

[Binance](#Binance)

* [bin_coins](#bin_coins)
  * show coins available on Binance

# CoinGecko <a name="CoinGecko"></a>

## cg_coins <a name="cg_coins"></a>

```text
usage: cg_coins [-s --skip] [-t --top] [-l --letter] [-k --key]
```

Display all available coins in coingecko. You can search with pagination mechanism with `cg_coins --skip [num] --top [num]`
or you can just search by letter like `cg_coins --letter d --key name --top 10` it will display top 10 matches for coins
which name starts with letter `d` and search will be done in column `name`

* -s/--skip - number of records to skip.  Default is 0. There are thousands of coins, so there is mechanism to paginate
  through them. e.q if you want to see only records from 500-750 you should use `cg_coins --skip 500 --top 250` or if
  you want to see 1200-1880 you should use `coins --skip 1200 --top 680`.
* -t/--top - number of news to display. One page of news contains 25 news, so to get 250 news script needs to scrape 10
  pages (it can take some time). Default 100. E.g `news --top 150`
* -l/--letter - first letters of coin by which you want to search
* -k/--key - search key. With this parameter you can specify in which column you would like to search. Choose on from
  `name, id, symbol`

![image](https://user-images.githubusercontent.com/275820/123538885-26428980-d737-11eb-9418-e3f80511786d.png)

## cg_trending <a name="cg_trending"></a>

```text
usage: cg_trending [-t --top] [-s --sortby] [--descend] [-l --links]
```

Shows most trending coins on CoinGecko.

* -t/--top - number of coins to display. To display top 10 coins: `cg_trending --top 10`
* -s/--sortby - sort by given column. You can chose on from `rank, name, price_usd, price_btc`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `cg_trending --top 10 --links`

![image](https://user-images.githubusercontent.com/275820/124305015-c8fa6e00-db64-11eb-81de-4e8b943c6c0d.png)

## cg_most_voted <a name="cg_most_voted"></a>

```text
usage: cg_most_voted [-t --top] [-s --sortby] [--descend] [-l --links]
```

Shows most voted coins on CoinGecko.

* -t/--top - number of coins to display. To display top 10 coins: `cg_most_voted --top 10`
* -s/--sortby - sort by given column. You can chose on from `rank, name, price_usd, price_btc`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `cg_most_voted --top 10 --links`

![image](https://user-images.githubusercontent.com/275820/123538516-8cc6a800-d735-11eb-85ee-e3f2141a54fb.png)

## cg_most_visited <a name="cg_most_visited"></a>

```text
usage: cg_most_visited [-t --top] [-s --sortby] [--descend] [-l --links]
```

Shows most visited coins on CoinGecko.

* -t/--top - number of coins to display. To display top 10 coins: `cg_most_visited --top 10`
* -s/--sortby - sort by given column. You can chose on from `rank, name, price_usd, price_btc`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `cg_most_visited --top 10 --links`

![image](https://user-images.githubusercontent.com/275820/123538524-9cde8780-d735-11eb-9827-c02ea8bd5db7.png)

## cg_sentiment <a name="cg_sentiment"></a>

```text
usage: cg_sentiment [-t --top] [-s --sortby] [--descend] [-l --links]
```

Shows coins with the most positive sentiment on CoinGecko

* -t/--top - number of coins to display. To display top 10 coins: `cg_sentiment --top 10`
* -s/--sortby - sort by given column. You can chose on from `rank, name, price_usd, price_btc`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `cg_sentiment --top 10 --links`

![image](https://user-images.githubusercontent.com/275820/123538553-c5ff1800-d735-11eb-9fef-ef490184c6d8.png)

## cg_recently <a name="cg_recently"></a>

```text
usage: cg_recently [-t --top] [-s --sortby] [--descend] [-l --links]
```

Shows coins which were recently added on CoinGecko

* -t/--top - number of coins to display. To display top 10 coins: `cg_recently --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can chose on from `rank, name, symbol, price, change_24h, change_1h, added`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `cg_recently --top 10 --links`

![image](https://user-images.githubusercontent.com/275820/124305122-f47d5880-db64-11eb-9048-b495248723d3.png)

## cg_top_volume <a name="cg_top_volume"></a>

```text
usage: cg_top_volume [-t --top] [-s --sortby] [--descend]
```

Shows coins with the highest transactions volume on CoinGecko

* -t/--top - number of coins to display. To display top 10 coins: `cg_top_volume --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can chose on from
  `rank, name, symbol, price, change_1h, change_24h, change_7d , volume_24h`
* --descend - flag to sort in descending order (lowest first)

![image](https://user-images.githubusercontent.com/275820/124305188-0a8b1900-db65-11eb-953f-febc32500ff9.png)

## cg_gainers <a name="cg_gainers"></a>

```text
usage: cg_gainers [-p --period] [-t --top] [-s --sortby] [--descend] [-l --links]
```

Shows largest gainers - coins which gain the most in given period.

* -p/--period - time period in which coins gained the most in price. One from `1h, 24h, 7d, 14d, 30d, 60d, 1y`.
  If you want to see top gainers in last 24h `cg_gainers -p 24h` or top gainers in last 60days `cg_gainers -p 60d`
* -t/--top - number of coins to display. To display top 10 coins: `cg_gainers --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can chose on from `rank, name, symbol, price, change, volume`.
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `cg_gainers --period 24h --links`

![image](https://user-images.githubusercontent.com/275820/124305218-137bea80-db65-11eb-914c-865b56cf33ea.png)

## cg_losers <a name="cg_losers"></a>

```text
usage: cg_losers [-p --period] [-t --top] [-s --sortby] [--descend] [-l --links]
```

Shows largest losers - coins which lost the most in given period.

* -p/--period - time period in which coins lost the most in price. One from `1h, 24h, 7d, 14d, 30d, 60d, 1y`.
  If you want to see top losers in last 24h `cg_losers -p 24h` or top losers in last 60days `cg_losers -p 60d`
* -t/--top - number of coins to display. To display top 10 coins: `cg_losers --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can chose on from `rank, name, symbol, price, change, volume`.
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `cg_losers --period 24h --links`

![image](https://user-images.githubusercontent.com/275820/124305327-3ad2b780-db65-11eb-9922-7783b740312c.png))

## cg_yfarms <a name="cg_yfarms"></a>

```text
usage: cg_yfarms [-t --top] [-s --sortby] [--descend]
```

Shows Top Yield Farming Pools by Value Locked from <https://www.coingecko.com/en/yield-farming>
Yield farming, also referred to as liquidity mining, is a way to generate rewards with cryptocurrency holdings.
In simple terms, it means locking up cryptocurrencies and getting rewards.

* -t/--top - number of yield farms to display. To display top 10 yield farms: `cg_yfarms --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can sort data by `rank, name, value_locked, return_year`
* --descend - flag to sort in descending order (lowest first)

![image](https://user-images.githubusercontent.com/275820/124305461-6ce41980-db65-11eb-9c82-648f4ff905e8.png)

## cg_top_defi <a name="cg_top_defi"></a>

```text
usage: cg_top_defi [-t --top] [-s --sortby] [--descend] [-l --links]
```

Shows Top DeFi Coins by Market Capitalization from <https://www.coingecko.com/en/defi>
DeFi or Decentralized Finance refers to financial services that are built on top of distributed networks with no central
intermediaries.

* -t/--top - number of defi coins to display. To display top 10 defi coins: `cg_top_defi --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can sort data by `rank, name, symbol, price, change_24h, change_1h, change_7d`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `cg_top_defi --links`.

![image](https://user-images.githubusercontent.com/275820/124305508-7c636280-db65-11eb-8ae7-38389ac72770.png)

## cg_top_dex <a name="cg_top_dex"></a>

```text
usage: cg_top_dex [-t --top] [-s --sortby] [--descend]
```

Shows Top Decentralized Exchanges on CoinGecko by Trading Volume from <https://www.coingecko.com/en/dex>
Decentralized exchanges or DEXs are autonomous decentralized applications (DApps) that allow cryptocurrency buyers or
sellers to trade without having to give up control over their funds to any intermediary or custodian. Source:
[coinmarketcap](#https://coinmarketcap.com/alexandria/article/what-are-decentralized-exchanges-dex)

* -t/--top - number of Decentralized Exchanges to display. To display top 10 DEX: `cg_top_dex --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can sort data by
  `rank, name, volume_24h, n_coins, n_pairs, visits, most_traded, market_share_by_vol most_traded_pairs, market_share_by_volume`
* --descend - flag to sort in descending order (lowest first)

![image](https://user-images.githubusercontent.com/275820/124305536-84230700-db65-11eb-82bf-ad2d0878135c.png)

## cg_top_nft <a name="cg_top_nft"></a>

```text
usage: cg_top_nft [-t --top] [-s --sortby] [--descend] [-l --links]
```

Shows Top NFT Coins by Market Capitalization from <https://www.coingecko.com/en/nft>
NFT (Non-fungible Token) refers to digital assets with unique characteristics.
Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

* -t/--top - number of NFT to display. To display top 10 NFT Coins: `cg_top_nft --top 10 --sortby rank`
* -s/--sortby - sort by given column. You can sort data by
  `rank, name, symbol, price, change_24h, change_1h, change_7d, volume_24h, market_cap`
* --descend - flag to sort in descending order (lowest first)
* -l/--links - flag to show urls. Using this flag will add additional column with urls e.g. `cg_top_nft --links`.

![image](https://user-images.githubusercontent.com/275820/124305553-8be2ab80-db65-11eb-92a8-86485d2b7ef8.png)

# CoinPaprika <a name="CoinPaprika"></a>

## cp_coins <a name="cp_coins"></a>

```text
usage: cp_coins [-s --skip] [-t --top] [-l --letter] [-k --key]
```

Display all available coins in coinpaprika. You can search with pagination mechanism with `cp_coins --skip [num] --top [num]`
or you can just search by letter like `cp_coins --letter d --key name --top 10` it will display top 10 matches for coins
which name starts with letter `d` and search will be done in column `name`

* -s/--skip: Number of records to skip.  Default is 0. There are thousands of coins, so there is mechanism to paginate
  through them. e.q if you want to see only records from 500-750 you should use `cp_coins --skip 500 --top 250` or if
  you want to see 1200-1880 you should use `cp_coins --skip 1200 --top 680`.
* -t/--top: Number of coins to display. E.g `cp_coins --top 150`
* -l/--letter: First letters of coin by which you want to search
* -k/--key: Search key. With this parameter you can specify in which column you would like to search. Choose on from
  `name, id, symbol`

## cp_search <a name="cp_search"></a>

```text
usage: cp_search [-q --query] [-c --cat] [-s --sort] [-t --top] [--descend]
```

Search over CoinPaprika API

* -q/--query: Phrase for search
* -c/--cat: Categories to search: currencies|exchanges|icos|people|tags|all. Default: all
* -t/--top: Number of found records to display.
* -s/--sort: Sort by given column. You can chose on from `category, id, name`.
* --descend: Flag to sort in descending order (lowest first)

![image](https://user-images.githubusercontent.com/275820/125336200-c7435e00-e34d-11eb-965f-16856f4d9913.png)

# CoinMarketCap <a name="CoinMarketCap"></a>

## cmc_top <a name="cmc_top"></a>

```text
cmc_top [-n] [-s --sort SORTBY] [--descend]
```

This command displays the top n cryptocurrencies from coinmarketcap.com.

* -n: Number of coins to look at (after sort).  Defaults to 10.
* -s/--sort : Column to sort by. One of {Symbol,CMC_Rank,LastPrice,DayPctChange,MarketCap}. Defaults to sorting by the
  CMC rank.
* --descend : Flag to change the sorting order.  Sorts in ascending order (since default order is the Rank which starts
  at 1).

<img width="990" alt="crypto" src="https://user-images.githubusercontent.com/25267873/115787544-4746d100-a3ba-11eb-9433-b7cb9142404a.png">

# Binance <a name="Binance"></a>

## bin_coins <a name="bin_coins"></a>

```text
usage: bin_coins [-s --skip] [-t --top] [-l --letter] [-k --key]
```

Display all available coins on Binance. In Binance terminology symbol means a pair of 2 coins e.g symbol is ETHBTC - it
means that baseAsset is ETH and quoteAsset is BTC. You can search with pagination mechanism with
`bin_coins --skip [num] --top [num]` or you can just search by letter like `bin_coins --letter d --key symbol --top 10`
it will display top 10 matches for coins which symbol starts with letter `d` and search will be done in column `symbol`

* -s/--skip: Number of records to skip.  Default is 0. There are thousands of coins, so there is mechanism to paginate
  through them. e.q if you want to see only records from 500-750 you should use `bin_coins --skip 500 --top 250`
* -t/--top: Number of coins to display.
* -l/--letter: First letters of coin by which you want to search
* -k/--key: Search key. With this parameter you can specify in which column you would like to search. Choose on from
  `symbol, quoteAsset, baseAsset`
