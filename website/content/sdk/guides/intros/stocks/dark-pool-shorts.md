---
title: Dark Pools and Short Data
---

The `DPS` sub-module contains the commands from the [Dark Pools and Short Data menu](https://docs.openbb.co/terminal/guides/intros/stocks/dark-pool-shorts) within the OpenBB Terminal. These functions are meant to supplement other research on technical trading factors, settlement schedules, market flow, and volume dynamics. Commands are specifically for US-listed equities, and the data is reported to [FINRA](https://www.finra.org/#/) on a lagging schedule. Some will also have a `_chart` companion.

## How to Use

Each function contained within the `openbb.stocks.dps` module is listed below with a short description.

|Path |Description |
|:----|-----------:|
|openbb.stocks.dps.ctb |Current Borrow Rates from Interactive Brokers |
|openbb.stocks.dps.dpotc |Weekly Volume Totals for a Ticker on ATS and OTC Venues |
|openbb.stocks.dps.ftd |Historical Fails-to-Deliver Numbers |
|openbb.stocks.dps.hsi |Stocks With High Reported Short Interest |
|openbb.stocks.dps.pos |Top Short Volumes From Last Trading Day |
|openbb.stocks.dps.prom |Tickers With Growing Trade Activity on ATS Tapes |
|openbb.stocks.dps.psi |Price vs. Short Volume |
|openbb.stocks.dps.shorted |Most Shorted Stocks According to Yahoo Finance |
|openbb.stocks.dps.sidtc |Short Interest and Days-to-Cover |
|openbb.stocks.dps.spos |Rolling 20-Day Net Short Volume of a Single Stock|

## Examples

### Import Statements

Start out the Python script or Notebook file with the familiar statements:

```python
from openbb_terminal.sdk import openbb
import pandas as pd
```

### CTB

`openbb.stocks.dps.ctb` gets the current borrow rate and availability, on Interactive Brokers, for all tickers.

```python
ctb_df = openbb.stocks.dps.ctb()

ctb_df
```

|    | Symbol   | Fees      |   Available |
|---:|:---------|:----------|------------:|
|  0 | PCF      | 864.8795% |      100000 |
|  1 | EPR PRE  | 625.0102% |       80000 |
|  2 | KITT     | 574.4353% |         100 |
|  3 | EFSH     | 439.7636% |        2000 |
|  4 | EVTL     | 434.336%  |        9000 |
| 17655 | DSAIF    | 0.0%   |        1000 |
| 17656 | DRREF    | 0.0%   |       25000 |
| 17657 | DOSEF    | 0.0%   |         100 |
| 17658 | DMYY     | 0.0%   |      100000 |
| 17659 | DLICY    | 0.0%   |         100 |

### POS

`openbb.stocks.dps.pos` represents the cumulative net short dollar volume (Dark Pool Position $) by security. Is it calculated by taking the net short volume (short volume minus buy volume - a positive number means that the short volume was higher than the buy volume) times the closing price and taking the 20-day cumulative sum of this series. [Source: Stockgrid.io](https://www.stockgrid.io/darkpools)

- Net Short Volume: Short volume minus buy volume.
- Net Short Volume $: Net short volume multiplied by the last close.
- Position: The sum of the net short volume over the last 20 trading days.
- Position $: Position multiplied by the last close.

Data is updated at 6pm EST.

The function returns up to 400 results, applying `ascend = True` unlocks the most negative values.

```python
pos_high = openbb.stocks.dps.pos()
pos_high = pos_high.convert_dtypes()
pos_high.set_index('Date', inplace = True)
pos_low = openbb.stocks.dps.pos(ascend = True)
pos_low = pos_low.convert_dtypes()
pos_low.set_index('Date', inplace = True)
pos_df = pd.concat([pos_low,pos_high])
pos_df.sort_values(by=['Dark Pools Position $'], ascending = False, inplace = True)

pos_df
```

| Date       | Ticker   |   Short Volume |   Short Volume % |   Net Short Volume |   Net Short Volume $ |   Dark Pools Position |   Dark Pools Position $ |
|:-----------|:---------|---------------:|-----------------:|-------------------:|---------------------:|----------------------:|------------------------:|
| 2022-11-25 | SPY      |       10511774 |         0.638082 |            4549536 |          1.83041e+09 |             109490269 |             4.27107e+10 |
| 2022-11-25 | QQQ      |        2952642 |         0.490496 |            -114422 |         -3.283e+07   |             130622909 |             3.6231e+10  |
| 2022-11-25 | NVDA     |        6264211 |         0.62147  |            2448753 |          3.98412e+08 |              61850799 |             1.00604e+10 |
| 2022-11-25 | IWM      |        3932703 |         0.541717 |             605706 |          1.12407e+08 |              34431260 |             6.31318e+09 |
| 2022-11-25 | HYG      |        1170511 |         0.523497 |             105076 |          7.88175e+06 |              75184813 |             5.53232e+09 |
| 2022-11-25 | META     |        1652587 |         0.359614 |           -1290276 |         -1.4375e+08  |             -88892626 |            -8.17035e+09 |
| 2022-11-25 | SQQQ     |        6198104 |         0.358094 |           -4912392 |         -2.20223e+08 |            -160324410 |            -8.81487e+09 |
| 2022-11-25 | MSFT     |        1246644 |         0.356497 |           -1003640 |         -2.48391e+08 |             -60211625 |            -1.41156e+10 |
| 2022-11-25 | TSLA     |       14145558 |         0.480631 |           -1140119 |         -2.08482e+08 |            -106217407 |            -2.06849e+10 |
| 2022-11-25 | AMZN     |        9907246 |         0.467855 |           -1361394 |         -1.27168e+08 |            -238062247 |            -2.26635e+10 |

### SPOS

`openbb.stocks.dps.spos` is a section of the same data above, but as a time-series for individual tickers. There is one-year of daily historical data available.

```python
spy_spos = openbb.stocks.dps.spos('SPY')

spy_spos.tail(5)
```

|    | dates               |   Net Short Vol. (1k $) |   Position (1M $) |
|---:|:--------------------|------------------------:|------------------:|
|  4 | 2021-12-03 00:00:00 |                 1218.48 |          10786    |
|  3 | 2021-12-02 00:00:00 |                 3224.17 |           9567.52 |
|  2 | 2021-12-01 00:00:00 |                 2558.79 |           6343.35 |
|  1 | 2021-11-30 00:00:00 |                 2737.27 |           3784.56 |
|  0 | 2021-11-29 00:00:00 |                 1047.29 |           1047.29 |

### PSI

Price vs.Short Interest. This function has two data sources, with their own syntax. `openbb.stocks.dps.psi_sg` will return the other columns `openbb.stocks.dps.spos` is missing. The example below puts them all together.

```python
spy_spos = openbb.stocks.dps.spos('SPY')
spy_spos.rename(columns = {'dates':'date'}, inplace= True)
spy_spos.set_index(keys = 'date', inplace =True)
spy_psi,spy_price = openbb.stocks.dps.psi_sg('SPY')
spy_psi.set_index('date', inplace = True)
spy_pos = spy_psi.join(spy_spos)

spy_pos
```

| date                |   Short Vol. [1M] |   Short Vol. % |   Short Exempt Vol. [1k] |   Total Vol. [1M] |   Net Short Vol. (1k $) |   Position (1M $) |
|:--------------------|------------------:|---------------:|-------------------------:|------------------:|------------------------:|------------------:|
| 2022-11-25 00:00:00 |          10.5118  |          63.81 |                   37.129 |           16.474  |               1830.41   |          42710.7  |
| 2022-11-23 00:00:00 |          13.6484  |          60.55 |                   91.552 |           22.5399 |               1914.28   |          42099.3  |
| 2022-11-22 00:00:00 |          10.0279  |          53.85 |                   52.335 |           18.6233 |                572.874  |          42444.8  |
| 2022-11-21 00:00:00 |           9.42557 |          57.6  |                   61.242 |           16.3632 |                981.734  |          42187.3  |
| 2022-11-18 00:00:00 |          18.445   |          60.68 |                  112.603 |           30.3973 |               2571.31   |          42352.3  |
| 2022-02-16 00:00:00 |          11.0333  |          52.77 |                    7.958 |           20.909  |                516.966  |          19836.2  |
| 2022-02-15 00:00:00 |          11.8138  |          57.01 |                   36.259 |           20.7236 |               1295.52   |          21808.3  |
| 2022-02-14 00:00:00 |          12.744   |          53.08 |                   50.473 |           24.0105 |                648.705  |          19105.9  |
| 2022-02-11 00:00:00 |          14.1183  |          46.63 |                   55.511 |           30.2776 |               -898.962  |          17553.7  |
| 2022-02-10 00:00:00 |          22.5696  |          62.98 |                   46.454 |           35.834  |               4181.07   |          21316.8  |

The other version of this command is, `openbb.stocks.dps.psi_q`. It returns daily short volume from Nasdaq and NYSE separately, with daily historic data going back to 2013, and is sourced by Quandl. The first table below is the short volume and from Nasdaq.

```python
nasdaq_psi = openbb.stocks.dps.psi_q(nyse=False, symbol = 'SPY')

nasdaq_psi.head(5)
```

| Date                |   ShortVolume |   ShortExemptVolume |   TotalVolume |
|:--------------------|--------------:|--------------------:|--------------:|
| 2013-04-01 00:00:00 |   8.99908e+06 |                3500 |   1.92365e+07 |
| 2013-04-02 00:00:00 |   1.15943e+07 |                6600 |   2.09414e+07 |
| 2013-04-03 00:00:00 |   1.89638e+07 |               13418 |   2.83739e+07 |
| 2013-04-04 00:00:00 |   1.29551e+07 |                7586 |   1.99661e+07 |
| 2013-04-05 00:00:00 |   1.43612e+07 |                   0 |   2.81504e+07 |

The second table is from NYSE

```python
nyse_psi = openbb.stocks.dps.psi_q(nyse=True, symbol = 'SPY')

nyse_psi.head(5)
```

| Date                |   ShortVolume |   ShortExemptVolume |   TotalVolume |
|:--------------------|--------------:|--------------------:|--------------:|
| 2013-04-01 00:00:00 |   1.04127e+06 |                3800 |   1.61224e+06 |
| 2013-04-02 00:00:00 |   1.47136e+06 |                4500 |   1.9255e+06  |
| 2013-04-03 00:00:00 |   2.43128e+06 |                   0 |   3.23342e+06 |
| 2013-04-04 00:00:00 |   1.55106e+06 |                 800 |   2.28563e+06 |
| 2013-04-05 00:00:00 |   1.94417e+06 |                 300 |   2.93733e+06 |

Let's join them together:

```python
nyse_psi.join(nasdaq_psi, lsuffix = ' (NYSE)', rsuffix = ' (NQ)')
```

| Date                |   ShortVolume (NYSE) |   ShortExemptVolume (NYSE) |   TotalVolume (NYSE) |   ShortVolume (NQ) |   ShortExemptVolume (NQ) |   TotalVolume (NQ) |
|:--------------------|---------------------:|---------------------------:|---------------------:|-------------------:|-------------------------:|-------------------:|
| 2013-04-01 00:00:00 |          1.04127e+06 |                       3800 |          1.61224e+06 |        8.99908e+06 |           3500           |        1.92365e+07 |
| 2013-04-02 00:00:00 |          1.47136e+06 |                       4500 |          1.9255e+06  |        1.15943e+07 |           6600           |        2.09414e+07 |
| 2013-04-03 00:00:00 |          2.43128e+06 |                          0 |          3.23342e+06 |        1.89638e+07 |          13418           |        2.83739e+07 |
| 2013-04-04 00:00:00 |          1.55106e+06 |                        800 |          2.28563e+06 |        1.29551e+07 |           7586           |        1.99661e+07 |
| 2013-04-05 00:00:00 |          1.94417e+06 |                        300 |          2.93733e+06 |        1.43612e+07 |              0           |        2.81504e+07 |
| 2022-11-21 00:00:00 |     838081           |                        171 |          2.05784e+06 |        8.47984e+06 |          61071           |        1.41414e+07 |
| 2022-11-22 00:00:00 |          1.24058e+06 |                        273 |          2.45227e+06 |        8.70804e+06 |          52062           |        1.60467e+07 |
| 2022-11-23 00:00:00 |          1.82258e+06 |                        524 |          3.35511e+06 |        1.17129e+07 |          91028           |        1.90024e+07 |
| 2022-11-25 00:00:00 |     410318           |                        353 |     804984           |        1.00677e+07 |          36776           |        1.56151e+07 |

### HSI

`openbb.stocks.dps.hsi` lists the stocks with the highest reported short interest from NYSE or Nasdaq.

```python
openbb.stocks.dps.hsi()
```

|    | Ticker   | Company                        | Exchange   | ShortInt   | Float   | Outstd   | Industry                                   |
|---:|:---------|:-------------------------------|:-----------|:-----------|:--------|:---------|:-------------------------------------------|
|  0 |          |                                |            |            |         |          |                                            |
|  1 | BBBY     | Bed Bath & Beyond Inc.         | Nasdaq     | 45.11%     | 76.45M  | 80.36M   | Retail (Specialty Non-Apparel)             |
|  2 | CVNA     | Carvana Co                     | NYSE       | 44.24%     | 93.40M  | 105.95M  | Retail (Specialty Non-Apparel)             |
|  3 | BYND     | Beyond Meat Inc                | Nasdaq     | 42.75%     | 57.25M  | 63.74M   | Food Processing                            |
|  4 | MSTR     | MicroStrategy Inc              | Nasdaq     | 40.51%     | 9.34M   | 9.35M    | Software & Programming                     |
| 31 | SPCE     | Virgin Galactic Holdings Inc   | NYSE       | 20.98%     | 208.85M | 274.56M  | Aerospace & Defense                        |
| 32 | PETS     | Petmed Express Inc             | Nasdaq     | 20.83%     | 19.74M  | 21.08M   | Retail (Drugs)                             |
| 33 | RIDE     | Lordstown Motors Corp          | Nasdaq     | 20.69%     | 162.40M | 216.98M  | Auto & Truck Manufacturers                 |
| 34 | FFIE     | Faraday Future Intelligent Ele | Nasdaq     | 20.67%     | 242.00M | 386.26M  | Auto & Truck Manufacturers                 |
| 35 | IGMS     | IGM Biosciences Inc            | Nasdaq     | 20.57%     | 17.31M  | 29.14M   | Biotechnology & Medical Research           |

