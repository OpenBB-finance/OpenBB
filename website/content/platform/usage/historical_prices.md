---
title: Historical Prices
sidebar_position: 4
description: This page provides an introduction to financial statement data available in the OpenBB
  Platform.  This includes quarterly and annual reports, along with metrics and ratios by company.
  This guide provides examples for using the variety of sources.
keywords:
- stocks
- companies
- prices
- historical
- ohlc
- intraday
- intervals
- market data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Historical Prices - Usage | OpenBB Platform Docs" />

Historical market prices typically come in the form of OHLC+V - open, high, low, close, volume.  There may be additional fields returned by a provider, but those are the expected columns. Granularity and amount of historical data will vary by provider and subscription status. Visit their websites to understand what your entitlements are.

:::info
These examples will assume that the OpenBB Platform is initialized in a Python session.

```python
from openbb import obb
import pandas as pd
```

:::

## Historical OHLC

The `historical` function is located under a submodule for each asset type. In the `openbb-equity` module.

```python
help(obb.equity.price.historical)
```

- This endpoint has the most number of providers out of any function. At the time of writing, choices are:

['alpha_vantage', 'cboe', 'fmp', 'intrinio', 'polygon', 'tiingo', 'yfinance']

- Common parameters have been standardized across all sources, `start_date`, `end_date`, `interval`.

- The default interval will be `1d`.

- The depth of historical data and choices for granularity will vary by provider and subscription status. Refer to the website and documentation of each source understand your specific entitlements.

- Despite being in the `equity` module, it's might be possible to get other asset types, like currencies or crypto, from the same endpoint.

- For demonstration purposes, we will use the `openbb-yfinance` data extension.

```python
df_daily = obb.equity.price.historical(symbol = "spy", provider="yfinance")
df_daily.to_df().head(1)
```

| date          |   open |   high |    low |   close |     volume |   dividends |   stock splits |   capital gains |
|:--------------|-------:|-------:|-------:|--------:|-----------:|------------:|---------------:|----------------:|
| 2022-11-22  | 396.63 | 400.07 | 395.15 |   399.9 | 60429000 |           0 |              0 |               0 |

To load the entire history available from a source, pick a starting date well beyond what it might be. For example, `1900-01-01`

```python
df_daily =(
  obb.equity.price.historical(symbol = "spy", start_date = "1990-01-01", provider="yfinance")
  .to_df()
)
df_daily.head(1)
```

| date          |   open |   high |   low |   close |     volume |   dividends |   stock splits |   capital gains |
|:--------------|-------:|-------:|------:|--------:|-----------:|------------:|---------------:|----------------:|
| 1993-01-29  |  43.97 |  43.97 | 43.75 |   43.94 | 1003200 |           0 |              0 |               0 |

### Intervals

The intervals are entered according to this pattern:

- `1m` = One Minute
- `1h` = One Hour
- `1d` = One Day
- `1W` = One Week
- `1M` = One Month

The date for monthly value is the first or last, depending on the provider. This can be easily resampled from daily data.

```python
df_monthly = (
  obb.equity.price.historical("spy", start_date="1990-01-01", interval="1M", provider="yfinance")
  .to_df()
)
df_monthly.tail(2)
```

| date          |   open |   high |    low |   close |      volume |   dividends |   stock splits |   capital gains |
|:--------------|-------:|-------:|-------:|--------:|------------:|------------:|---------------:|----------------:|
| 2023-10-01  | 426.62 | 438.14 | 409.21 |  418.2  | 1999149700 |           0 |              0 |               0 |
| 2023-11-01  | 419.2  | 456.38 | 418.65 |  455.02 | 1161239576 |           0 |              0 |               0 |

### Resample a Time Series

`yfinance` returns the monthly data for the first day of each month. Let's resample it to take from the last, using the daily information captured in the previous cells.

```python
(
    df_daily[["open", "high", "low", "close", "volume"]]
    .resample("M")
    .agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    ).tail(2)
)
```

| date          |   open |   high |    low |   close |      volume |
|:--------------|-------:|-------:|-------:|--------:|------------:|
| 2023-10-31  | 426.62 | 438.14 | 409.21 |  418.2  | 1999149700 |
| 2023-11-30  | 419.2  | 456.38 | 418.65 |  455.02 | 1210484176 |

We can see that the current month's total volume is higher when we resample the daily time series. It is difficult to know where the discrepancy lays, and it may just be a temporary glitch. However, we can verify that the total volume, according to YahooFinance, is the number we just sampled.

:::note
If you are following along, the results will not match exactly what is displayed here.
:::

```python
df_daily.loc["2023-11-01":].sum()["volume"]
```

