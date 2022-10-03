# OpenBB SDK

OpenBB SDK allows you to access to all OpenBB Terminal's capabilities programmatically. You will now have the building blocks to create tools and applications on top, whether that is a visualization dashboard or your own Python script.

You can get direct access to normalized financial data from multiple data providers, without having to develop your own integration from scratch. In addition, OpenBB SDK gives you a set of the toolbox to perform financial analysis on a variety of asset classes, including stocks, crypto, ETFs, funds; the economy as well as your portfolios.

## Installation

To be completed once pip install is available on PyPI

## Setup
### 1. Import OpenBB SDK

First off, import OpenBB SDK into your python script or Jupyter Notebook with:

```
from openbb_terminal.api import openbb
```


This imports all Terminal commands at once. To see all the available commands, you can press `tab` in jupyter notebook.
Another approach is to check out [OpenBB SDK Documentation](https://openbb-finance.github.io/OpenBBTerminal/api/), where you can explore its capabilities


### 2. Customize chart style
With OpenBB SDK, you can customize your chart style. You can switch between `dark` and `light` easily using this block of code:


```
from openbb_terminal.api import TerminalStyle
theme = TerminalStyle("light", "light", "light")
```

[INSERT CHART HERE]

OR

```
from openbb_terminal.api import TerminalStyle
theme = TerminalStyle("dark", "dark", "dark")
```
[INSERT CHART HERE]

### 3. Access Documentation
Each and every command of OpenBB SDK has detailed documentation about input parameters and returned outputs. You can access them using multiple ways:

**Approach 1: Press `shift + tab`**
This will work out of the box if you're using Jupyter Notebook. In case your IDE is VSCode, you will need to install the [Jupyter PowerToys
extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.vscode-jupyter-powertoys).

[INSERT SCREENSHOTs]


**Approach 2: Type `help(command)`**
You can also type `help(command)`, see example below, to see the command' docstring.


