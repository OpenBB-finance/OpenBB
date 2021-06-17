# PORTFOLIO ANALYSIS

This menu aims to analyze a portfolio loaded through csv, and the usage of the following commands along with an example will be exploited below.

* [load](#load)
  * load portfolio from csv file
* [group](#group)
  * view holdings by a user input group

## load
```
usage: load [-p PATH] [--no_sector] [--no_last_price] [--nan]
```
This function allows you to load from a predefined csv file.  The csv file can contain any information you want, but the stocks should be under a column `Ticker`.  The number owned should be defined in `Shares`.  By default, this will loop through all Tickers and pull sector and latest price. An example column that could be added would be if the ticker is considered a Value or Growth stock.
* -p/--path : Path to csv.  A template is supplied and the default path points to it.
* --no_sector : Flag to avoid getting the sector of each stock.
* --no_last_price : Flag to avoid getting the latest price for each supplied stock.
* --nan : Flag to display NaN columns.  Useful if importing partial information.

```python
(✨) (pa)> load
╒════╤══════════╤══════════╤════════════════════╤══════════════╤═════════╕
│    │ Ticker   │   Shares │ sector             │   last_price │   value │
╞════╪══════════╪══════════╪════════════════════╪══════════════╪═════════╡
│  0 │ AAPL     │        5 │ Technology         │       129.64 │  648.2  │
├────┼──────────┼──────────┼────────────────────┼──────────────┼─────────┤
│  1 │ GME      │        5 │ Consumer Cyclical  │       222.5  │ 1112.5  │
├────┼──────────┼──────────┼────────────────────┼──────────────┼─────────┤
│  2 │ MSFT     │        3 │ Technology         │       258.36 │  775.08 │
├────┼──────────┼──────────┼────────────────────┼──────────────┼─────────┤
│  3 │ O        │        2 │ Real Estate        │        69.61 │  139.22 │
├────┼──────────┼──────────┼────────────────────┼──────────────┼─────────┤
│  4 │ BAC      │        3 │ Financial Services │        41.39 │  124.17 │
╘════╧══════════╧══════════╧════════════════════╧══════════════╧═════════╛
```

## group
```
usage: group [-g GROUP]
```
Displays data in groups based on columns.  Currently this only looks at the `value` column.
* -g/--group : Column to group data by.  Ex: "sector"

```python
(✨) (pa)> group -g sector
╒════════════════════╤═════════╕
│ sector             │   value │
╞════════════════════╪═════════╡
│ Consumer Cyclical  │ 1112.5  │
├────────────────────┼─────────┤
│ Financial Services │  124.17 │
├────────────────────┼─────────┤
│ Real Estate        │  139.22 │
├────────────────────┼─────────┤
│ Technology         │ 1423.28 │
╘════════════════════╧═════════╛
```
