---
title: Portfolio
---

The [Portfolio menu](/terminal/guides/portfolio), from the OpenBB Terminal, is wrapped into a Python SDK layer, enabling users to programmatically work with the data in a flexible environment, fully customizable for the needs of any user. This guide will introduce the functions within the main Portfolio module, and walk through examples demonstrating how to work with a portfolio file and object.

## **How to Use**

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

### **Portfolio Files**

Portfolio files are spreadsheets (xlsx or csv files) containing positions and trades. Users should keep their collection of holdings files in the OpenBBUserData folder, `~/OpenBBUserData/portfolio/holdings`. They are shared resources with the CLI Terminal, and sample files are included within the installation folder. See the [source code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/miscellaneous/portfolio_examples/holdings) on GitHub to view and download them directly. We recommend using the example files as a template when creating a new portfolio because of specific formatting requirements. The table below illustrates the required column titles:

|    | Date       | Type   | Ticker   | Side   |   Price |   Quantity |   Fees |   Investment | Currency   | Sector                 | Industry                       | Country       | Region        |
|---:|:-----------|:-------|:---------|:-------|--------:|-----------:|-------:|-------------:|:-----------|:-----------------------|:-------------------------------|:--------------|:--------------|
|  7 | 2021-10-29 | STOCK  | K.TO     | Buy    |    7.93 |      190   |     20 |     1526.7   | CAD        | Basic Materials        | Gold                           | Canada        | North America |
|  6 | 2015-01-02 | ETF    | SPY      | Buy    |  178.28 |        5.6 |      0 |      998.368 | USD        | -                      | -                              | -             | -             |
|  5 | 2015-01-01 | CRYPTO | BTC-USD  | Buy    | 1000    |          2 |      0 |         2000 | USD        | Crypto                 | Crypto                         | Crypto        | Crypto        |
|  0 | 2011-01-03 | STOCK  | AMZN     | Buy    |    9.22 |        100 |      0 |          922 | USD        | Consumer Cyclical      | Internet Retail                | United States | North America |
|  1 | 2011-01-03 | STOCK  | AAPL     | Buy    |   11.74 |        100 |      0 |         1174 | USD        | Technology             | Consumer Electronics           | United States | North America |
|  2 | 2011-01-03 | STOCK  | MSFT     | Buy    |   28.04 |        100 |      0 |         2804 | USD        | Technology             | Software-Infrastructure        | United States | North America |
|  3 | 2011-01-03 | STOCK  | TSLA     | Buy    |    1.76 |        100 |      0 |          176 | USD        | Consumer Cyclical      | Auto Manufacturers             | United States | North America |
|  4 | 2011-01-03 | STOCK  | GOOG     | Buy    |   15.01 |        100 |      0 |         1501 | USD        | Communication Services | Internet Content & Information | United States | North America |

Not every column needs to contain a value, but they must exist despite being empty. The accepted values for `Type` are currently:

- Crypto
- ETF
- Stock
- More Coming Soon!

Below is the contents of the `csv` file that was used in the table above.

```csv
Date,Ticker,Type,Sector,Industry,Country,Price,Quantity,Fees,Premium,Investment,Side,Currency,Region
2011-01-03,AMZN,Stock,,,,9.22,100,0,0,922,Buy,USD,
2011-01-03,AAPL,Stock,,,,11.74,100,0,0,1174,Buy,USD,
2011-01-03,MSFT,Stock,,,,28.04,100,0,0,2804,Buy,USD,
2011-01-03,TSLA,Stock,,,,1.76,100,0,0,176,Buy,USD,
2011-01-03,GOOG,Stock,,,,15.01,100,0,0,1501,Buy,USD,
2015-01-01,BTC,CRYPTO,,,,1000.00,2,0,0,2000,Buy,USD,
2015-01-02,SPY,ETF,,,,178.28,5.6,0,0,1000,Buy,USD,
2021-10-29,K.TO,Stock,,,,7.93,190,20,0,1526.70,Buy,CAD,
```

Create a new file with any text editor, copy and paste the above block, and save the file as `~/OpenBBUserData/portfolio/holdings/example.csv`. In Mac OS, the Numbers application has a habit of altering the format of CSV files, be careful to preserve the formatting when saving. A simple text editor works very well for this particular task. If trouble persists while attempting to load a portfolio file, check the file for abnormalities.

To manually set the asset categorization (region, sector, industry, country), use the template file, `Public_Equity_Orderbook.xlsx`, instead.

## **Examples**

The examples in this guide will assume that the import statements below are included at the top of the Python script or Jupyter Notebook.

### **Import Statements**

```python
from openbb_terminal.sdk import openbb
import pandas as pd
# %matplotlib inline (uncomment if using a Jupyter Notebook or an Interactive Window)
```

### **Load**