```console
1210484176
```

### Differences Between Sources

To demonstrate the difference between sources, let's compare values for daily volume from several sources.

```python
# Collect the data

yahoo = obb.equity.price.historical("spy", provider="yfinance").to_df()
alphavantage = obb.equity.price.historical("spy", provider = "alpha_vantage").to_df()
intrinio = obb.equity.price.historical("spy", provider="intrinio").to_df()
fmp = obb.equity.price.historical("spy", provider="fmp").to_df()

# Make a new DataFrame with just the volume columns
compare = pd.DataFrame()
compare["AV Volume"] = alphavantage["volume"].tail(10)
compare["FMP Volume"] = fmp["volume"].tail(10)
compare["Intrinio Volume"] = intrinio["volume"].tail(10)
compare["Yahoo Volume"] = yahoo["volume"].tail(10)

compare
```

| date          |   AV Volume |   FMP Volume |   Intrinio Volume |   Yahoo Volume |
|:--------------|------------:|-------------:|------------------:|---------------:|
| 2023-11-09  | 83174417 |     83071417 |       83174417 |       83174400 |
| 2023-11-10  | 89558054 |     89558054 |       89558054 |       89462200 |
| 2023-11-13  | 52236068 |     52192568 |       52236068 |       52236100 |
| 2023-11-14  | 97176935 |     97130503 |      97176935 |       97176900 |
| 2023-11-15  | 77327573 |     77327573 |      77327573 |       77327600 |
| 2023-11-16  | 66665797 |     66654468 |       66665797 |       66665800 |
| 2023-11-17  | 83193902 |     83193902 |       83193902 |       83133200 |
| 2023-11-20  | 70055633 |     69614633 |       70055633 |       69936200 |
| 2023-11-21  | 49244639 |     49244639 |       49244639 |       49244600 |
| 2023-11-22  | 59446573 |     59313820 |       58205780 |       59394900 |

## Other Types of Symbols

Other types of assets and ticker symbols can be loaded from `obb.equity.price.historical()`, below are some examples but not an exhaustive list.

### Share Classes

Some sources use `-` as the distinction between a share class, e.g., `BRK-A` and `BRK-B`. Other formats include:

- A period: `BRK.A`
- A slash: `BRK/A`
- No separator, the share class becomes the fourth or fifth letter.

```python
obb.equity.price.historical("brk.b", provider="polygon")
```

```python
obb.equity.price.historical("brk-b", provider="fmp")
```

While some providers handle the different formats on their end, others do not. This is something to consider when no results are returned from one source. Some may even use a combination, or accept multiple variations. Sometimes there is no real logic behind the additional characters, `GOOGL` vs. `GOOG`. These are known unknown variables of ticker symbology, what's good for one source may return errors from another.

### Regional Identifiers

With providers supporting market data from multiple jurisdictions, the most common method for requesting data outside of US-listings is to append a suffix to the ticker symbol (e.g., `RELIANCE.NS`). Formats may be unique to a provider, so it is best to review the source's documentation for an overview of their specific conventions. [This page](https://help.yahoo.com/kb/SLN2310.html) on Yahoo describes how they format symbols, which many others follow to some degree.

### Indices

Sources will have their own treatment of these symbols, some examples are:

- YahooFinance/FMP/CBOE: ^RUT
- Polygon: I:NDX

```python
obb.equity.price.historical("^RUT", provider="cboe").to_df().tail(1)
```

| date          |    open |    high |     low |   close |   volume |
|:--------------|--------:|--------:|--------:|--------:|---------:|
| 2023-11-22  | 1796.37 | 1804.96 | 1785.93 | 1792.92 |        0 |

```python
obb.equity.price.historical("^RUT", provider="fmp").to_df().tail(1)
```

| date          |    open |    high |     low |   close |   volume |    vwap | label           |   adj_close |   unadjusted_volume |   change |   change_percent |   change_over_time |
|:--------------|--------:|--------:|--------:|--------:|---------:|--------:|:----------------|------------:|--------------------:|---------:|-----------------:|-------------------:|
| 2023-11-22  | 1792.51 | 1803.12 | 1789.88 | 1795.54 |        0 | 1796.18 | November 22, 23 |     1795.54 |                   0 |  3.02893 |          0.16898 |          0.0016898 |

:::info
**For an endpoint geared more specifically towards indices, try `obb.index.market()`**
:::

### Currencies

FX symbols face the same dilemma as share classes, there are several variations of the same symbol.

- YahooFinance: `EURUSD=X`
- Polygon: `C:EURUSD`
- AlphaVantage/FMP: `EURUSD`

