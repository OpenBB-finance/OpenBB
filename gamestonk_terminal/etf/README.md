# ETF
Menu for Exchange Traded Funds.

Data is currently scraped from StockAnalysis.com/etf

* [web](#web)
  * open webbroswer to stockanalysis.com
* [search](#search)
  * search for ETFs matching an input
* [overview](#overview)
  *  get ETF overview
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
Opens StockAnalysis.com/etf.  This site shows all avalaiable ETFs (currently > 2800).

## search <a name="search"></a>
```python
usage: search [-n --name]
```
Search for ETFs matching
* -n/--name : Name to search for.  Can be a company or other search term

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
usage: overview [-n --name]
```
* -n/--name : ETF to get data for

Returns the overview of the ETF.  Shows Last Price, Assets, Net Asset Value (NAV), Expense Ratio, PE Ratio, 5Year Beta, Total Dividend and Dividend Yield.

Example will be a single column from the [compare](#compare) example.

## holdings <a name="holdings"></a>
```python
usage: overview [-n --name] [-l --limit]
```
* -n/--name : Name of ETF to get data for.
* -l/--limit : Number of assets to show.  Max 200.  Defaults to 20.

Returns the top holdings in the ETF.  Shows percentage and total shares held.

Example:
```
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
usage: compare [-n --names]
```
* -n/--names : ETFs to compare.  Input as comma separated (ETF1,ETF2,..)

Campares the overview of different ETFs.

Example:

```
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
usage: screener [--config] [-p MIN_PRICE] [-P MAX_PRICE] [-a MIN_ASSETS] [-A MAX_ASSETS] [-n MIN_NAV] [-N MAX_NAV] [-e MIN_EXP] [-E MAX_EXP] [-r MIN_PE] [-R MAX_PE] [-d MIN_DIV]
              [-D MAX_DIV] [-b MIN_BETA] [-B MAX_BETA] [--num] [--export {csv,json,xlsx}] [-h]
````

* --config : Flag to load from etf_config.ini file.  This supersedes any other arguments.
* -p/--min_price : Minimum ETF price
* -P/--max_price : Maximum ETF price
* -a/--min_assets : Minimum ETF assets held
* -A/--max_assets : Maximum ETF assets held
* -n/--min_nav : Minimum ETF net asset valuation
* -N/--max_nav : Maximum ETF net asset valuation
* -e/--min_exp : Minimum ETF expense ratio
* -E/--max_exp : Maximum ETF expense ratio
* -r/--min_pe : Minimum ETF PE Ratio
* -R/--max_pe : Maximum ETF PE Ratio
* -d/--min_div : Minimum ETF dividend yield
* -D/--max_div : Maximum ETF dividend yield
* -b/--min_beta : Minimum ETF 5Y beta
* -B/--max_beta : Maximum ETF 5Y beta
* --num : Number of etfs to display in console. Defaults to 20
* --export {csv,json,xlsx} : Export to the selected file

Screen ETFs based on the overview data from stockanalysis.com.  This data is scraped nightly at midnight EST, so it will not be up to date or change during the day.  Repo can be found at https://github.com/jmaslek/etf_scraper.
For screeners with many results (exceeding the `--num` flag), the console will display a random subset of them.

Note that to use the config file, locate the desired data column then change MIN and MAX.  Make sure unused columns are set to None.
Example which will screen for ETFs between $45 and $57:
```python
[Price]
MIN = 45
MAX = 57
```

Sample usage:
```python
(✨) (etf)> screener -p 45 -P 88 -E 1 -d 3 -r 12 -a 10000
ETFs downloaded

╒═════╤═════════╤══════════╤═══════╤═══════════╤═══════╤════════╤═══════╤════════════╕
│     │   Price │   Assets │   NAV │   Expense │    PE │   Beta │   Div │   DivYield │
╞═════╪═════════╪══════════╪═══════╪═══════════╪═══════╪════════╪═══════╪════════════╡
│ VGK │   66.97 │    19750 │ 67.38 │      0.08 │ 20.7  │   0.94 │  2.07 │       3.07 │
├─────┼─────────┼──────────┼───────┼───────────┼───────┼────────┼───────┼────────────┤
│ XLE │   51.75 │    24950 │ 52.92 │      0.12 │ 20    │   1.75 │  2.11 │       3.99 │
├─────┼─────────┼──────────┼───────┼───────────┼───────┼────────┼───────┼────────────┤
│ XLU │   64.52 │    11640 │ 64.31 │      0.12 │ 19.94 │   0.35 │  1.98 │       3.07 │
╘═════╧═════════╧══════════╧═══════╧═══════════╧═══════╧════════╧═══════╧════════════╛
```
# WSJ <a name="wsj"></a>
The following functions atake the information from the [WSJ Market Data Page](https://www.wsj.com/market-data)

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
