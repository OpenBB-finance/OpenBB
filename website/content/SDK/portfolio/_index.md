---
title: Introduction to Portfolio
keywords: "portfolio, attribution, optimization, pnl, benchmark, return, volatility, metrics, broker, integration, report"
excerpt: "The Introduction to Portfolio explains how to use the
menu and provides a brief description of its sub-menus"
geekdocCollapseSection: true
---

The capabilities of the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/portfolio/" target="_blank">Portfolio menu</a> from the OpenBB Terminal are wrapped into a powerful SDK, enabling users to work with the data in a flexible environment that can be fully customized to meet the needs of any user. This menu is dedicated to properly explaining and optimizing your own portfolio with features to load your own orderbook (transactions) it is possible to compare your results to that of a <a href="https://www.investopedia.com/terms/b/benchmark.asp" target="_blank">benchmark</a>. For example, you are able to load both your portfolio and a benchmark, then have the option to look into the performance compared to the benchmark asking the question "_What if I invested all my money in the benchmark instead?_" as well as see a wide variety of statistics and metrics. Next to that, with these findings you can apply optimization techniques to your portfolio through functionalities regarding <a href="https://openbb-finance.github.io/OpenBBTerminal/sdk/portfolio/po/" target="_blank">Portfolio Optimization</a>.

## How to use

Start a Python script or Notebook file by importing the module:

```python
from openbb_terminal.sdk import openbb
```

The contents of the menu is printed by running a cell with `openbb.portfolio` which
returns the following:

```
PORTFOLIO Menu

The SDK commands of the the menu:
	<openbb>.portfolio.holdv
	<openbb>.portfolio.holdp
	<openbb>.portfolio.yret
	<openbb>.portfolio.mret
	<openbb>.portfolio.dret
	<openbb>.portfolio.max_drawdown_ratio
	<openbb>.portfolio.distr
	<openbb>.portfolio.maxdd
	<openbb>.portfolio.rvol
	<openbb>.portfolio.rsharpe
	<openbb>.portfolio.rsort
	<openbb>.portfolio.rbeta
	<openbb>.portfolio.summary
	<openbb>.portfolio.skew
	<openbb>.portfolio.kurtosis
	<openbb>.portfolio.volatility
	<openbb>.portfolio.sharpe
<continues>
```

The first step in using this menu is loading a portfolio. Here, we provide an example titled "Public_Equity_Orderbook.xlsx" which can be loaded in. This file also serves as a template when you wish to fill in your own orders. This results
in the following:

```python
from openbb_terminal.sdk import Portfolio

# Define your own orderbook location here
orderbook_path = "Public_Equity_Orderbook.xlsx"

# Load in the transactions
transactions = Portfolio.read_orderbook(orderbook_path)
P = Portfolio(transactions)
P.generate_portfolio_data()

# Load in the benchmark, by default this is the SPY ETF
P.set_benchmark()
```

Note that the Excel sheet requires the following columns:
- **Date** - The date the trade occurred
- **Name** - The name of the security
- **Type** - The type of the security. Use Cash/Stock/Crypto/ETF as appropriate
- **Price** - The price the security was added or removed at, on a per-unit basis
- **Quantity** - How much of the security in question was added or removed
- **Side** - Whether you bought or sold. Use Buy/Deposit/1 to add to the portfolio or Sell/Withdrawal/0 to remove from the portfolio
a search criteria, country, sector or industry.

Furthermore, the chosen Excel sheet above also has additional columns but these are _optional_. The OpenBB Terminal
can figure out by itself what industry, sector, country and region belongs to the loaded in equity. You can see this in
action by loading in the "Public_Equity_Orderbook_No_Categorization.xlsx" Excel sheet.

With the `get_orderbook` on the `Portfolio` class command we can show how the data has been loaded in:

````python
P.get_orderbook()
````

This returns the following (a portion of the data):