:::info
**The symbol prefixes are handled internally when `obb.currency.price.historical()` is used, enter as a pair with no extra characters.**
:::

```python
obb.equity.price.historical("EURUSD=X", provider="yfinance").to_df().tail(1)
```

| date          |   open |   high |    low |   close |   volume |   dividends |   stock splits |
|:--------------|-------:|-------:|-------:|--------:|---------:|------------:|---------------:|
| 2023-11-22  | 1.0918 | 1.0923 | 1.0855 |  1.0918 |        0 |           0 |              0 |

```python
obb.equity.price.historical("C:EURUSD", provider="polygon").to_df().tail(1)
```

| date          |    open |   high |    low |   close |   volume |   vwap |   transactions |
|:--------------|--------:|-------:|-------:|--------:|---------:|-------:|---------------:|
| 2023-11-21  | 1.09168 | 1.0923 | 1.0851 |  1.0888 |   155827 | 1.0893 |         155827 |

### Crypto

Similar, but different to FX tickers.

- YahooFinance: `BTC-USD`
- Polygon: `X:BTCUSD`
- AlphaVantage/FMP: `BTCUSD`

:::info
**The symbol prefixes are handled internally when `obb.crypto.price.historical()` is used, enter as a pair with no extra characters and placing the fiat currency second.**
:::

```python
obb.equity.price.historical("X:BTCUSD", provider="polygon").to_df().tail(1)
```

| date          |   open |   high |   low |   close |   volume |    vwap |   transactions |
|:--------------|-------:|-------:|------:|--------:|---------:|--------:|---------------:|
| 2023-11-21  |  35756 |  37900 | 35633 | 37433.8 |  30411.4 | 36841.5 |         464907 |

As noted above, `X:` or other prefixes are not required when using the `crypto` version of this same endpoint.

```python
obb.crypto.price.historical("BTCUSD", provider="polygon").to_df().tail(1)
```

| date          |   open |   high |   low |   close |   volume |    vwap |   transactions |
|:--------------|-------:|-------:|------:|--------:|---------:|--------:|---------------:|
| 2023-11-21  |  35756 |  37900 | 35633 | 37433.8 |  30411.4 | 36841.5 |         464907 |

### Futures

Historical prices for the continuation chart, can be fetched by the `fmp` or `yfinance` data extensions.  Individual active contracts are returned by `yfinance`.

- Continuous front-month: `CL=F`
- December 2023 contract: `CLZ24.NYM`
- March 2024 contract: `CLH24.NYM`

Individual contracts will require knowing which of the CME venues the future is listed on. `["NYM", "NYB", "CME", "CBT"]`.

```python
obb.equity.price.historical("CL=F", provider="fmp").to_df().tail(1)
```

| date          |   open |   high |   low |   close |   volume |   vwap | label           |   adj_close |   unadjusted_volume |   change |   change_percent |   change_over_time |
|:--------------|-------:|-------:|------:|--------:|---------:|-------:|:----------------|------------:|--------------------:|---------:|-----------------:|-------------------:|
| 2023-11-22 |  77.77 |  77.97 | 73.79 |   76.78 |   368686 |  76.18 | November 22, 23 |       76.78 |              368686 |    -0.99 |            -1.27 |            -0.0127 |

```python
obb.equity.price.historical("CLZ24.NYM", provider="yfinance").to_df().tail(1)
```

| date          |   open |   high |   low |   close |   volume |   dividends |   stock splits |
|:--------------|-------:|-------:|------:|--------:|---------:|------------:|---------------:|
| 2023-11-22  |  74.07 |  74.07 | 73.41 |   73.46 |      610 |           0 |              0 |

### Options

Individual options contracts are also loadable from `openbb.equity.price.historical()`.

- YahooFinance: `SPY241220P00400000`
- Polygon: `O:SPY241220P00400000`

```python
obb.equity.price.historical("SPY241220P00400000", provider="yfinance").to_df().tail(1)
```

| date                |   open |   high |   low |   close |   volume |   dividends |   stock splits |
|:--------------------|-------:|-------:|------:|--------:|---------:|------------:|---------------:|
| 2023-11-22 00:00:00 |   10.5 |  10.82 | 10.25 |   10.61 |       77 |           0 |              0 |

```python
obb.equity.price.historical("O:SPY241220P00400000", provider="polygon").to_df().tail(1)
```

| date          |   open |   high |   low |   close |   volume |    vwap |   transactions |
|:--------------|-------:|-------:|------:|--------:|---------:|--------:|---------------:|
| 2023-11-20  |   10.9 |  10.95 | 10.75 |   10.75 |       17 | 10.8376 |             10 |
