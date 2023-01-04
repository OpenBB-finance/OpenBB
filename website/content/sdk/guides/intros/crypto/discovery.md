---
title: Discovery
---

The Discovery sub-module contains the tools for finding new trends in Crpyto markets and making new discoveries. The commands within the menu are listed below along with a short description. The module is accessed by entering, `openbb.crypto.disc`, and then a `.` activates code completion and type hints.

## How to Use

|Path |Description |
|:----|-----------:|
|openbb.crypto.disc.categories_keys |A List of Categories for Searching Coins |
|openbb.crypto.disc.coin_list |A List of Coins Available on CoinGecko |
|openbb.crypto.disc.coins |Search Coins on CoinGecko by Category |
|openbb.crypto.disc.coins_for_given_exchange |A Dictionary of all Trading Pairs on Binance |
|openbb.crypto.disc.cpsearch |Search CoinPaprika |
|openbb.crypto.disc.gainers |Top Gainers Over Different Periods |
|openbb.crypto.disc.losers |Top Losers Over Different Periods |
|openbb.crypto.disc.top_coins |The Top Movers |
|openbb.crypto.disc.top_dapps |The Top DeFi Applications by Daily Volume and Users |
|openbb.crypto.disc.top_dexes |The Top DeFi Exchanges |
|openbb.crypto.disc.top_games |The Top DeFi Games |
|openbb.crypto.disc.top_nfts |The Top NFTs |
|openbb.crypto.disc.trending |Trending Coins on CoinGecko |

## Examples

The examples below will assume the import statement block is included at the top of the file.

```python
from openbb_terminal.sdk import openbb
```

### Coins

Search coins on CoinGecko, or compare them all.

```python
openbb.crypto.disc.coins().head(5)
```

