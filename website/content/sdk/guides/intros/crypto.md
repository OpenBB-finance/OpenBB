---
title: Crypto
sidebar_location:
---

The Crypto module wraps the functions of the OpenBB Terminal menu. This allows web applications and dashboards to be built quickly, on top of the existing infrastructure. Navigating the functions is similar to operating the OpenBB Terminal.

## How to Use

The list below are all the SDK functions at the `openbb.crypto` level:

| Path                  |    Type    |           Description |
| :-------------------- | :--------: | --------------------: |
| openbb.crypto.candle  |  Function  |          OHLC+V chart |
| openbb.crypto.dd      | Sub-Module |         Due Diligence |
| openbb.crypto.defi    | Sub-Module |                  DeFi |
| openbb.crypto.disc    | Sub-Module |             Discovery |
| openbb.crypto.find    |  Function  |   Find Digital Assets |
| openbb.crypto.load    |  Function  |  Load Historical Data |
| openbb.crypto.nft     | Sub-Module |                  NFTs |
| openbb.crypto.onchain | Sub-Module |       Onchain Metrics |
| openbb.crypto.ov      | Sub-Module |       Market Overview |
| openbb.crypto.price   |  Function  | Live Prices from Pyth |
| openbb.crypto.tools   | Sub-Module |           Calculators |

Alternatively, the contents of a menu is printed by running, `help(openbb.crypto)`. The objective of this guide is to introduce the high-level functions and provide a sample of examples from the sub-modules. Refer to the guides for each sub-module to learn more about them specifically.

## Examples

### Import Statements

The examples in this guide will assume that the code block below is at the beginning of the Python script or Jupyter Notebook file.

```python
import pandas as pd
from openbb_terminal.sdk import openbb
%matplotlib inline
```

### Load

The `load` function is capable of loading from a variety of sources, one of which is CCXT. When `CCXT` is `source`, an additional argument, `exchange`, is required.

```python
help(openbb.crypto.load)

Help on Operation in module openbb_terminal.core.library.operation:

<openbb_terminal.core.library.operation.Operation object>
    Load crypto currency to get data for

    Parameters
    ----------
    symbol: str
        Coin to get
    start_date: str or datetime, optional
        Start date to get data from with. - datetime or string format (YYYY-MM-DD)
    interval: str
        The interval between data points in minutes.
        Choose from: 1, 15, 30, 60, 240, 1440, 10080, 43200
    exchange: str:
        The exchange to get data from.
    vs_currency: str
        Quote Currency (Defaults to usdt)
    end_date: str or datetime, optional
        End date to get data from with. - datetime or string format (YYYY-MM-DD)
    source: str
        The source of the data
        Choose from: CCXT, CoinGecko, YahooFinance

    Returns
    -------
    pd.DataFrame
        Dataframe consisting of price and volume data
```

<details>
  <summary><code>CCXT Exchange List</code> <code>(expand to see list of exchanges supported by CCXT)</code></summary>