|    | Date       | Type   | Ticker   | Side   |   Price |   Quantity |   Fees |   Investment | Currency   | Sector            | Industry               | Country       | Region        |
|---:|:-----------|:-------|:---------|:-------|--------:|-----------:|-------:|-------------:|:-----------|:------------------|:-----------------------|:--------------|:--------------|
| 38 | 2022-05-02 | STOCK  | YUM      | Buy    |  115.76 |         11 |     40 |      1313.36 | USD        | Consumer Cyclical | Restaurants            | United States | North America |
| 37 | 2022-04-12 | STOCK  | DGX      | Buy    |  137.27 |         10 |     30 |      1402.7  | USD        | Healthcare        | Diagnostics & Research | United States | North America |
| 36 | 2022-03-04 | STOCK  | TSM      | Buy    |  105.06 |         30 |      0 |      3151.8  | USD        | Technology        | Semiconductors         | Taiwan        | Asia          |
| 35 | 2022-02-02 | STOCK  | BABA     | Buy    |  122.88 |         30 |      0 |      3686.4  | USD        | Consumer Cyclical | Internet Retail        | China         | Asia          |
| 34 | 2021-12-28 | STOCK  | NKE      | Buy    |  166.42 |         13 |     20 |      2183.46 | USD        | Consumer Cyclical | Footwear & Accessories | Germany       | Europe        |

With the portfolio and benchmark loaded in, we can see how the portfolio performed compared to if you invested the same amount of money into the
benchmark instead. This reflects the capabilities of you, as an investor, to outperform a passive strategy.

```python
openbb.portfolio.perf(P)
```

|                  | Portfolio          | Benchmark          | Difference         |
|:-----------------|:-------------------|:-------------------|:-------------------|
| Total Investment | 48693.95           | 48693.95           | -                  |
| Total Value      | 54591.70 | 60379.68 | -5787.97 |
| Total % Return   | 12.11%             | 24.00%             | -11.89%            |
| Total Abs Return | 5897.75  | 11685.73 | -5787.97 |

Compliment this by showing the volatility of the portfolio for different time periods with the volatility measure.

```python
openbb.portfolio.volatility(P)
```

|     |   Portfolio [%] |   Benchmark [%] |
|:----|----------------:|----------------:|
| mtd |           7.024 |           3.589 |
| qtd |          13.515 |           8.823 |
| ytd |          34.853 |          22.489 |
| 3m  |          18.119 |          12.562 |
| 6m  |          26.216 |          17.64  |
| 1y  |          36.341 |          23.303 |
| 3y  |          54.114 |          42.435 |
| 5y  |          62.103 |          47.383 |
| 10y |          72.617 |          54.408 |
| all |          91.162 |          62.297 |

## Examples

Instead of loading the "Public_Equity_Orderbook.xlsx" file, we now load in
"Public_Equity_Orderbook_No_Categorization.xlsx" which does not include categorization of the stocks
by industry, sector, country and region. Therefore, we let the OpenBB Terminal figure this out. This
takes a bit longer to load.

```python
from openbb_terminal.sdk import Portfolio

# Define your own orderbook location here
orderbook_path = "Public_Equity_Orderbook_No_Categorization.xlsx"

# Load in the transactions
transactions = Portfolio.read_orderbook(orderbook_path)
P = Portfolio(transactions)
P.generate_portfolio_data()

# Load in the benchmark, by default this is the SPY ETF
P.set_benchmark()
```

Then, we can show our performance compared to that of the benchmark.

```python
openbb.portfolio.perf(P)
```

|                  | Portfolio         | Benchmark          | Difference         |
|:-----------------|:------------------|:-------------------|:-------------------|
| Total Investment | 48693.95          | 48693.95           | -                  |
| Total Value      | 54795.03 | 60472.14 | -5677.11|
| Total % Return   | 12.53%            | 24.19%             | -11.66%            |
| Total Abs Return | 6101.08| 11778.19| -5677.11 |


Furthermore, we can also show the rolling beta.
```python
openbb.portfolio.rbeta(P, chart=True)
```

![Rolling Beta of the Portfolio](https://user-images.githubusercontent.com/46355364/180178392-96efb6e1-60a1-4f76-92d8-434fb3637c21.png)

This helps in understanding that, even though you achieved a superior return, this also came at a greater risk compared to that of the benchmark. With the available functionalities you can further look into these results, e.g. by looking at the sharpe ratio:

```python
openbb.portfolio.sharpe(P)
```

|     |   Portfolio |   Benchmark |
|:----|------------:|------------:|
| mtd |       0.193 |      -0.207 |
| qtd |       0.144 |       0.132 |
| ytd |      -0.077 |      -0.058 |
| 3m  |      -0.069 |      -0.071 |
| 6m  |      -0.013 |      -0.013 |
| 1y  |      -0.073 |      -0.046 |
| 3y  |       0.021 |       0.029 |
| 5y  |       0.026 |       0.035 |
| 10y |       0.044 |       0.049 |
| all |       0.03  |       0.045 |