|     | id            | symbol   | name          | image                                                                                 |   current_price |   market_cap |   market_cap_rank |   fully_diluted_valuation |   total_volume |     high_24h |      low_24h |   price_change_24h |   price_change_percentage_24h |   market_cap_change_24h |   market_cap_change_percentage_24h |   circulating_supply |   total_supply |   max_supply |          ath |   ath_change_percentage | ath_date                 |         atl |   atl_change_percentage | atl_date                 | roi                                                                               | last_updated             |   price_change_percentage_14d_in_currency |   price_change_percentage_1h_in_currency |   price_change_percentage_1y_in_currency |   price_change_percentage_200d_in_currency |   price_change_percentage_24h_in_currency |   price_change_percentage_30d_in_currency |   price_change_percentage_7d_in_currency |
|----:|:--------------|:---------|:--------------|:--------------------------------------------------------------------------------------|----------------:|-------------:|------------------:|--------------------------:|---------------:|-------------:|-------------:|-------------------:|------------------------------:|------------------------:|-----------------------------------:|---------------------:|---------------:|-------------:|-------------:|------------------------:|:-------------------------|------------:|------------------------:|:-------------------------|:----------------------------------------------------------------------------------|:-------------------------|------------------------------------------:|-----------------------------------------:|-----------------------------------------:|-------------------------------------------:|------------------------------------------:|------------------------------------------:|-----------------------------------------:|
| 170 | 0x            | zrx      | 0x            | https://assets.coingecko.com/coins/images/863/large/0x.png?1547034672                 |       0.192066  |    162596592 |               171 |               1.91855e+08 |    7.92999e+06 |    0.198545  |    0.190939  |       -0.00511834  |                      -2.59572 |            -4.64766e+06 |                           -2.77897 |          8.47496e+08 |        1e+09   |      1e+09   |     2.5      |                -92.3016 | 2018-01-13T00:00:00.000Z |  0.120667   |                 59.3019 | 2020-03-13T02:27:49.563Z | {'times': 3.00137262387235, 'currency': 'usd', 'percentage': 300.137262387235}    | 2022-12-05T22:57:31.604Z |                                   6.39773 |                                 0.236744 |                                 -78.329  |                                   -48.4052 |                                 -2.59572  |                                  -31.7183 |                                -0.08195  |
|  97 | zilliqa       | zil      | Zilliqa       | https://assets.coingecko.com/coins/images/2687/large/Zilliqa-logo.png?1547036894      |       0.0227407 |    344299494 |                98 |               4.77046e+08 |    1.92004e+07 |    0.0235163 |    0.0226905 |       -0.000172456 |                      -0.75265 |            -2.93894e+06 |                           -0.84638 |          1.51564e+10 |        2.1e+10 |      2.1e+10 |     0.255376 |                -91.0876 | 2021-05-06T17:33:45.940Z |  0.00239616 |                849.86   | 2020-03-13T02:22:55.161Z | {'times': 1.131460045428967, 'currency': 'eth', 'percentage': 113.14600454289669} | 2022-12-05T22:57:22.010Z |                                   7.01544 |                                -0.119826 |                                 -67.7389 |                                   -52.7247 |                                 -0.752652 |                                  -30.9379 |                                -0.991144 |
| 189 | zencash       | zen      | Horizen       | https://assets.coingecko.com/coins/images/691/large/horizen.png?1555052241            |      10.64      |    139250373 |               190 |               2.22972e+08 |    5.44128e+06 |   11.07      |   10.62      |       -0.264045    |                      -2.42165 |            -3.61206e+06 |                           -2.52835 |          1.31149e+07 |        2.1e+07 |      2.1e+07 |   165.92     |                -93.5817 | 2021-05-08T06:00:30.087Z |  3.26       |                226.208  | 2019-10-17T00:00:00.000Z |                                                                                   | 2022-12-05T22:57:34.376Z |                                  21.2037  |                                -0.57332  |                                 -86.651  |                                   -44.0292 |                                 -2.42165  |                                  -25.8735 |                                11.1271   |
|  63 | zcash         | zec      | Zcash         | https://assets.coingecko.com/coins/images/486/large/circle-zcash-color.png?1547034197 |      46.24      |    602735976 |                64 |               9.69752e+08 |    3.57518e+07 |   47.32      |   45.31      |        0.479718    |                       1.04838 |             5.91658e+06 |                            0.99135 |          1.30523e+07 |        2.1e+07 |      2.1e+07 |  3191.93     |                -98.5521 | 2016-10-29T00:00:00.000Z | 19.75       |                133.959  | 2020-03-13T02:20:55.002Z |                                                                                   | 2022-12-05T22:57:30.607Z |                                  21.4551  |                                 0.502131 |                                 -75.4374 |                                   -53.9461 |                                  1.04838  |                                  -14.1037 |                                13.3262   |
| 141 | yearn-finance | yfi      | yearn.finance | https://assets.coingecko.com/coins/images/11849/large/yfi-192x192.png?1598325330      |    7082.34      |    220754373 |               142 |               2.59099e+08 |    4.54938e+07 | 7472.6       | 7052.76      |     -157.22        |                      -2.17168 |            -5.96275e+06 |                           -2.63004 |      31239.8         |    36666       |  36666       | 90787        |                -92.1948 | 2021-05-12T00:29:37.713Z | 31.65       |              22292.3    | 2020-07-18T12:26:27.150Z |                                                                                   | 2022-12-05T22:57:24.815Z |                                  15.7094  |                                -0.124164 |                                 -71.239  |                                   -22.0297 |                                 -2.17168  |                                  -15.4178 |                                13.2592   |

Coins can be filtered by category. For a list of defined categories enter:

```python
categories:dict = openbb.crypto.disc.categories_keys()
```

The category chosen below is called, `big-data`.

```python
openbb.crypto.disc.coins(category = categories[10], sortby = 'market_cap').head(5)
```

