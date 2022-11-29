---
title: Portfolio
---

The [Portfolio menu](/terminal/guides/intros/portfolio), from the OpenBB Terminal, is wrapped into a Python SDK layer, enabling users to programmatically work with the data in a flexible environment, fully customizable for the needs of any user. This guide will introduce the functions within the main Portfolio module, and walk through examples demonstrating how to work with a portfolio file and object.

## How to Use

Below is a brief description of each function within the Portfolio module:

| Path                       |    Type    |                                  Description |
| :------------------------- | :--------: | -------------------------------------------: |
| openbb.portfolio.alloc         |  Sub-Module  |      Allocation Metrics Compared to the Benchmark |
| openbb.portfolio.bench         | Function |                 Select a Benchmark for the Portfolio |
| openbb.portfolio.distr              |  Function  | Distribution of Daily Returns |
| openbb.portfolio.dret |  Function  |                            Daily Returns |
| openbb.portfolio.es        |  Function  |                 Expected Shortfall |
| openbb.portfolio.holdp     |  Function  |                   Holdings of Assets as a % |
| openbb.portfolio.holdv         |  Function  |      Holdings of Assets as an Absolute Value |
| openbb.portfolio.load         |  Function  |      Load a Portfolio File |
| openbb.portfolio.maxdd         |  Function  |      Maximum Drawdown |
| openbb.portfolio.metric         |  Sub-Module  |      Risk and Portfolio Metrics |
| openbb.portfolio.mret         |  Function  |      Monthly Returns |
| openbb.portfolio.om            |  Function  |                  Omega Ratio |
| openbb.portfolio.perf             | Function |         Portfolio Performance vs Benchmark |
| openbb.portfolio.po            | Sub-Module |         Portfolio Optimization Sub Menu |
| openbb.portfolio.rbeta              |  Function  |   Rolling Beta of Portfolio and Benchmark Returns |
| openbb.portfolio.rsharpe            |  Function  |         Rolling Sharpe Ratio |
| openbb.portfolio.rsort         |  Function  |       Rolling Sortino Ratio |
| openbb.portfolio.rvol         |  Function  |      Rolling Volatility |
| openbb.portfolio.show         |  Function  |      Portfolio Transactions |
| openbb.portfolio.summary          |  Function  |   Summary of Portfolio and Benchmark Returns |
| openbb.portfolio.var         |  Function  |      Portfolio VaR |
| openbb.portfolio.yret        |  Function  |            Yearly Returns |

Alteratively, the contents of the Porfolio module is printed with:

```python
help(openbb.portfolio)
```

Many of the functions in this module will also have a companion command, `_chart`.

### Portfolio Files

Portfolio files are spreadsheets (xlsx or csv files) containing historical trades which add up to represent a net balance in the Portfolio Engine. Users should keep their collection of holdings files in the OpenBBUserData folder, `~/OpenBBUserData/portfolio/holdings`. They are shared resources with the CLI Terminal, and sample files are included within the installation folder. See the [source code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/miscellaneous/portfolio_examples/holdings) on GitHub to view and download them directly. We recommend using the example files as a template when creating a new portfolio because of specific formatting requirements. The table below illustrates the required column titles:

| Date       | Type   | Ticker   | Side   |   Price |   Quantity |   Fees |   Investment | Currency   | Sector                 | Industry                       | Country       | Region        |
|:-----------|:-------|:---------|:-------|--------:|-----------:|-------:|-------------:|:-----------|:-----------------------|:-------------------------------|:--------------|:--------------|
| 2021-10-29 | STOCK  | K.TO     | Buy    |    7.93 |      190   |     20 |     1526.7   | CAD        | Basic Materials        | Gold                           | Canada        | North America |
| 2015-01-02 | ETF    | SPY      | Buy    |  178.28 |        5.6 |      0 |      998.368 | USD        | -                      | -                              | -             | -             |
| 2015-01-01 | CRYPTO | BTC-USD  | Buy    | 1000    |          2 |      0 |         2000 | USD        | Crypto                 | Crypto                         | Crypto        | Crypto        |
| 2011-01-03 | STOCK  | AMZN     | Buy    |    9.22 |        100 |      0 |          922 | USD        | Consumer Cyclical      | Internet Retail                | United States | North America |
| 2011-01-03 | STOCK  | AAPL     | Buy    |   11.74 |        100 |      0 |         1174 | USD        | Technology             | Consumer Electronics           | United States | North America |
| 2011-01-03 | STOCK  | MSFT     | Buy    |   28.04 |        100 |      0 |         2804 | USD        | Technology             | Software-Infrastructure        | United States | North America |
| 2011-01-03 | STOCK  | TSLA     | Buy    |    1.76 |        100 |      0 |          176 | USD        | Consumer Cyclical      | Auto Manufacturers             | United States | North America |
| 2011-01-03 | STOCK  | GOOG     | Buy    |   15.01 |        100 |      0 |         1501 | USD        | Communication Services | Internet Content & Information | United States | North America |

