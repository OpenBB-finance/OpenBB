---
title: Portfolio Optimization
keywords: ["portfolio", "optimization", "mean variance", "risk parity", "black litterman", "mean risk",
"hierarchical clustering models"]
excerpt: "The Introduction to Portfolio Optimization within the Portfolio menu explains how to use various portfolio
optimization techniques and provides a brief description of its sub-menus"
---
The Portfolio Optimization menu allows the user to apply advanced optimization techniques to a portfolio of any type and of any size. It does so by introducing a multitude of optimization techniques ranging from <a href="https://www.investopedia.com/terms/m/meanvariance-analysis.asp" target="_blank" rel="noreferrer noopener">mean-variance optimization</a> to <a href="https://www.investopedia.com/terms/r/risk-parity.asp" target="_blank" rel="noreferrer noopener">risk parity models</a> and <a href="https://www.investopedia.com/terms/c/cluster_analysis.asp" target="_blank" rel="noreferrer noopener">hierarchical clustering models</a>. By providing Excel templates, the user can make sense of the vast array of parameters that each command has. E.g. think of the historic period you wish to use or which of the more than 10 risk measures and covariance methods should be used? These are questions the templates make easier to answer.

The capabilities of the [Portfolio Optiminzation menu](/terminal/guides/intros/portfolio/po) from the OpenBB Terminal are wrapped into a powerful SDK, enabling users to work with the data in a flexible environment that can be fully customized to meet the needs of any user. These functionalities allow the user to apply advanced optimization techniques to a portfolio of any type and of any size. It does so by introducing a multitude of optimization techniques ranging from <a href="https://www.investopedia.com/terms/m/meanvariance-analysis.asp" target="_blank" rel="noreferrer noopener">mean-variance optimization</a> to <a href="https://www.investopedia.com/terms/r/risk-parity.asp" target="_blank" rel="noreferrer noopener">risk parity models</a> and <a href="https://www.investopedia.com/terms/c/cluster_analysis.asp" target="_blank" rel="noreferrer noopener">hierarchical clustering models</a>. By providing Excel templates, the user can make sense of the vast array of parameters that each command has. E.g. think of the historic period you wish to use or which of the more than 10 risk measures and covariance methods should be used? These are questions the templates make easier to answer.

## How to use
Start a Python script or Notebook file by importing the module:

```python
from openbb_terminal.sdk import openbb
```

This menu requires the usage of the Excel templates to work properly. As there is a lot of complexity involved around these techniques, these templates allow the user to understand what values for each parameter are actually used and allow for an easy way to define the allocation.

:::note For this there are two templates that need to be set, the **OpenBB Parameters Template** and the **60_40_Portfolio.xlsx**. These files can be found in [here](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/miscellaneous/portfolio_examples). One is in the `allocation` folder and the other is in `optimization`. the Select a file and press "Download" on the right, then place it into the OpenBBUserData folder. You can find more about this folder [here](/sdk/advanced/data).
:::

### OpenBB Parameters Template
This template provides the user with the ability to set define values for each parameter based on the optimization technique that is deployed. E.g. if you select `riskparity` for the `technique` parameter, you will notice that some parameters turn <span style={{color: "#BEBEBE"}}>grey</span>. This means that the parameter is irrelevant for the selected method.

The OpenBB Terminal does, however, allow the user to run any model despite the `technique` you selected. Therefore, if you are interested in running multiple models, consider removing the value for `technique`. Do note that this makes it more difficult to understand which values are used for which model.

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171144692-dd812efd-1e95-4a71-a93f-7ae8a480fe5d.png"><img alt="OpenBB Parameters Template" src="https://user-images.githubusercontent.com/46355364/171144692-dd812efd-1e95-4a71-a93f-7ae8a480fe5d.png"></img></a>

### OpenBB Portfolio Template
This template hands the user a format to work with it to define the portfolio. Here, categorization is applied based on asset class, sector, industry, country and currency. By using the dropdown menus within this Excel, you are able to apply the proper categorization. This is based on the same methodology as found in other areas of the terminal.

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171145061-cd618153-801c-4771-ba57-7ee0ab8c57e8.png"><img alt="OpenBB Portfolio Template" src="https://user-images.githubusercontent.com/46355364/171145061-cd618153-801c-4771-ba57-7ee0ab8c57e8.png"></img></a>

You can load in the portfolio template with the following code:

```python
import pandas as pd

# Define your own orderbook path here, current value won't work
order_book_path = "60_40_Portfolio.xlsx"

# Read in the file
order_book = pd.read_excel(order_book_path)

# Adjust the columns accordingly
order_book_cols = ['Ticker', 'Asset Class', 'Sector', 'Industry', 'Country',
       'Current Invested Amount', 'Currency']

order_book = order_book[order_book_cols]

# Load in the portfolio
p = openbb.portfolio.po.load(symbols_file_path=order_book_path)
weights, performance = openbb.portfolio.po.equal(portfolio_engine=p)
```

### Performing optimization
Based on the parameters and allocation the user has set, the optimization process begins. What optimization technique is ideal depends entirely on the user's risk profile and objectives. As an illustration, <a href="https://www.investopedia.com/terms/r/risk-parity.asp" target="_blank" rel="noreferrer noopener">Risk Parity</a> is presented below:

```python
# Perform calculations
weights_riskparity, data_returns_riskparity = openbb.portfolio.po.riskparity(p)

weights_riskparity
```

Which returns:

|       |   Risk Parity |
|:------|--------------:|
| AAPL  |       0.0462  |
| AMZN  |       0.04545 |
| APTV  |       0.03177 |
| ASML  |       0.03328 |
| BABA  |       0.04192 |
| GOOGL |       0.04758 |
| HYG   |       0.13093 |
| NKE   |       0.04909 |
| TIP   |       0.30826 |
| TLT   |       0.21927 |
| TSM   |       0.04626 |

It is possible to use the commands without loading in the parameters template or by using the parameters template but changing some arguments directly into the terminal. For example, using the same method as described above, the risk measure is changed to <a href="https://www.investopedia.com/terms/c/conditional_value_at_risk.asp" target="_blank" rel="noreferrer noopener">Conditional Value at Risk (CVaR)</a> and the used historic period is increased to 10 years (keeping all other parameters unchanged):

```python
# Perform calculations
weights_riskparity, data_returns_riskparity = openbb.portfolio.po.riskparity(p, interval="10y", risk_measure="CVaR")

weights_riskparity
```

Which returns:

|       |   Risk Parity |
|:------|--------------:|
| AAPL  |       0.04843 |
| AMZN  |       0.04302 |
| APTV  |       0.03907 |
| ASML  |       0.03717 |
| GOOGL |       0.04877 |
| HYG   |       0.14643 |
| NKE   |       0.05275 |
| TIP   |       0.33264 |
| TLT   |       0.20371 |
| TSM   |       0.04802 |



## Examples
To demonstrate the capabilities of the Portfolio Optimization menu, the entire <a href="https://www.investopedia.com/terms/s/sp500.asp" target="_blank" rel="noreferrer noopener">S&P 500 index</a> (as of 30th of May 2022) is used and optimized and analysed in a variety of ways. Starting by loading in the dataset with the following:

```python
import pandas as pd

# Define your own orderbook path here, current value won't work
order_book_path = "pathto/SP_500_Portfolio.xlsx"

# Read in the file
order_book = pd.read_excel(order_book_path)

# Adjust the columns accordingly
order_book_cols = ['Ticker', 'Asset Class', 'Sector', 'Industry', 'Country',
       'Current Invested Amount', 'Currency']

order_book = order_book[order_book_cols]

# Load in the portfolio
tickers, categories = openbb.portfolio.po.load(symbols_file_path=order_book_path)
```

Then, the <a href="https://jpm.pm-research.com/content/42/4/59.short" target="_blank" rel="noreferrer noopener">Hierarchical Risk Parity</a> technique is applied by using the following:

```python
order_book_path = "pathto/SP_500_Portfolio.xlsx"

order_book = pd.read_excel(order_book_path)
# Adjust the columns accordingly
order_book_cols = [
    'Ticker',
    'Asset Class',
    'Sector',
    'Industry',
    'Country',
    'Current Invested Amount',
    'Currency',
]

order_book = order_book[order_book_cols]

p = openbb.portfolio.po.load(symbols_file_path=order_book_path)
riskparity, data_returns_riskparity = openbb.portfolio.po.hrp(p, interval="5y",
    risk_measure='SLPM',
    risk_aversion=0.8)

print(riskparity)
print(data_returns_riskparity)
```

This results in the following (the result is edited, as it would show 500 tickers, to prevent flooding this page):

|       |   Hierarchical Risk Parity |
|:------|---------------------------:|
| A     |                    0.00199 |
| AAL   |                    0.00104 |
| AAP   |                    0.00185 |
| AAPL  |                    0.00184 |
| ABBV  |                    0.0028  |
| ...   | ... |
| NOC   |                    0.00228 |
| XOM   |                    0.00167 |
| ZBRA  |                    0.00156 |
| ZION  |                    0.0014  |
| ZTS   |                    0.00225 |

It is possible to delve further into these findings with the `plot` functionality for example done by looking at the portfolio's returns <a href="https://www.investopedia.com/terms/h/histogram.asp" target="_blank" rel="noreferrer noopener">histogram</a> which also includes a variety of risk measures as well as the portfolio's drawdowns.

````
openbb.portfolio.po.plot(p, category='SECTOR', chart_type="hist")
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171145848-5a3f5333-6b7f-4d7a-a96e-0859adb1ce78.png"><img alt="Portfokio Returns Histogram" src="https://user-images.githubusercontent.com/46355364/171145848-5a3f5333-6b7f-4d7a-a96e-0859adb1ce78.png"></img></a>

````
openbb.portfolio.po.plot(p, category='SECTOR', chart_type="dd")
````

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/171145983-2d2c1c2e-67d2-4839-b43a-51bd22332de8.png"><img alt="Portfolio Drawdowns" src="https://user-images.githubusercontent.com/46355364/171145983-2d2c1c2e-67d2-4839-b43a-51bd22332de8.png"></img></a>