|    | id               | symbol   | name     | image                                                                                    |   current_price |   market_cap |   market_cap_rank |   fully_diluted_valuation |     total_volume |   high_24h |   low_24h |   price_change_24h |   price_change_percentage_24h |   market_cap_change_24h |   market_cap_change_percentage_24h |   circulating_supply |   total_supply |   max_supply |       ath |   ath_change_percentage | ath_date                 |        atl |   atl_change_percentage | atl_date                 | roi                                                                                 | last_updated             |   price_change_percentage_14d_in_currency |   price_change_percentage_1h_in_currency |   price_change_percentage_1y_in_currency |   price_change_percentage_200d_in_currency |   price_change_percentage_24h_in_currency |   price_change_percentage_30d_in_currency |   price_change_percentage_7d_in_currency |
|---:|:-----------------|:---------|:---------|:-----------------------------------------------------------------------------------------|----------------:|-------------:|------------------:|--------------------------:|-----------------:|-----------:|----------:|-------------------:|------------------------------:|------------------------:|-----------------------------------:|---------------------:|---------------:|-------------:|----------:|------------------------:|:-------------------------|-----------:|------------------------:|:-------------------------|:------------------------------------------------------------------------------------|:-------------------------|------------------------------------------:|-----------------------------------------:|-----------------------------------------:|-------------------------------------------:|------------------------------------------:|------------------------------------------:|-----------------------------------------:|
|  0 | dock             | dock     | Dock     | https://assets.coingecko.com/coins/images/3978/large/dock-icon-dark-large.png?1623764407 |       0.0163913 |  7.04484e+07 |               295 |             nan           | 567668           |  0.0170636 | 0.0163263 |       -0.00031004  |                      -1.85637 |            -2.34457e+06 |                           -3.22088 |          0           |          1e+09 |      nan     |  0.241848 |                -93.2225 | 2018-05-04T05:29:09.155Z | 0.00259319 |                532.083  | 2020-03-13T02:24:35.312Z | {'times': -0.8420344706449371, 'currency': 'eth', 'percentage': -84.20344706449372} | 2022-12-05T23:04:48.481Z |                                   11.105  |                                 0.113349 |                                 -79.607  |                                   -17.3245 |                                 -1.85637  |                                 -19.6563  |                                 0.481131 |
|  1 | covalent         | cqt      | Covalent | https://assets.coingecko.com/coins/images/14168/large/covalent-cqt.png?1624545218        |       0.099484  |  4.18854e+07 |               431 |               9.95348e+07 | 997478           |  0.112201  | 0.095826  |       -0.0110446   |                      -9.99251 |            -4.62241e+06 |                           -9.93901 |          4.20811e+08 |          1e+09 |        1e+09 |  2.08     |                -95.2091 | 2021-08-14T05:30:40.858Z | 0.051932   |                 91.5619 | 2022-08-01T23:38:54.301Z |                                                                                     | 2022-12-05T23:04:47.896Z |                                   16.5464 |                                 1.49149  |                                 -87.4469 |                                   -34.8706 |                                 -9.99251  |                                 -21.1618  |                               -16.3863   |
|  2 | gxchain          | gxc      | GXChain  | https://assets.coingecko.com/coins/images/1089/large/26296223.png?1571192241             |       0.46468   |  3.48511e+07 |               476 |             nan           | 114097           |  0.797016  | 0.359858  |       -0.331496    |                     -41.636   |            -2.48954e+07 |                          -41.6683  |          7.5e+07     |          1e+08 |      nan     | 10.61     |                -95.62   | 2018-01-13T00:00:00.000Z | 0.189778   |                144.839  | 2020-03-13T02:24:02.919Z |                                                                                     | 2022-12-05T23:04:01.358Z |                                   25.3322 |                                 3.68092  |                                 -83.5683 |                                    13.1713 |                                -41.636    |                                  -0.22209 |                                31.9026   |
|  3 | insights-network | instar   | INSTAR   | https://assets.coingecko.com/coins/images/3504/large/2558.png?1547038269                 |       0.0362529 |  2.85208e+07 |               534 |             nan           |     19.93        |  0.0370935 | 0.0359575 |       -0.000214289 |                      -0.58762 |            -5.51571e+06 |                          -16.2053  |          0           |          3e+08 |      nan     |  0.27882  |                -86.9978 | 2022-10-02T09:16:16.012Z | 0.00467988 |                674.655  | 2020-03-13T02:22:38.395Z | {'times': -0.7583139455766651, 'currency': 'usd', 'percentage': -75.83139455766651} | 2022-12-05T18:39:15.686Z |                                   -1.2191 |                               nan        |                                  27.2158 |                                   113.695  |                                 -0.587622 |                                 -44.2698  |                                 3.3329   |
|  4 | bonfida          | fida     | Bonfida  | https://assets.coingecko.com/coins/images/13395/large/bonfida.png?1658327819             |       0.392327  |  2.36672e+07 |               585 |               3.92307e+08 |      6.01989e+06 |  0.401193  | 0.386429  |       -0.00802685  |                      -2.00494 |       -441335           |                           -1.83062 |          6.03284e+07 |          1e+09 |        1e+09 | 18.77     |                -97.9102 | 2021-11-03T20:34:33.492Z | 0.113165   |                246.695  | 2020-12-22T10:58:52.143Z |                                                                                     | 2022-12-05T23:04:56.497Z |                                  -31.5948 |                                -0.13385  |                                 -94.9581 |                                   -30.7982 |                                 -2.00494  |                                  -5.84654 |                               -12.1443   |