Taking the newly created, `example.csv`, file from the previous section, let's load it into the Portfolio Engine. There are a few parameters available for this function, and an object is returned.

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
```

The syntax should resemble something like the sample below; don't forget to modify the path to match the local path.

```python
P = openbb.portfolio.load(
  transactions_file_path = '/Users/path_to/OpenBBUserData/portfolio/holdings/example.csv',
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

### **The Portfolio Object**

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

### **Show**

`openbb.portfolio.show` is for displaying the transactions from the loaded portfolio file. Scroll back up to view the output of this function again.

```python
openbb.portfolio.show(P)
```

### **Perf**

Performance against the benchmark is summarized in a table with, `openbb.portfolio.perf`.

```python
print(openbb.portfolio.perf(P))
```

|                  | Portfolio          | Benchmark          | Difference        |
|:-----------------|:-------------------|:-------------------|:------------------|
| Total Investment | 11102.068          | 11102.068          | -                 |
| Total Value      | 114027.38207511902 | 36203.95564599375  | 77823.42642912528 |
| Total % Return   | 927.08%            | 226.10%            | 700.98%           |
| Total Abs Return | 102925.31407511902 | 25101.887645993753 | 77823.42642912528 |

### **Summary**

`openbb.portfolio.summary` prints a table of risk metrics, comparing the portfolio against the benchmark.

```python
print(openbb.portfolio.summary(P))
```

|                  | Portfolio            | Benchmark           | Difference           |
|:-----------------|:---------------------|:--------------------|:---------------------|
| Volatility       | 1.65%                | 0.99%               | 0.66%                |
| Skew             | -0.31960161923253505 | -0.6065148005015982 | 0.2869131812690632   |
| Kurtosis         | 8.795677320588695    | 16.87494260151323   | -8.079265280924535   |
| Maximum Drawdown | -59.05%              | -35.00%             | -24.05%              |
| Sharpe ratio     | 0.05052486519019196  | 0.03936319466622848 | 0.011161670523963482 |
| Sortino ratio    | 0.062308795370197276 | 0.04131937917727341 | 0.020989416192923868 |
| R2 Score         | 41.36%               | 41.36%              | 0.00%                |

### **MaxDD**

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
| 2022-11-21 |    -0.576778 |     109442 |
| 2022-11-22 |    -0.569757 |     111257 |
| 2022-11-23 |    -0.559085 |     114017 |
| 2022-11-24 |    -0.559045 |     114027 |
| 2022-11-25 |    -0.56185  |     113302 |

MaxDD also has a `_chart` command, and is called with:

```python
openbb.portfolio.maxdd_chart(P)
```

![openbb.portfolio.maxdd_chart](https://user-images.githubusercontent.com/85772166/204072456-f6b8e038-08ef-4ac5-9920-14a9c1e4197f.png "openbb.portfolio.maxdd_chart")

### **RSharpe**

Calculate a rolling sharpe ratio over a specified window.

```python
rs = openbb.portfolio.rsharpe(P, window = '3m')
rs.rename(columns = {'portfolio': 'Portfolio Sharpe', 'benchmark': 'Benchmark Sharpe'}, inplace = True)
rs.index = rs.index.strftime(date_format='%Y-%m-%d')
print(rs.tail(5))
```

| Date       |   Portfolio Sharpe |   Benchmark Sharpe |
|:-----------|-------------------:|-------------------:|
| 2022-11-21 |         -0.148472  |          0.0202855 |
| 2022-11-22 |         -0.125775  |          0.0466755 |
| 2022-11-23 |         -0.0919441 |          0.072191  |
| 2022-11-24 |         -0.0949094 |          0.0847346 |
| 2022-11-25 |         -0.0851729 |          0.105643  |

### RVol

`openbb.portfolio.rvol` has the same input parameters as `rsharpe`.

```python
rv = openbb.portfolio.rvol(P, window = '3m')
rv.rename(columns={'portfolio': 'Portfolio Volatility', 'benchmark': 'Benchmark Volatility'}, inplace = True)
rv.index = rv.index.strftime(date_format='%Y-%m-%d')
rolling_metrics = dd.join(rv,rs)

print(rolling_metrics.tail(5))
```

| Date       |   Portfolio % Drawdown |   Portfolio Value |   Portfolio Volatility |   Benchmark Volatility |   Portfolio Sharpe |   Benchmark Sharpe |
|:-----------|-----------------------:|---------------------:|-----------------------:|-----------------------:|-------------------:|-------------------:|
| 2022-11-21 |              -0.576778 |               109442 |              0.0214689 |              0.0148696 |         -0.148472  |          0.0202855 |
| 2022-11-22 |              -0.569757 |               111257 |              0.0215719 |              0.0148761 |         -0.125775  |          0.0466755 |
| 2022-11-23 |              -0.559085 |               114017 |              0.021727  |              0.014715  |         -0.0919441 |          0.072191  |
| 2022-11-24 |              -0.559045 |               114027 |              0.0217148 |              0.0146321 |         -0.0949094 |          0.0847346 |
| 2022-11-25 |              -0.56185  |               113302 |              0.0215965 |              0.0144397 |         -0.0851729 |          0.105643  |

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
| 2022-11-21 |          -0.0255093   |          -0.00423343  |
| 2022-11-22 |           0.0165906   |           0.0131086   |
| 2022-11-23 |           0.0248036   |           0.00609483  |
| 2022-11-24 |           0.000090    |           0.000000    |
| 2022-11-25 |          -0.00636119  |           0.000744793 |

Read the [Portfolio Optimization Intro](https://docs.openbb.co/sdk/guides/intros/portfolio/po) to learn about the optimization features, and the parameters preset template.