**Approach 3: Use OpenBB SDK Documentation page**
Finally, if you prefer to check documentation on a web browser, OpenBB SDK Documentation[https://openbb-finance.github.io/OpenBBTerminal/api/] will be your best friend. You can browse available commands and search for any specific one that you need.





[INSERT CHART]
### 4. Set API Keys

TO BE COMPLETED once we finish the development

## Usage
### 1. Data Layer

### **Getting financial data from multiple data sources using one single API**
OpenBB SDK provides you access to normalized financial data from dozens of data sources, without having to built your own integration or relying on multiple third-party packages. Let's explore how we can do that.

First, you will need to load in the desired ticker. If it's not on the top of your mind, make use of our search functionality.
```
openbb.stocks.search("apple")
```

[INSERT CHART]

We want to load `Apple Inc.` listed on US exchange, so our ticker should be `AAPL`. Let's say if you want to load from Brazilian exchange, you should load in `AAPL34.SA`.

```
df = openbb.stocks.load("AAPL")
```

What's extremely powerful about OpenBB SDK is that you can specify the data source. Depending on the asset class, we have a list of available data sources and it's only getting bigger with contributions from our open-source community.

```
## From YahooFinance
df_yf = openbb.stocks.load("AAPL", source='YahooFinance')


## From AlphaVantage
df_av = openbb.stocks.load("AAPL", source='AlphaVantage')


## From IEXCloud
df_iex = openbb.stocks.load("AAPL", source='IEXCloud')


## From Polygon
df_pol = openbb.stocks.load("AAPL", source='Polygon')

```


### **Easy option to switch between obtaining underlying data and charts**
Depending on your needs, you can get the outputs in form of data (e.g. `pandas dataframe`) or charts. If the latter is what you want, simple add `chart=True` as the last parameter.

### 1. Getting underlying data

```
openbb.economy.index(indices = ['sp500', 'nyse_ny', 'russell1000'], start_date = '2010-01-01')
```

[INSERT CHART - DF_SD]

You might be wondering how to find all the available indices. This type of information should be available in the docstring. Let's give it a try.

[INSERT CHART]

As mentioned in the docstring, you can access it with the following helper function.

```
openbb.economy.available_indices()
```
[INSERT CHART - DF_SD]


### 2. Getting charts

```
openbb.economy.index(indices = ['sp500', 'nyse_ny', 'russell1000'], start_date = '2010-01-01', chart=True)
```
[INSERT CHART - DF_VAR]


## 2. Toolbox Layer
In addition to financial data, you can also get access to a robust and powerful toolbox to perform analysis on different asset classes and on your portfolio.


Imagine that you would like to leverage existing financial calculations from OpenBB and apply it on your own data. This can be done easily as OpenBB SDK's commands usually accept a `dataframe` as an input. Here you can load it your data, either via a `csv`, `excel` file, or connecting directly with an `API` or a `database`. The possibilities are endless.

Let's go through an example to see how we can do it in a few simple steps. Here we shall see how to use `portfolio optimization` functionalities from OpenBB SDK.

#### Step 1. Loading order book

Here we will use an example orderbook for illustration purposes. You can totally upload your own order book

```
order_book_path = "portfolio/allocation/60_40_Portfolio.xlsx"
tickers, categories = openbb.portfolio.po.load(excel_file = order_book_path)
```

[INSERT CHART]


#### Step 2. Optimizing portfolio
The optimization process has a large variety of options including basic mean-variance techniques like optimizing for the maximum Sharpe ratio, minimizing variance and similar.

```
## Max Sharpe optimization
weights_max_sharpe, data_returns_max_sharpe = openbb.portfolio.po.maxsharpe(tickers)

print("Max Sharpe")
weights_max_sharpe
```
[INSERT CHART]

```
## Minimum risk optimization
weights_min_risk, data_returns_min_risk = openbb.portfolio.po.minrisk(tickers)

print("Min Risk")
weights_min_risk
```

[INSERT CHART]


These methods are basic because they don't account for concentration risk properly. For instance, you can see that much of the allocation falls on a few stocks.

This opens up the portfolio to a lot of unsystematic risk. Therefore, we have much more advanced techniques including Hierarchical Risk Parity and Nested Clustered Optimization.

```
## Hierarchical Risk Parity optimization

weights_hrp, data_returns_hrp = openbb.portfolio.po.hrp(tickers)

print("Hierarchical Risk Parity")
weights_hrp

```


```
openbb.portfolio.po.plot(data=data_returns_hrp,weights=weights_hrp,heat=True)
```

[INSERT CHART]


```
openbb.portfolio.po.plot(data=data_returns_hrp,weights=weights_hrp,rc_chart=True)
```
[INSERT CHART]

These functionalities have an extensive list of parameters and thus the optimization process is also highly dependent on these calculations. E.g. see the following documentation.

[INSERT CHART]


This allows us to alter certain assumption which also alters the outcome, for example.

```
weights_hrp_2, data_returns_hrp_2 = openbb.portfolio.po.hrp(
    tickers,
    interval="5y",
    risk_measure="cVaR",
    risk_aversion=0.8
)

pd.DataFrame([weights_hrp, weights_hrp_2], index=["Basic", "Extended"]).T

```
[INSERT CHART]

THe basic method optimized for *variance*. The extended method increases the period of historical data, optimizes for conditional Value at Risk and has a lower risk aversion.

```openbb.portfolio.po.plot(data=data_returns_hrp,weights=weights_hrp,pie=True)```

[INSERT CHART]


```openbb.portfolio.po.plot(data=data_returns_hrp_2,weights=weights_hrp_2,pie=True)```


[INSERT CHART]



## Useful tips

### 1. Display matplotlib charts in Jupyter Notebook**\
If you copy-paste the code below and use it as your initialization then you're matplotlib graphs will be inside the result cell.

```python
import matplotlib.pyplot as plt
import matplotlib_inline.backend_inline
from openbb_terminal.api import openbb
%matplotlib inline
matplotlib_inline.backend_inline.set_matplotlib_formats("svg")
```


### 2. Take advantage of `external_axes`
The code below utilizes the `external_axes` parameter to get two axis in one chart.

```python
import matplotlib.pyplot as plt
from openbb_terminal.api import openbb
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(11, 5), dpi=150)
openbb.stocks.dps.dpotc(
    "aapl",
    external_axes=[ax1, ax2],
    chart=True,
)
fig.tight_layout()
```

You can also do this to save output charts in a variable for later uses.


### For more examples, we'd recommend checking out our [curated Jupyter Notebook reports](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/reports). They are excellent demonstration on how to use the SDK to its fullest extent!
