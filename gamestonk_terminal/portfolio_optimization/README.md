# Portfolio Optimization

This menu aims to discover optimal portfolios for selected stocks.

Currently we support two methods:

* [Property Weighting](#weighting)
    * Equal Weights
    * Market Cap Weighting
    * Divident Yield Weighting
* [Mean-Variance-Optimization](#eff_front)
    * Max sharpe ratio
    * Minimum volatility
    * Maximum returns at given risk level
    * Minimum risk level at a given return 

## Procedure
There are three ways to load stocks to be analyzed. 
* add
* select
* from ca menu
###add
Adds selected tickers to the menu to be considered

````
usage: add ticker1,ticker2,ticker3,...
````
###select
Clears current list and loads selected ticker
````
usage: select ticker1,ticker2,ticker3,...
````

### ca menu
From the ca menu, the loaded ticker and the selected similar tickers can be loaded by entering the `> po` menu.

From this `po` menu, you can return to `ca` using `ca`, which will keep your loaded stock, but reset the selected stocks from that menu.

Once your stocks are listed, you can select one of the options.
## Property weighted <a name="weighting"></a>
* equal weights
* market cap weighted
* dividend yield weighted
### equal weights
````
equal_weight
````
Returns `{"Ticker" : 1/# of tickers}`
### market cap weighted
````
mkt_cap
````
Returns a dictionary where each weight is given as (Company Market Cap)/(Sum all included market caps)
###dividened yield weighted
````
div_yield
````
Returns weights based on relative divident yield.

## Mean Variance Optimization<a name="eff_front"></a>

These approaches are based off of the efficient frontier approach, which is meant to solve the following optimization problem.

<img src="https://latex.codecogs.com/svg.image?w^TS&space;w" title="w^TS w" />

With constraints:

<img src="https://latex.codecogs.com/svg.image?w^TR&space;>&space;R^*" title="w^TR > R^*" />

\
<img src="https://latex.codecogs.com/svg.image?w_1&plus;w_2&plus;...w_n&space;=&space;1" title="w_1+w_2+...w_n = 1" />

Where S is the covariance matrix between stocks and R is the expected returns.  The condition that all weights add up to 1
just implies that you want to have a net long portfolio (with no margin).  
A long-short portfolio can have negative weights and usually wants to have everything add up to 0 for a market-neutral strategy.

Currently, we do not allow for changing risk models or adding constraints.  If there is something spefic, please submit a feature request, or if you can
write it, feel free to add a PR!

All of our current implementations use the [PyPortFolioOpt](#https://pyportfolioopt.readthedocs.io/en/latest/index.html) package.

### max_sharpe
The sharpe ratio is defined as 

(Mean Returns - Risk Free Rate)/(Standard Deviation of Returns)

The usage is:
````
max_sharpe [-p PERIOD] 
````
* -p/--period Amount of time to retreive data from yfinance. Options are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max and it defualts to 3mo.

### min_vol
This portfolio minimizes the total volatility, which also means it has the smallest returns among the efficient frontier.
The usage is:
````
min_vol [-p PERIOD] 
````
* -p/--period Amount of time to retreive data from yfinance. Options are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max and it defualts to 3mo.

### eff_risk
This portfolio maximizes the returns at a given risk tolerance
The usage is:
````
eff_risk [-p PERIOD] [-r --risk RISK_LEVEL]
````
* -p/--period Amount of time to retreive data from yfinance. Options are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max and it defualts to 3mo.
* -r/--risk Risk tolerance.  5% is 0.05.

### eff_ret
This portfolio minimizes the risk at a given return level
The usage is:
````
eff_ret [-p PERIOD] [-r --return]
````
* -p/--period Amount of time to retreive data from yfinance. Options are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max and it defualts to 3mo.
* -r/--return.  Desired return.  5% is 0.05.

### show_eff
This function plots random portfolios basd on their risk and returns and shows the efficient frontier.
The usage is:
````
show_eff [-p PERIOD]  [-n N_PORTFOLIOS]
````
* -p/--period Amount of time to retreive data from yfinance. Options are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max and it defualts to 3mo.
* -n Number of portfolios to simulate.