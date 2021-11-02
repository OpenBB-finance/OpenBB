# ETF

Menu for Exchange Traded Funds.

Data is currently scraped from StockAnalysis.com/etf

* [search](#search)
  * search for ETFs matching an input
* [overview](#overview)
  * get ETF overview
* [holdings](#holdings)
  * show ETF holdings
* [compare](#compare)
  * compare multiple ETFs overview
* [screener](#screener)
  * screen ETFs

[WSJ](#WSJ)

* [gainers](#gainers)
  * show top gainers
* [decliners](#decliners)
  * show top decliners
* [active](#active)
  * show most active

## web <a name="web"></a>

```python
usage: web
```

Opens StockAnalysis.com/etf.  This site shows all available ETFs (currently > 2800).

## search <a name="search"></a>

```python
usage: search [-e --etf] [--export {csv,json,xlsx}]
```

Search for ETFs matching

* -e/--etf : Name to search for.  Can be a company or other search term
* --export {csv,json,xlsx} : Export to the selected file

Example Usage: Search for all ETFs that deal with AI

```python
(✨) (etf)> search artificial intelligence
BOTZ - Global X Robotics & Artificial Intelligence ETF
IRBO - iShares Robotics and Artificial Intelligence ETF
ROBT - First Trust Nasdaq Artificial Intelligence and Robotics ETF
THNQ - ROBO Global Artificial Intelligence ETF
UBOT - Daily Robotics, Artificial Intelligence & Automation Index Bull 3X Shares
```

Note that this searches for exact strings in the ETF name.  Searching for SPY will return nothing.

## overview <a name="overview"></a>

```python
usage: overview [-e --etf] [--export {csv,json,xlsx}]
```

* -e/--etf : ETF to get data for
* --export {csv,json,xlsx} : Export to the selected file

Returns the overview of the ETF.  Shows Last Price, Assets, Net Asset Value (NAV), Expense Ratio, PE Ratio, 5Year Beta,
Total Dividend and Dividend Yield.

Example will be a single column from the [compare](#compare) example.

## holdings <a name="holdings"></a>

```python
usage: overview [-e --etf] [-l --limit] [--export {csv,json,xlsx}]
```

* -e/--etf : Name of ETF to get data for.
* -l/--limit : Number of assets to show.  Max 200.  Defaults to 20.
* --export {csv,json,xlsx} : Export to the selected file

Returns the top holdings in the ETF.  Shows percentage and total shares held.

Example:

```text
(✨) (etf)> holdings spy -l 5
╒════╤══════════╤════════════╤═════════════╕
│    │ Ticker   │ % of ETF   │ Shares      │
╞════╪══════════╪════════════╪═════════════╡
│  0 │ AAPL     │ 5.66%      │ 162,078,640 │
├────┼──────────┼────────────┼─────────────┤
│  1 │ MSFT     │ 5.26%      │ 77,463,250  │
├────┼──────────┼────────────┼─────────────┤
│  2 │ AMZN     │ 3.89%      │ 4,396,091   │
├────┼──────────┼────────────┼─────────────┤
│  3 │ FB       │ 2.11%      │ 24,705,450  │
├────┼──────────┼────────────┼─────────────┤
│  4 │ GOOGL    │ 1.93%      │ 3,088,769   │
╘════╧══════════╧════════════╧═════════════╛
```

## compare <a name="compare"></a>

```python
usage: compare [-e --etfs] [--export {csv,json,xlsx}]
```

* -e/--etfs : ETFs to compare.  Input as comma separated (ETF1,ETF2,..)
* --export {csv,json,xlsx} : Export to the selected file

Compares the overview of different ETFs.

Example:

```text
(✨) (etf)> compare spy,qqq,voo,doge
DOGE not found
╒════════════════╤══════════╤══════════╤══════════╕
│                │ SPY      │ QQQ      │ VOO      │
╞════════════════╪══════════╪══════════╪══════════╡
│ Last Price     │ $414.94  │ $327.01  │ $381.47  │
├────────────────┼──────────┼──────────┼──────────┤
│ Assets         │ $353.25B │ $157.51B │ $222.38B │
├────────────────┼──────────┼──────────┼──────────┤
│ NAV            │ $415.21  │ $328.91  │ $381.70  │
├────────────────┼──────────┼──────────┼──────────┤
│ Expense Ratio  │ 0.09%    │ 0.20%    │ 0.03%    │
├────────────────┼──────────┼──────────┼──────────┤
│ PE Ratio       │ 25.16    │ 35.32    │ 27.60    │
├────────────────┼──────────┼──────────┼──────────┤
│ Beta (5Y)      │ 0.99     │ 1.04     │ 0.99     │
├────────────────┼──────────┼──────────┼──────────┤
│ Dividend (ttm) │ $5.56    │ $1.77    │ $5.39    │
├────────────────┼──────────┼──────────┼──────────┤
│ Dividend Yield │ 1.34%    │ 0.54%    │ 1.41%    │
╘════════════════╧══════════╧══════════╧══════════╛
```

## screener <a name="screener"></a>

````python
usage: screener  [-n --num] [--export {csv,json,xlsx}] [-h]
````

* -n/--num : Number of etfs to display in console. Defaults to 20
* --export {csv,json,xlsx} : Export to the selected file

Screen ETFs based on the overview data from stockanalysis.com.  This data is scraped hourly during market hours.
Repo can be found at <https://github.com/jmaslek/etf_scraper>. For screeners with many results (exceeding the `--num` flag)
, the console will display a random subset of them.

Note that to use the config file, locate the desired data column then change MIN and MAX.  Make sure unused columns are
set to None. Example which will screen for ETFs the Opened between $45 and $57 (note the available data is Open and
Previous Close):

```python
[OPEN]
MIN = 45
MAX = 57
```

```python
╒══════╤══════════╤════════╤═══════════╤═══════╤═════════════╤═══════╤════════════╤════════════╤════════╤═════════════╤═════════╤══════════╤════════╤══════════╕
│      │ Assets   │ NAV    │ Expense   │ PE    │ SharesOut   │ Div   │ DivYield   │ Volume     │ Open   │ PrevClose   │ YrLow   │ YrHigh   │ Beta   │ N_Hold   │
╞══════╪══════════╪════════╪═══════════╪═══════╪═════════════╪═══════╪════════════╪════════════╪════════╪═════════════╪═════════╪══════════╪════════╪══════════╡
│ IGM  │ 3700.0   │ 416.0  │ 0.46      │ 44.78 │ 8.9         │ 0.78  │ 0.19       │ 22094.0    │ 417.6  │ 418.63      │ 290.01  │ 421.34   │ 1.08   │ 336.0    │
├──────┼──────────┼────────┼───────────┼───────┼─────────────┼───────┼────────────┼────────────┼────────┼─────────────┼─────────┼──────────┼────────┼──────────┤
│ IGV  │ 5060.0   │ 408.22 │ 0.46      │ 50.19 │ 12.4        │       │            │ 713902.0   │ 408.22 │ 411.47      │ 285.69  │ 411.75   │ 0.98   │ 126.0    │
├──────┼──────────┼────────┼───────────┼───────┼─────────────┼───────┼────────────┼────────────┼────────┼─────────────┼─────────┼──────────┼────────┼──────────┤
│ IVV  │ 295380.0 │ 441.0  │ 0.03      │ 33.44 │ 669.8       │ 5.65  │ 1.28       │ 2660313.0  │ 444.04 │ 443.65      │ 317.52  │ 444.87   │ 0.99   │ 508.0    │
├──────┼──────────┼────────┼───────────┼───────┼─────────────┼───────┼────────────┼────────────┼────────┼─────────────┼─────────┼──────────┼────────┼──────────┤
│ MDY  │ 21010.0  │ 488.64 │ 0.23      │ 17.71 │ 42.99       │ 4.63  │ 0.95       │ 564149.0   │ 495.62 │ 493.13      │ 319.23  │ 506.29   │ 1.19   │ 401.0    │
├──────┼──────────┼────────┼───────────┼───────┼─────────────┼───────┼────────────┼────────────┼────────┼─────────────┼─────────┼──────────┼────────┼──────────┤
│ SOXX │ 7540.0   │ 468.39 │ 0.46      │ 36.98 │ 16.1        │ 3.08  │ 0.66       │ 410960.0   │ 465.25 │ 468.1       │ 284.72  │ 471.38   │ 1.18   │ 34.0     │
├──────┼──────────┼────────┼───────────┼───────┼─────────────┼───────┼────────────┼────────────┼────────┼─────────────┼─────────┼──────────┼────────┼──────────┤
│ SPY  │ 382830.0 │ 439.08 │ 0.09      │ 22.2  │ 871.88      │ 5.57  │ 1.27       │ 46930008.0 │ 442.15 │ 441.76      │ 316.37  │ 442.94   │ 0.99   │ 507.0    │
├──────┼──────────┼────────┼───────────┼───────┼─────────────┼───────┼────────────┼────────────┼────────┼─────────────┼─────────┼──────────┼────────┼──────────┤
│ VGT  │ 49530.0  │ 414.64 │ 0.1       │ 35.6  │ 119.45      │ 2.61  │ 0.63       │ 233043.0   │ 415.72 │ 417.13      │ 289.64  │ 417.32   │ 1.07   │ 358.0    │
├──────┼──────────┼────────┼───────────┼───────┼─────────────┼───────┼────────────┼────────────┼────────┼─────────────┼─────────┼──────────┼────────┼──────────┤
│ VOO  │ 244900.0 │ 403.65 │ 0.03      │ 26.9  │ 606.7       │ 5.29  │ 1.31       │ 2486923.0  │ 406.48 │ 406.16      │ 290.58  │ 407.18   │ 0.99   │ 508.0    │
╘══════╧══════════╧════════╧═══════════╧═══════╧═════════════╧═══════╧════════════╧════════════╧════════╧═════════════╧═════════╧══════════╧════════╧══════════╛

```

```text
# WSJ <a name="wsj"></a>
The following functions take the information from the [WSJ Market Data Page](https://www.wsj.com/market-data)

## gainers <a name="gainers"></a>

```python
usage: gainers [-n NUM] [--export {csv,json,xlsx}] [-h]
```

Shows top gaining ETFs

* -n/--num: Number to show.  Defaults to 25, which is the max provided
* --export: Export data to one of {csv, json, xlsx}.

## decliners <a name="decliners"></a>

```python
usage: decliners [-n NUM] [--export {csv,json,xlsx}] [-h]
```

Shows highest declining ETFs

* -n/--num: Number to show.  Defaults to 25, which is the max provided
* --export: Export data to one of {csv, json, xlsx}.

## active <a name="active"></a>

```python
usage: active [-n NUM] [--export {csv,json,xlsx}] [-h]
```

Shows most active ETFs

* -n/--num: Number to show.  Defaults to 25, which is the max provided
* --export: Export data to one of {csv, json, xlsx}.