|     |           Exchange |
| --- | -----------------: |
|     |                aax |
|     |           ascendex |
|     |            bequant |
|     |              bibox |
|     |             bigone |
|     |            binance |
|     |       binancecoinm |
|     |          binanceus |
|     |        binanceusdm |
|     |              bit2c |
|     |            bitbank |
|     |             bitbay |
|     |         bitcoincom |
|     |           bitfinex |
|     |          bitfinex2 |
|     |           bitflyer |
|     |           bitforex |
|     |             bitget |
|     |            bithumb |
|     |            bitmart |
|     |             bitmex |
|     |            bitopro |
|     |           bitpanda |
|     |             bitrue |
|     |              bitso |
|     |           bitstamp |
|     |          bitstamp1 |
|     |            bittrex |
|     |            bitvavo |
|     |               bkex |
|     |               bl3p |
|     |           btcalpha |
|     |             btcbox |
|     |              btcex |
|     |         btcmarkets |
|     |         btctradeua |
|     |            btcturk |
|     |               buda |
|     |                 bw |
|     |              bybit |
|     |          bytetrade |
|     |                cex |
|     |      coinbaseprime |
|     |        coinbasepro |
|     |          coincheck |
|     |             coinex |
|     |         coinfalcon |
|     |           coinmate |
|     |            coinone |
|     |           coinspot |
|     |             crex24 |
|     |          cryptocom |
|     |        currencycom |
|     |              delta |
|     |            deribit |
|     |          digifinex |
|     |             eqonex |
|     |               exmo |
|     |            flowbtc |
|     |             fmfwio |
|     |                ftx |
|     |              ftxus |
|     |               gate |
|     |             gateio |
|     |             gemini |
|     |             hitbtc |
|     |            bitbtc3 |
|     |            hollaex |
|     |              huobi |
|     |            huobijp |
|     |               idex |
|     | independentreserve |
|     |            indodax |
|     |              itbit |
|     |             kraken |
|     |             kucoin |
|     |      kucoinfutures |
|     |               kuna |
|     |            latoken |
|     |              lbank |
|     |             lbank2 |
|     |             liquid |
|     |               luno |
|     |              lykke |
|     |            mercado |
|     |               mexc |
|     |              mexc3 |
|     |               ndax |
|     |            novadax |
|     |            oceanex |
|     |             okcoin |
|     |               okex |
|     |              okex5 |
|     |                okx |
|     |            paymium |
|     |             phemex |
|     |           poloniex |
|     |             probit |
|     |             qtrade |
|     |              ripio |
|     |               stex |
|     |            therock |
|     |            tidebit |
|     |              tidex |
|     |              timex |
|     |         tokocrypto |
|     |              upbit |
|     |      wavesexchange |
|     |           whitebit |
|     |                woo |
|     |              yobit |
|     |               zaif |
|     |                 zb |
|     |             zipmex |
|     |              zonda |

</details>

```python
eth_df = openbb.crypto.load('ETH', source = 'CCXT', exchange = 'binance')

eth_df.tail(5)
```

| date                |    Open |    High |     Low |   Close | Volume |
| :------------------ | ------: | ------: | ------: | ------: | -----: |
| 2022-11-14 00:00:00 |  1221.5 |  1291.2 | 1171.13 | 1243.28 | 934742 |
| 2022-11-15 00:00:00 | 1243.29 |    1291 | 1234.01 | 1253.23 | 632826 |
| 2022-11-16 00:00:00 | 1253.22 | 1268.67 | 1187.06 | 1216.17 | 673340 |
| 2022-11-17 00:00:00 | 1216.16 | 1228.22 | 1181.05 | 1200.43 | 530537 |
| 2022-11-18 00:00:00 | 1200.42 |    1234 | 1199.18 | 1206.11 | 306400 |

Adding the `interval` argument allows for intraday data or weekly/monthly periods to be loaded.

```python
eth_df = openbb.crypto.load('ETH', source = 'CCXT', exchange = 'binance', interval = '30')

eth_df.tail(3)
```

| date                |    Open |    High |     Low |   Close |  Volume |
| :------------------ | ------: | ------: | ------: | ------: | ------: |
| 2022-11-18 17:00:00 | 1207.44 | 1208.35 | 1200.36 | 1205.35 | 11359.4 |
| 2022-11-18 17:30:00 | 1205.36 | 1207.12 |  1202.5 | 1204.17 | 5878.59 |
| 2022-11-18 18:00:00 | 1204.17 | 1207.28 | 1203.26 | 1206.37 | 1540.67 |

Loading monthly OHLC+V data looks like this:

```python
eth_df = openbb.crypto.load('ETH', source = 'CCXT', exchange = 'binance', interval = '43200')

eth_df.tail(3)
```

| date                |    Open |    High |     Low |   Close |      Volume |
| :------------------ | ------: | ------: | ------: | ------: | ----------: |
| 2022-09-01 00:00:00 | 1554.11 |    1789 |    1220 | 1328.72 | 2.25453e+07 |
| 2022-10-01 00:00:00 | 1328.71 | 1663.06 |    1190 | 1572.69 | 1.67681e+07 |
| 2022-11-01 00:00:00 | 1572.69 |    1680 | 1073.53 | 1204.78 |  1.6707e+07 |

