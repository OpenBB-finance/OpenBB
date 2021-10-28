# STOCKS

## Commands

#### Load
```
usage: load [-t S_TICKER] [-s S_START_DATE] [-i {1,5,15,30,60}] [--source {yf,av,iex}] [-p]
```
Load stock ticker to perform analysis on. When the data source is 'yf', an Indian ticker can be loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in <https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html>.
  * -t : Stock ticker
  * -s : The starting date (format YYYY-MM-DD) of the stock
  * -i : Intraday stock minutes
  * --source : Source of historical data. 'yf' and 'av' available. Default 'yf'
  * -p : Pre/After market hours. Only works for 'yf' source, and intraday data

#### Quote
```
quote -t S_TICKER
```
Show the current price of a stock.

<img width="896" alt="Captura de ecrã 2021-08-06, às 21 31 12" src="https://user-images.githubusercontent.com/25267873/128567977-7185427e-1511-460e-954d-047b53ea5c7d.png">

#### Candle
```
candle -s START_DATE
```
Visualize candles historical data, with support and resistance bars, and moving averages of 20 and 50.

![nio](https://user-images.githubusercontent.com/25267873/111053397-4d609e00-845b-11eb-9c94-89b8892a8e81.png)


#### News

```text
news [-n N_NUM] [-d N_START_DATE] [-o] [-s N_SOURCES [N_SOURCES ...]]
```

Prints latest news about company, including date, title and web link. [Source: News API]

* -n : Number of latest news being printed. Default 5.
* -d : The starting date (format YYYY-MM-DD) to search articles from.
* -o : Show oldest articles first.
* -s : Show news only from the sources specified (e.g bbc yahoo.com)

<img width="770" alt="Captura de ecrã 2021-03-22, às 22 47 42" src="https://user-images.githubusercontent.com/25267873/112070935-b2587a00-8b66-11eb-8dfb-0353fc83311d.png">





## [Research »»](research/README.md)

Command|Website
----|----
`macroaxis`         |<https://www.macroaxis.com>
`yahoo`             |<https://www.finance.yahoo.com>
`finviz`            |<https://www.finviz.com>
`marketwatch`       |<https://www.marketwatch.com>
`fool`              |<https://www.fool.com>
`businessinsider`   |<https://www.markets.businessinsider.com>
`fmp`               |<https://www.financialmodelingprep.com>
`fidelity`          |<https://www.eresearch.fidelity.com>
`tradingview`       |<https://www.tradingview.com>
`marketchameleon`   |<https://www.marketchameleon.com>
`stockrow`          |<https://www.stockrow.com>
`barchart`          |<https://www.barchart.com>
`grufity`           |<https://www.grufity.com>
`fintel`            |<https://www.fintel.com>
`zacks`             |<https://www.zacks.com>
`macrotrends`       |<https://www.macrotrends.net>
`newsfilter`        |<https://www.newsfilter.io>
`stockanalysis`     |<https://www.stockanalysis.com>

&nbsp;



## [Residual Analysis »»](residuals_analysis/README.md)

Command|Description|More Info
------ | --------|----
`pick`          |pick one of the model fitting | Supports [ARIMA](https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average), [Naive](https://en.wikipedia.org/wiki/Forecasting#Naïve_approach)
`fit`           |show model fit against stock | [Wikipedia](https://en.wikipedia.org/wiki/Curve_fitting)
`res`           |show residuals | [Wikipedia](https://en.wikipedia.org/wiki/Errors_and_residuals)
`hist`          |histogram and density plot | [Wikipedia](https://en.wikipedia.org/wiki/Histogram)
`qqplot`        |residuals against standard normal curve | [Wikipedia](https://en.wikipedia.org/wiki/Q–Q_plot)
`acf`           |(partial) auto-correlation function | [Wikipedia](https://en.wikipedia.org/wiki/Autocorrelation)
`normality`     |normality test (Kurtosis,Skewness,...) | [Wikipedia](https://en.wikipedia.org/wiki/Normality_test)
`goodness`      |goodness of fit test (Kolmogorov-Smirnov) | [Wikipedia](https://en.wikipedia.org/wiki/Goodness_of_fit)
`arch`          |autoregressive conditional heteroscedasticity | [Wikipedia](https://en.wikipedia.org/wiki/Autoregressive_conditional_heteroskedasticity)
`unitroot`      |unit root test / stationarity (ADF, KPSS) | [Wikipedia](https://en.wikipedia.org/wiki/Unit_root_test)
`independence`  |tests independent and identically distributed (BDS) | [Wikipedia](https://en.wikipedia.org/wiki/Pearson%27s_chi-squared_test#Testing_for_statistical_independence)

&nbsp;

## [Screener »»](screener/README.md)

Command|Description
------ | --------
view           |view [preset(s)](/gamestonk_terminal/stocks/screener/presets/README.md)
set            |set one of the [presets](/gamestonk_terminal/stocks/screener/presets/README.md)
[Yahoo Finance](https://finance.yahoo.com/) |
historical     |view historical price
[Finviz](https://finviz.com/screener.ashx) |
overview       |overview (e.g. Sector, Industry, Market Cap, Volume)
valuation      |valuation (e.g. P/E, PEG, P/S, P/B, EPS this Y)
financial      |financial (e.g. Dividend, ROA, ROE, ROI, Earnings)
ownership      |ownership (e.g. Float, Insider Own, Short Ratio)
performance    |performance (e.g. Perf Week, Perf YTD, Volatility M)
technical      |technical (e.g. Beta, SMA50, 52W Low, RSI, Change)
signals        |view filter signals (e.g. -s top_gainers)

&nbsp;

## [Insider »»](insider/README.md)

Entire menu relies on [Open Insider](http://openinsider.com).

Command|Description
------ | --------
view           |view [preset(s)](/gamestonk_terminal/stocks/insider/presets/README.md)
set            |set one of the [presets](/gamestonk_terminal/stocks/insider/presets/README.md)
filter         |filter insiders based on preset
**Latest** |
lcb |latest cluster boys
lpsb | latest penny stock buys
lit | latest insider trading (all filings)
lip | latest insider purchases
blip |  big latest insider purchases ($25k+)
blop | big latest officer purchases ($25k+)
blcp | big latest CEO/CFO purchases ($25k+)
lis | latest insider sales
blis | big latest insider sales ($100k+)
blos | big latest officer sales ($100k+)
blcs | big latest CEO/CFO sales ($100k+)
**Top** |
topt | top officer purchases today
toppw | top officer purchases past week
toppm | top officer purchases past month
tipt | top insider purchases today
tippw | top insider purchases past week
tippm | top insider purchases past month
tist | top insider sales today
tispw | top insider sales past week
tispm | top insider sales past month

&nbsp;


## [Backtesting »»](backtesting/README.md)

Command|Description
------ | --------
`ema`           | buy when price exceeds EMA(l)
`ema_cross`     | buy when EMA(short) > EMA(long)
`rsi`           | buy when RSI < low and sell when RSI > high


## [Government »»](government/README.md)

Entire menu relies on [Quiver Quantitative](https://www.quiverquant.com).

Command|Description
----|----
`last_congress`         | last congress trading
`buy_congress`          | plot top buy congress tickers
`sell_congress`         | plot top sell congress tickers
`last_senate`           | last senate trading
`buy_senate`            | plot top buy senate tickers
`sell_senate`           | plot top sell senate tickers
`last_house`            | last house trading
`buy_house`             | plot top buy house tickers
`sell_house`            | plot top sell house tickers
`last_contracts`        | last government contracts
`sum_contracts`         | plot sum of last government contracts
**When TICKER is provided** |
`raw_congress`          | raw congress trades on the ticker
`congress`              | plot congress trades on the ticker
`raw_senate`            | raw senate trades on the ticker
`senate`                | plot senate trades on the ticker
`raw_house`             | raw house trades on the ticker
`house`                 | plot house trades on the ticker
`raw_contracts`         | raw contracts on the ticker
`contracts`             | plot sum of contracts on the ticker

&nbsp;