Not every column needs to contain a value, but they must exist despite being empty. The accepted values for `Type` are currently:

- Crypto
- ETF
- Stock
- More Coming Soon!

The table above is supplied here as a portfolio XLSX file - [example.xlsx](https://github.com/OpenBB-finance/OpenBBTerminal/files/10096861/example.xlsx) - save the file in the OpenBBUserData folder, `~/OpenBBUserData/portfolio/holdings/`

Categorization will be done automatically where the information is not supplied. To manually set the asset categorization (region, sector, industry, country), use the template file, `Public_Equity_Orderbook.xlsx`.

## Examples

The examples in this guide will assume that the import statements below are included at the top of the Python script or Jupyter Notebook.

### Import Statements

```python
from openbb_terminal.sdk import openbb
import pandas as pd
# %matplotlib inline (uncomment if using a Jupyter Notebook or an Interactive Window)
```

### Load

Taking the downloaded `example.xlsx` file from the previous section, let's load it into the Portfolio Engine. There are a few parameters available for this function, and an object is returned.

```python
help(openbb.portfolio.load)
```

```console
    Get PortfolioEngine object

    Parameters
    ----------
    transactions_file_path : str
        Path to transactions file
    benchmark_symbol : str
        Benchmark ticker to download data
    full_shares : bool
        Whether to mimic the portfolio trades exactly (partial shares) or round down the
        quantity to the nearest number
    risk_free_rate : float
        Risk free rate in float format

    Returns
    -------
    PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio_examples/holdings/example.csv")
```

The syntax should resemble something like the sample below; don't forget to modify the path to match the local path.

```python
P = openbb.portfolio.load(
  transactions_file_path = '/Users/path_to/OpenBBUserData/portfolio/holdings/example.xlsx',
  benchmark_symbol = 'VTI',
  full_shares = False,
  risk_free_rate = 3.0
)
```

```console
Preprocessing transactions: 100%|██████████| 14/14 [00:01<00:00,  8.82it/s]
        Loading price data: 100%|██████████| 3/3 [00:01<00:00,  2.64it/s]
       Calculating returns: 100%|██████████| 1/1 [00:00<00:00, 14.52it/s]
         Loading benchmark: 100%|██████████| 4/4 [00:04<00:00,  1.21s/it]
```

### The Portfolio Object

A Portfolio Object is assigned to the variable, `P`. The created object, or parts of it, are used as inputs to the other functions in this module. It can also be interacted with directly, for example, to change the benchmark ticker. `SPY` is a holding in the example portfolio, so let's stick with `VTI` as the performance benchmark.

```python
P.set_benchmark(symbol = 'SPY')

 Loading benchmark:  50%|█████     | 2/4 [00:00<00:00,  5.69it/s]

print(P.benchmark_ticker)

SPY
```

Populating a list of tickers from the Portfolio Object is accomplished by assigning a variable to it:

```python
tickers = P.tickers_list
print(tickers)

['SPY', 'TSLA', 'K.TO', 'AAPL', 'AMZN', 'MSFT', 'BTC-USD', 'GOOG']
```

### Show

`openbb.portfolio.show` is for displaying the transactions from the loaded portfolio file. Scroll back up to view the output of this function again.

```python
openbb.portfolio.show(P)
```

### Perf

Performance against the benchmark is summarized in a table with, `openbb.portfolio.perf`.

```python
print(openbb.portfolio.perf(P))
```

|                  | Portfolio          | Benchmark          | Difference        |
|:-----------------|:-------------------|:-------------------|:------------------|
| Total Investment | 11102.07          | 11102.07          | -                 |
| Total Value      | 114027.38 | 36203.96  | 77823.43 |
| Total % Return   | 927.08%            | 226.10%            | 700.98%           |
| Total Abs Return | 102925.31 | 25101.89 | 77823.43 |

### Summary

`openbb.portfolio.summary` prints a table of risk metrics, comparing the portfolio against the benchmark.

```python
print(openbb.portfolio.summary(P))
```

|                  | Portfolio            | Benchmark           | Difference           |
|:-----------------|:---------------------|:--------------------|:---------------------|
| Volatility       | 1.65%                | 0.99%               | 0.66%                |
| Skew             | -0.32 | -0.61 | 0.29  |
| Kurtosis         | 8.80   | 16.87  | -8.079   |
| Maximum Drawdown | -59.05%              | -35.00%             | -24.05%              |
| Sharpe ratio     | 0.05 | 0.039 | 0.011 |
| Sortino ratio    | 0.06 | 0.04 | 0.021 |
| R2 Score         | 41.36%               | 41.36%              | 0.00%                |

### MaxDD

`openbb.portfolio.maxdd` calculates the maximum drawdown as price and % value; it returns a Tuple.

```python
holdings,dd = openbb.portfolio.maxdd(P)
dd = pd.DataFrame(dd)
dd.rename(columns = {'Total': 'Portfolio % Drawdown'}, inplace = True)
holdings = pd.DataFrame(holdings)
holdings.rename(columns = {'Total': 'Portfolio Value'}, inplace = True)
dd = dd.join(holdings)
dd.index = dd.index.strftime(date_format='%Y-%m-%d')
print(dd.tail(5))
```

| Date       |  Portfolio % Drawdown | Portfolio Value |
|:-----------|-------------:|-----------:|
| 2022-11-21 |    -0.58 |     109442 |
| 2022-11-22 |    -0.57 |     111257 |
| 2022-11-23 |    -0.56 |     114017 |
| 2022-11-24 |    -0.56 |     114027 |
| 2022-11-25 |    -0.56 |     113302 |

MaxDD also has a `_chart` command, and is called with:

```python
openbb.portfolio.maxdd_chart(P)
```

![openbb.portfolio.maxdd_chart](https://user-images.githubusercontent.com/85772166/204072456-f6b8e038-08ef-4ac5-9920-14a9c1e4197f.png "openbb.portfolio.maxdd_chart")

### RSharpe

Calculate a rolling sharpe ratio over a specified window.

```python
rs = openbb.portfolio.rsharpe(P, window = '3m')
rs.rename(columns = {'portfolio': 'Portfolio Sharpe', 'benchmark': 'Benchmark Sharpe'}, inplace = True)
rs.index = rs.index.strftime(date_format='%Y-%m-%d')
print(rs.tail(5))
```

| Date       |   Portfolio Sharpe |   Benchmark Sharpe |
|:-----------|-------------------:|-------------------:|
| 2022-11-21 |         -0.15  |          0.02 |
| 2022-11-22 |         -0.13  |          0.05 |
| 2022-11-23 |         -0.09 |          0.07  |
| 2022-11-24 |         -0.09 |          0.08 |
| 2022-11-25 |         -0.09 |          0.11  |

### RVol

`openbb.portfolio.rvol` has the same input parameters as `rsharpe`.

```python
rv = openbb.portfolio.rvol(P, window = '3m')
rv.rename(columns={'portfolio': 'Portfolio Volatility', 'benchmark': 'Benchmark Volatility'}, inplace = True)
rv.index = rv.index.strftime(date_format='%Y-%m-%d')

print(rv.tail(5))
```

| Date       |   Portfolio Volatility |   Benchmark Volatility |
|:-----------|-----------------------:|---------------------:|
|2022-11-23   |           0.021727     |         0.014490|
|2022-11-24    |          0.021715     |         0.014439|
|2022-11-25   |           0.021596    |          0.014256|
|2022-11-26   |           0.021591    |          0.014256|
|2022-11-27   |           0.021592    |          0.014256|

### DRet

`openbb.portfolio.dret` returns a DataFrame with daily returns of the portfolio and benchmark.

```python
returns = openbb.portfolio.dret(P)
returns.rename(columns = {'portfolio': 'Portfolio % Returns', 'benchmark': 'Benchmark % Returns'}, inplace = True)
returns.index = returns.index.rename('Date')

print(returns.tail(5))
```

| Date       |   Portfolio % Returns |   Benchmark % Returns |
|:-----------|----------------------:|----------------------:|
| 2022-11-21 |          -0.03  |          -0.00 |
| 2022-11-22 |           0.02  |           0.01 |
| 2022-11-23 |           0.02  |           0.01 |
| 2022-11-24 |           0.00  |           0.00 |
| 2022-11-25 |          -0.01  |           0.00 |

Read the [Portfolio Optimization Intro](https://docs.openbb.co/sdk/guides/intros/portfolio/po) to learn about the optimization features, and the parameters preset template.