### Candles

A loaded DataFrame is used as the input for the `candles` function:

```python
openbb.crypto.candle(eth_df)
```

![openbb.crypto.candle](https://user-images.githubusercontent.com/85772166/202791587-d69c7568-69ff-46b3-b41f-146ed8796f7e.png "openbb.crypto.candle")

Notice that the chart has no title. It can be added using the `title` argument.

```python
openbb.crypto.candles(eth_df, title = 'ETH/USDT (Monthly)')
```

![openbb.crypto.candle](https://user-images.githubusercontent.com/85772166/202791726-b4a775d9-5a00-4d92-8fbc-bd26aeff62d2.png "openbb.crypto.candle")

### Find

Find similar coins by name, symbol, or ID.

```python
results = openbb.crypto.find(
    query = 'Genesis',
    source = 'CoinPaprika',
    key = 'name',
)

results.head(5)
```

|     | name          | rank | id                 | symbol | type  |
| --: | :------------ | ---: | :----------------- | :----- | :---- |
|   0 | Gnosis        |  124 | gno-gnosis         | GNO    | token |
|   1 | Gene          | 4696 | gene-gene          | GENE   | token |
|   2 | Nemesis       | 4246 | nms-nemesis        | NMS    | token |
|   3 | Genesis Token | 7763 | gent-genesis-token | GENT   | token |
|   4 | Alpha Genesis | 4732 | agen-alpha-genesis | AGEN   | token |

### Active Addresses

Get the historical number of active wallet addresses for a token with: `openbb.crypto.dd.active`.

```python
active_eth = openbb.crypto.dd.active(symbol = 'ETH', interval = '24h', start_date = '2017-09-01')
active_eth = active_eth.reset_index()
active_eth.rename(columns = {'v': 'Active Addresses', 't': 'Date'}, inplace = True)
active_eth.set_index(keys = ['Date'], inplace = True)

active_eth.tail(5)
```

| Date                | Active Addresses |
| :------------------ | ---------------: |
| 2022-11-13 00:00:00 |           426441 |
| 2022-11-14 00:00:00 |           474868 |
| 2022-11-15 00:00:00 |           469880 |
| 2022-11-16 00:00:00 |           448492 |
| 2022-11-17 00:00:00 |           463467 |

### Trades

Get trade-level data from a specific exchange with: `openbb.crypto.dd.trades`

```python
trades_ethusdt = openbb.crypto.dd.trades(exchange_id = 'binance', symbol = 'ETH', to_symbol = 'USDT')

trades_ethusdt.tail(5)
```

|     | Date                             |   Price | Amount |    Cost | Side |
| --: | :------------------------------- | ------: | -----: | ------: | :--- |
| 495 | 2022-11-18 19:16:15.959000+00:00 | 1204.02 | 2.7033 | 3254.83 | buy  |
| 496 | 2022-11-18 19:16:15.959000+00:00 | 1204.03 | 1.1769 | 1417.02 | buy  |
| 497 | 2022-11-18 19:16:15.981000+00:00 | 1204.03 | 5.0493 | 6079.51 | buy  |
| 498 | 2022-11-18 19:16:15.981000+00:00 | 1204.07 | 2.1126 | 2543.72 | buy  |
| 499 | 2022-11-18 19:16:15.981000+00:00 | 1204.08 | 5.2811 | 6358.87 | buy  |

Use the `exchange_id` argument to return data from other venues, such as CoinBase.

```python
trades_ethusdt = openbb.crypto.dd.trades(exchange_id = 'coinbaseprime', symbol = 'ETH', to_symbol = 'USDT')

trades_ethusdt.tail(5)
```

|     | Date                             |   Price |   Amount |        Cost | Side |
| --: | :------------------------------- | ------: | -------: | ----------: | :--- |
| 995 | 2022-11-18 19:20:15.176000+00:00 | 1204.65 |  3.89878 |     4696.67 | sell |
| 996 | 2022-11-18 19:20:29.524000+00:00 | 1204.78 |  0.41545 |     500.526 | buy  |
| 997 | 2022-11-18 19:20:29.931000+00:00 | 1204.78 |  6.2e-07 | 0.000746964 | buy  |
| 998 | 2022-11-18 19:20:32.263000+00:00 | 1205.03 |  0.41536 |     500.521 | buy  |
| 999 | 2022-11-18 19:20:32.274000+00:00 | 1205.03 | 3.05e-06 |  0.00367534 | buy  |

### Coin_List

Retrieve a list of all coins available from CoinPaprika with: `openbb.crypto.ov.coin_list()`

```python
coins = openbb.crypto.ov.coin_list()

coins.head(10)
```

|     | rank | id               | name         | symbol | type  |
| --: | ---: | :--------------- | :----------- | :----- | :---- |
|   0 |    1 | btc-bitcoin      | Bitcoin      | BTC    | coin  |
|   1 |    2 | eth-ethereum     | Ethereum     | ETH    | coin  |
|   2 |    3 | usdt-tether      | Tether       | USDT   | token |
|   3 |    4 | usdc-usd-coin    | USD Coin     | USDC   | token |
|   4 |    5 | bnb-binance-coin | Binance Coin | BNB    | coin  |
|   5 |    6 | busd-binance-usd | Binance USD  | BUSD   | token |
|   6 |    7 | xrp-xrp          | XRP          | XRP    | coin  |
|   7 |    8 | doge-dogecoin    | Dogecoin     | DOGE   | coin  |
|   8 |    9 | ada-cardano      | Cardano      | ADA    | coin  |
|   9 |   10 | hex-hex          | HEX          | HEX    | token |

### BAAS (Historical Bid-Ask Average Spread)

Measure liquidity over time for an asset with: `openbb.crypto.onchain.baas`

```python
openbb.crypto.onchain.baas(symbol = 'ETH', to_symbol = 'USDT')
```

|     | Date       | Base currency | Quote currency | Daily spread | Average bid price | Average ask price |
| --: | :--------- | :------------ | :------------- | -----------: | ----------------: | ----------------: |
|   0 | 2022-11-08 | ETH           | USDT           |      26.7961 |           1480.72 |           1453.93 |
|   1 | 2022-11-09 | ETH           | USDT           |      87.9466 |           1255.58 |           1167.63 |
|   2 | 2022-11-10 | ETH           | USDT           |      24.8262 |            1248.8 |           1273.62 |
|   3 | 2022-11-11 | ETH           | USDT           |       365.65 |           877.792 |           1243.44 |
|   4 | 2022-11-13 | ETH           | USDT           |      23.2032 |           1240.23 |           1217.02 |
|   5 | 2022-11-14 | ETH           | USDT           |      22.5726 |           1221.92 |           1199.35 |

### Trending

Discover trending coins on CoinGecko with: `openbb.crypto.disc.trending()`

```python
openbb.crypto.disc.trending()
```

|     | Symbol        | Name                | market_cap Cap Rank |
| --: | :------------ | :------------------ | ------------------: |
|   0 | solana        | Solana              |                  16 |
|   1 | chiliz        | Chiliz              |                  36 |
|   2 | aptos         | Aptos               |                  64 |
|   3 | elrond-erd-2  | MultiversX (Elrond) |                  43 |
|   4 | algorand      | Algorand            |                  29 |
|   5 | matic-network | Polygon             |                  10 |
|   6 | media-network | Media Network       |                 890 |

### News

Get crypto-focussed news with: `openbb.crypto.ov.news`

```python
openbb.crypto.ov.news(post_kind = 'news',region = 'en', filter_= 'important', ascend = False)
```

|     | published_at | domain             | title                                                              | negative_votes | positive_votes | link                                                                                                                                              |
| --: | :----------- | :----------------- | :----------------------------------------------------------------- | -------------: | -------------: | :------------------------------------------------------------------------------------------------------------------------------------------------ |
|   0 | 2022-11-18   | decrypt.co         | Edward Snowden: Sanctioning of Ethereum Mixer Tornado Cash Was     |              0 |              2 | https://cryptopanic.com/news/16935211/Edward-Snowden-Sanctioning-of-Ethereum-Mixer-Tornado-Cash-Was-Deeply-Illiberal-and-Profoundly-Authoritarian |
|     |              |                    | 'Deeply Illiberal and Profoundly Authoritarian'                    |                |                |                                                                                                                                                   |
|  10 | 2022-11-18   | theblockcrypto.com | Cardano developer Emurgo to issue fiat-pegged stablecoin called    |              3 |             21 | https://cryptopanic.com/news/16933998/Cardano-developer-Emurgo-to-issue-fiat-pegged-stablecoin-called-USDA                                        |
|     |              |                    | USDA                                                               |                |                |                                                                                                                                                   |
|   1 | 2022-11-18   | beincrypto.com     | SHIB Army Remains Positive as Memecoin Social Sentiment Index      |              0 |              3 | https://cryptopanic.com/news/16935115/SHIB-Army-Remains-Positive-as-Memecoin-Social-Sentiment-Index-Remains-Positive                              |
|     |              |                    | Remains Positive                                                   |                |                |                                                                                                                                                   |
|  17 | 2022-11-18   | u.today            | Is El Salvador's President's Decision to Buy One Bitcoin per Day a |              2 |             48 | https://cryptopanic.com/news/16925762/Is-El-Salvadors-Presidents-Decision-to-Buy-One-Bitcoin-per-Day-a-Good-Idea                                  |
|     |              |                    | Good Idea?                                                         |                |                |                                                                                                                                                   |
|  15 | 2022-11-18   | dailyhodl.com      | ‘Secret’ Altcoin Goes Parabolic After Rumors of European Ban on    |              0 |              3 | https://cryptopanic.com/news/16925942/Secret-Altcoin-Goes-Parabolic-After-Rumors-of-European-Ban-on-Privacy-Coins-Swirl                           |
|     |              |                    | Privacy Coins Swirl                                                |                |                |                                                                                                                                                   |
|  74 | 2022-11-15   | cryptopotato.com   | OKX Announces $100 Million Fund to Support Distressed Projects     |              0 |              4 | https://cryptopanic.com/news/16903760/OKX-Announces-100-Million-Fund-to-Support-Distressed-Projects-Following-FTX-Crash-Report                    |
|     |              |                    | Following FTX Crash (Report)                                       |                |                |                                                                                                                                                   |
|  73 | 2022-11-15   | cointelegraph.com  | Thousands petition for congressional investigation of alleged      |              1 |             36 | https://cryptopanic.com/news/16904296/Thousands-petition-for-congressional-investigation-of-alleged-GenslerSBF-links                              |
|     |              |                    | Gensler–SBF links                                                  |                |                |                                                                                                                                                   |
|  72 | 2022-11-15   | cryptonews.com     | XRP Price Forecast as XRP Pumps 9%, Becomes Top Performer          |              0 |             13 | https://cryptopanic.com/news/16904392/XRP-Price-Forecast-as-XRP-Pumps-9-Becomes-Top-Performer                                                     |
|  71 | 2022-11-15   | theblockcrypto.com | Kraken’s Ogilvie says staking adoption set to skyrocket            |              0 |              4 | https://cryptopanic.com/news/16904805/Krakens-Ogilvie-says-staking-adoption-set-to-skyrocket                                                      |
|  79 | 2022-11-15   | zycrypto.com       | SEC vs. Ripple Case Sees New Twists And Turns As Whale Holdings In |              2 |             15 | https://cryptopanic.com/news/16903258/SEC-vs-Ripple-Case-Sees-New-Twists-And-Turns-As-Whale-Holdings-In-XRP-Skyrocket                             |
|     |              |                    | XRP Skyrocket                                                      |                |                |                                                                                                                                                   |