### Trending

Print the trending coins on CoinGecko:

```python
openbb.crypto.disc.trending()
```

|    | Symbol        | Name          |   market_cap Cap Rank |
|---:|:--------------|:--------------|----------------------:|
|  0 | chainlink     | Chainlink     |                    21 |
|  1 | magiccraft    | MagicCraft    |                   806 |
|  2 | apollo        | Apollo        |                   858 |
|  3 | gmx           | GMX           |                    86 |
|  4 | dawn-protocol | Dawn Protocol |                   406 |
|  5 | evmos         | Evmos         |                   149 |
|  6 | maple         | Maple         |                   443 |
|  7 | aptos         | Aptos         |                    59 |

### Losers

Filter coins by the changes over various windows of time, from an hour to a year.

```python
openbb.crypto.disc.losers().head(3)
```

|    | Symbol   | Name                |      Price [$] |   Market Cap |   Market Cap Rank |   Volume [$] |   Change 1h [%] |
|---:|:---------|:--------------------|---------------:|-------------:|------------------:|-------------:|----------------:|
| 34 | ape      | ApeCoin             |     3.95       |   1430668301 |                35 |    225914151 |     -0.613265   |
| 48 | theta    | Theta Network       |     0.879573   |    880099193 |                49 |     19024380 |     -0.159237   |
| 12 | ltc      | Litecoin            |    80.28       |   5764526837 |                13 |   1079151325 |     -0.147648   |

Compared to the last fourteen days:

```python
openbb.crypto.disc.losers(interval = '14d').head(3)
```

|    | Symbol   | Name      |   Price [$] |   Market Cap |   Market Cap Rank |   Volume [$] |   Change 14d [%] |
|---:|:---------|:----------|------------:|-------------:|------------------:|-------------:|-----------------:|
| 31 | algo     | Algorand  |    0.237655 |   1691877131 |                32 |     79911891 |         -3.84964 |
| 22 | leo      | LEO Token |    3.79     |   3541787576 |                23 |      2082712 |         -2.70556 |
| 38 | flow     | Flow      |    1.11     |   1150005942 |                39 |     44608861 |         -2.16063 |

Over one-year:

```python
openbb.crypto.disc.losers(interval = '1y').head(3)
```

|    | Symbol   | Name               |   Price [$] |   Market Cap |   Market Cap Rank |   Volume [$] |   Change 1y [%] |
|---:|:---------|:-------------------|------------:|-------------:|------------------:|-------------:|----------------:|
| 39 | lunc     | Terra Luna Classic |  0.00017433 |   1042097683 |                40 |     75780496 |        -99.9997 |
| 16 | sol      | Solana             | 13.87       |   5045641411 |                17 |    382220595 |        -92.9463 |
| 43 | axs      | Axie Infinity      |  8.92       |   1004779023 |                44 |    707998935 |        -91.6799 |

