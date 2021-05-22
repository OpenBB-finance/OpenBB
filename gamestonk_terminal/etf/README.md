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

Campares the overview of different ETFs.  Unknown tickers show nan

Example:

```
(✨) (etf)> compare spy,qqq,voo,DOGE
DOGE not found
╒════════════════╤══════════╤══════════╤══════════╤════════╕
│                │ SPY      │ QQQ      │ VOO      │   DOGE │
╞════════════════╪══════════╪══════════╪══════════╪════════╡
│ Last Price     │ $414.94  │ $327.01  │ $381.47  │    nan │
├────────────────┼──────────┼──────────┼──────────┼────────┤
│ Assets         │ $352.93B │ $153.76B │ $219.80B │    nan │
├────────────────┼──────────┼──────────┼──────────┼────────┤
│ NAV            │ $410.85  │ $322.66  │ $377.68  │    nan │
├────────────────┼──────────┼──────────┼──────────┼────────┤
│ Expense Ratio  │ 0.09%    │ 0.20%    │ 0.03%    │    nan │
├────────────────┼──────────┼──────────┼──────────┼────────┤
│ PE Ratio       │ 25.16    │ 35.32    │ 27.60    │    nan │
├────────────────┼──────────┼──────────┼──────────┼────────┤
│ Beta (5Y)      │ 0.99     │ 1.04     │ 0.99     │    nan │
├────────────────┼──────────┼──────────┼──────────┼────────┤
│ Dividend (ttm) │ $5.56    │ $1.77    │ $5.39    │    nan │
├────────────────┼──────────┼──────────┼──────────┼────────┤
│ Dividend Yield │ 1.35%    │ 0.55%    │ 1.43%    │    nan │
╘════════════════╧══════════╧══════════╧══════════╧════════╛
```
