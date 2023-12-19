---
title: Forex
description: This guide introduces the Forex (FX) menu, in the OpenBB Terminal, and provides examples for use.  Features in this menu include historical prices and forward rates.  It also provides entry points to the QA, TA, and Forecast menus.
keywords:
- Forex
- currency trading
- currency pairs
- USD/EUR
- JPY/GBP
- quote
- candle
- forward rates
- fwd
- technical analysis
- forecasting
- Oanda
- historical data
- real-time currency exchange
- terminal
- quantitative analysis
- seasonality
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Forex - Menus | OpenBB Terminal Docs" />

The Forex menu includes features for historical prices, forward rates, and real-time exchange rates.  It also provides entry points to the [`/ta/`](/terminal/menus/common/ta.md), [`/qa`](/terminal/menus/common/qa.md), and [`/forecast`](/terminal/menus/forecast.md) menus.


## Usage

The Forex menu is entered by typing `forex`, from the Main menu, or with the absolute path:

```console
/forex
```

![Screenshot 2023-11-03 at 12 26 41 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/83356fc6-9966-4da3-9bed-64ae7e42ecd0)

### Load

The first step will be to load a pair of currencies.  The pairs are entered as a six-letter symbol, with the former of the pair being "from".

```console
load JPYUSD
```

Inversely:

```console
load USDJPY
```

### Quote

A `quote` from YahooFinance displays the last price and a timestamp when it was refreshed.

```console
/forex/load JPYUSD/quote
```

```console
Quote for JPY/USD

Last refreshed : 2023-11-03 19:30:00
Last value     : 0.006694381590932608
```

From AlphaVantage, a table is returned that includes a bid and ask.

```console
quote --source AlphaVantage
```

|                    | Realtime Currency Exchange Rate   |
|:-------------------|:----------------------------------|
| From_Currency Code | JPY                               |
| From_Currency Name | Japanese Yen                      |
| To_Currency Code   | USD                               |
| To_Currency Name   | United States Dollar              |
| Exchange Rate      | 0.00669000                        |
| Last Refreshed     | 2023-11-03 19:34:01               |
| Time Zone          | UTC                               |
| Bid Price          | 0.00668900                        |
| Ask Price          | 0.00669000                        |


### FWD

The `fwd` command gets a table with the term structure of a currency pair.

```console
/forex/load USDJPY/fwd
```

| Expiration    |     Ask |     Bid |     Mid |     Points |
|:--------------|--------:|--------:|--------:|-----------:|
| Overnight     | 149.397 | 149.368 | 149.383 |     0      |
| Tomorrow Next | 149.397 | 149.368 | 149.382 |    -2.33   |
| Spot Next     | 149.397 | 149.368 | 149.382 |    -2.325  |
| One Week      | 149.395 | 149.366 | 149.381 |   -16.315  |
| Two Weeks     | 149.394 | 149.365 | 149.379 |   -32.59   |
| Three Weeks   | 149.392 | 149.363 | 149.378 |   -48.89   |
| One Month     | 149.39  | 149.361 | 149.375 |   -70.1505 |
| Two Months    | 149.381 | 149.352 | 149.367 |  -155.31   |
| Three Months  | 149.375 | 149.346 | 149.36  |  -222.871  |
| Four Months   | 149.368 | 149.339 | 149.353 |  -290.68   |
| Five Months   | 149.36  | 149.331 | 149.346 |  -365.94   |
| Six Months    | 149.354 | 149.325 | 149.339 |  -431.97   |
| Seven Months  | 149.347 | 149.318 | 149.332 |  -500.22   |
| Eight Months  | 149.34  | 149.311 | 149.326 |  -567.58   |
| Nine Months   | 149.334 | 149.305 | 149.319 |  -630.18   |
| Ten Months    | 149.327 | 149.298 | 149.313 |  -697.4    |
| Eleven Months | 149.322 | 149.293 | 149.307 |  -753.2    |
| One Year      | 149.316 | 149.287 | 149.301 |  -812.9    |
| Two Years     | 149.256 | 149.227 | 149.242 | -1408.19   |
| Three Years   | 149.204 | 149.173 | 149.188 | -1943.13   |
| Four Years    | 149.158 | 149.127 | 149.142 | -2401.05   |
| Five Years    | 149.108 | 149.077 | 149.092 | -2904.72   |
| Six Years     | 149.08  | 149.048 | 149.064 | -3185.9    |
| Seven Years   | 149.047 | 149.014 | 149.03  | -3522.5    |
| Ten Years     | 148.948 | 148.912 | 148.93  | -4527.5    |
