# Portfolio Optimization

This menu aims to optimize a portfolio of pre-loaded stocks, and the usage of the following commands along with an example will be exploited below.

* [add](#add)
  * add ticker to optimize
* [select](#select)
  * overwrite current tickers with new tickers
* [equal](#equal)
  * equally weighted
* [property](#property)
  * weight according to selected info property (e.g. marketCap)

[Mean Variance Optimization](#Mean_Variance_Optimization)

* [maxsharpe](#maxsharpe)
  * optimizes for maximal Sharpe ratio (a.k.a the tangency portfolio)
* [minvol](#minvol)
  * optimizes for minimum volatility
* [maxquadutil](#maxquadutil)
  * maximises the quadratic utility, given some risk aversion
* [effret](#effret)
  * maximises return for a given target risk
* [effrisk](#effrisk)
  * minimises risk for a given target return
* [ef](#ef)
  * show the efficient frontier


### add <a name="add"></a>

```text
add [-t ADD_TICKERS]
```

Add/Select tickers for portfolio to be optimized.

* -t : Tickers to be used in the portfolio to optimize
* 

### select <a name="select"></a>

```text
select [-t ADD_TICKERS]
```

Add/Select tickers for portfolio to be optimized.

* -t : Tickers to be used in the portfolio to optimize


### equal <a name="equal"></a>

```text
equal [-v VALUE] [--pie]
```

Returns an equally weighted portfolio

* -v : If provided, this represents an actual allocation amount for the portfolio.  Defaults to 1, which just returns the weights.
* --pie : Display a pie chart for weights


### property <a name="property"></a>

```text
property [-p PROPERTY] [-v VALUE] [--pie]
```

Returns a portfolio that is weighted based on a selected property info

* -p : Property info to weigh. Use one of: previousClose, regularMarketOpen, twoHundredDayAverage, trailingAnnualDividendYield, payoutRatio, volume24Hr, regularMarketDayHigh, navPrice, averageDailyVolume10Day, totalAssets, regularMarketPreviousClose, fiftyDayAverage, trailingAnnualDividendRate, open, toCurrency, averageVolume10days, expireDate, yield, algorithm, dividendRate, exDividendDate, beta, circulatingSupply, regularMarketDayLow, priceHint, currency, trailingPE, regularMarketVolume, lastMarket, maxSupply, openInterest, marketCap, volumeAllCurrencies, strikePrice, averageVolume, priceToSalesTrailing12Months, dayLow, ask, ytdReturn, askSize, volume, fiftyTwoWeekHigh, forwardPE, fromCurrency, fiveYearAvgDividendYield, fiftyTwoWeekLow, bid, dividendYield, bidSize, dayHigh, annualHoldingsTurnover, enterpriseToRevenue, beta3Year, profitMargins, enterpriseToEbitda, 52WeekChange, morningStarRiskRating, forwardEps, revenueQuarterlyGrowth, sharesOutstanding, fundInceptionDate, annualReportExpenseRatio, bookValue, sharesShort, sharesPercentSharesOut, fundFamily, lastFiscalYearEnd, heldPercentInstitutions, netIncomeToCommon, trailingEps, lastDividendValue, SandP52WeekChange, priceToBook, heldPercentInsiders, shortRatio, sharesShortPreviousMonthDate, floatShares, enterpriseValue, threeYearAverageReturn, lastSplitFactor, legalType, lastDividendDate, morningStarOverallRating, earningsQuarterlyGrowth, pegRatio, lastCapGain, shortPercentOfFloat, sharesShortPriorMonth, impliedSharesOutstanding, fiveYearAverageReturn, and regularMarketPrice.
* -v : If provided, this represents an actual allocation amount for the portfolio.  Defaults to 1, which just returns the weights.
* --pie : Display a pie chart for weights


## Mean Variance Optimization <a name="Mean_Variance_Optimization"></a>

These approaches are based off of the efficient frontier approach, which is meant to solve the following optimization problem.

Minimize: <img src="https://latex.codecogs.com/svg.image?w^TS&space;w" title="w^TS w" />

Subject to: <img src="https://latex.codecogs.com/svg.image?w^TR&space;>&space;R^*" title="w^TR > R^*" />, and <img src="https://latex.codecogs.com/svg.image?w_1&plus;w_2&plus;...w_n&space;=&space;1" title="w_1+w_2+...w_n = 1" />

* Where S is the covariance matrix between stocks and R is the expected returns.  
* The condition that all weights add up to 1 just implies that you want to have a net long portfolio (with no margin).  
* A long-short portfolio can have negative weights and usually wants to have everything add up to 0 for a market-neutral strategy.

Currently, we do not allow for changing risk models or adding constraints.  
If there is something specific, please submit a feature request, or if you can write it, feel free to add a PR!
All of these commands use [PyPortFolioOpt](#https://pyportfolioopt.readthedocs.io/en/latest/index.html) package.

### maxsharpe <a name="maxhsarpe"></a>

````
usage: max_sharpe [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [--pie] [-r RISK_FREE_RATE]
````

Maximise the Sharpe Ratio. The result is also referred to as the tangency portfolio, as it is the portfolio for which the capital market line is tangent to the efficient frontier. This is a convex optimization problem after making a certain variable substitution. See Cornuejols and Tutuncu (2006) <http://web.math.ku.dk/~rolf/CT_FinOpt.pdf> for more. The sharpe ratio is defined as (Mean Returns - Risk Free Rate)/(Standard Deviation of Returns).

* -p : Amount of time to retrieve data from yfinance. Default: 3mo.
* -v : If provided, this represents an actual allocation amount for the portfolio.  Defaults to 1, which just returns the weights.
* --pie : Display a pie chart for weights


### minvol <a name="minvol"></a>

````
usage: minvol [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [--pie]
````

This portfolio minimizes the total volatility, which also means it has the smallest returns among the efficient frontier.

* -p : Amount of time to retrieve data from yfinance. Default: 3mo.
* -v : If provided, this represents an actual allocation amount for the portfolio.  Defaults to 1, which just returns the weights.
* --pie : Display a pie chart for weights


### maxquadutil <a name="maxquadutil"></a>

````
usage: maxquadutil [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [--pie] [-r RISK_AVERSION] [-n]
````

Maximises the quadratic utility, given some risk aversion.

* -p : Amount of time to retrieve data from yfinance. Default: 3mo.
* -v : If provided, this represents an actual allocation amount for the portfolio.  Defaults to 1, which just returns the weights.
* --pie : Display a pie chart for weights
* -r : Risk aversion parameter
* -n : Whether the portfolio should be market neutral (weights sum to zero). Defaults: False.


### effret <a name="effret"></a>

````
usage: effret [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [--pie] [-t TARGET_RETURN] [-n]
````

Calculate the 'Markowitz portfolio', minimising volatility for a given target return.

* -p : Amount of time to retrieve data from yfinance. Default: 3mo.
* -v : If provided, this represents an actual allocation amount for the portfolio.  Defaults to 1, which just returns the weights.
* --pie : Display a pie chart for weights
* -t : The desired return of the resulting portfolio
* -n : Whether the portfolio should be market neutral (weights sum to zero). Defaults: False.


### effrisk <a name="effrisk"></a>

````
usage: effrisk [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [--pie] [-t TARGET_VOLATILITY] [-n]
````

Maximise return for a target risk. The resulting portfolio will have a volatility less than the target (but not guaranteed to be equal).

* -p : Amount of time to retrieve data from yfinance. Default: 3mo.
* -v : If provided, this represents an actual allocation amount for the portfolio.  Defaults to 1, which just returns the weights.
* --pie : Display a pie chart for weights
* -t : The desired maximum volatility of the resultingportfolio
* -n : Whether the portfolio should be market neutral (weights sum to zero). Defaults: False.


### ef

````
usage: ef [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-n N_PORT] 
````

This function plots random portfolios based on their risk and returns and shows the efficient frontier.
     
* -n : Number of portfolios to simulate. Default 300.
* -p : Amount of time to retrieve data from yfinance. Options are: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max and it defaults to 3mo.



## Sample Usage
In this example, we generate weights for a list of 6 stocks using the eff_ret command.  This optimization looks to maximize returns 
at a given risk level.  We start by adding the stocks we want to analyze:
````
select aapl,amzn,msft,f,gm,ge
````
Which shows:
````
Current Tickers: GE, GM, AMZN, AAPL, F, MSFT
````
To perform the optimization, we will set a target return of 25% (.25).  Given how stocks performed during COVID,
there is a lot of volatility, so many optimizations may not get low volatility.  The module also returns annualized volatility,
so the number is your portfolio volatility * `sqrt(252`.  This optimization will be (including a pie chart!).  Note we could also supply a different
time period, which changes the expected returns and historical volatility, which changes the optimization.  We could also specify a dollar
amount that you wish to allocate using the `-v` flag.
````
eff_ret -r .25 --pie
````
The console will show (numbers will vary based on when this is done).
![console](https://user-images.githubusercontent.com/18151143/114740311-bd429c80-9d17-11eb-90e2-97430781431a.png)

And the pie chart:

![yummypie](https://user-images.githubusercontent.com/18151143/114740289-b9167f00-9d17-11eb-9c29-470785b21d09.png)

Note that since `AAPL` had zero allocation, it was omitted from the chart.
