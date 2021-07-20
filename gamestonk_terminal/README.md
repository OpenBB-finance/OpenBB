# Features 📈

### Table of contents

* [Discover Stocks](#Discover-Stocks-)
* [Behavioural Analysis](#Behavioural-Analysis-)
* [Research](#Research-)
* [Fundamental Analysis](#Fundamental-Analysis-)
* [Technical Analysis](#Technical-Analysis-)
* [Due Diligence](#Due-Diligence-)
* [Prediction Techniques](#Prediction-Techniques-)
* [Portfolio Analysis](#Portfolio-Analysis-)
* [Brokers](#Brokers-)
* [Portfolio Optimization](#Portfolio-Optimization-)
* [Cryptocurrencies](#Cryptocurrencies-)
* [Comparison Analysis](#Comparison-Analysis-)
* [Exploratory Data Analysis](#Exploratory-Data-Analysis-)
* [Residual Analysis](#Residual-Analysis-)
* [Economy](#Economy)
* [Options](#Options-)
* [Screener](#Screener-)
* [Forex](#Forex-)
* [Backtesting](#Backtesting-)
* [Resource Collection](#Resource-Collection-)
* [Government](#Government-)
* [ETF](#ETF-)

## Main

The main menu allows the following commands:

```
usage: load [-t S_TICKER] [-s S_START_DATE] [-i {1,5,15,30,60}] [--source {yf,av,iex}] [-p]
```

* Load stock ticker to perform analysis on. When the data source is 'yf', an Indian ticker can be loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in <https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html>.
  * -t : Stock ticker
  * -s : The starting date (format YYYY-MM-DD) of the stock
  * -i : Intraday stock minutes
  * --source : Source of historical data. 'yf' and 'av' available. Default 'yf'
  * -p : Pre/After market hours. Only works for 'yf' source, and intraday data

**Note:** Until a ticker is loaded, the menu will only show *disc* and *sen* menu, as the others require a ticker being provided.

```
usage: clear
```

* Clear previously loaded stock ticker.

```
view
```

* Visualise historical data of a stock.
![AAPL](https://user-images.githubusercontent.com/18151143/125211301-69424800-e273-11eb-853d-0b7a0db8ffb7.png)


Line plot color is configurable in config_plot.py

```
quote -t S_TICKER
```

* Show the current price of a stock.

```
candle -s START_DATE
```

* Visualize candles historical data, with support and resistance bars, and moving averages of 20 and 50.

![nio](https://user-images.githubusercontent.com/25267873/111053397-4d609e00-845b-11eb-9c94-89b8892a8e81.png)

```
export -f GNUS_data -F csv
```

* Exports the historical data from this ticker to a file or stdout.
  * -f : Name of file to save the historical data exported (stdout if unspecified). Default: stdout.
  * -F : Export historical data into following formats: csv, json, excel, clipboard. Default: csv.

## Discover Stocks [»](discovery/README.md)

Command|Description|Source
---|---|---
`ipo`           |past and future IPOs |[Finnhub](https://finnhub.io)
`map`           |S&P500 index stocks map |[Finviz](https://finviz.com)
`rtp_sectors`   |real-time performance sectors |[Alpha Vantage](www.alphavantage.co)
`gainers`       |show latest top gainers |[Yahoo Finance](https://finance.yahoo.com/)
`losers`        |show latest top losers |[Yahoo Finance](https://finance.yahoo.com/)
`orders`        |orders by Fidelity Customers |[Fidelity](https://www.fidelity.com/)
`ark_orders`    |orders by ARK Investment Management LLC | [Cathiesark](https://www.cathiesark.com)
`up_earnings`   |upcoming earnings release dates |[Seeking Alpha](https://seekingalpha.com/)
`high_short`    |show top high short interest stocks of over 20% ratio |[High Short Interest](https://www.highshortinterest.com/)
`low_float`     |show low float stocks under 10M shares float |[Low Float](https://www.lowfloat.com/)
`simply_wallst` |Simply Wall St. research data |[Simply Wall St.](https://simplywall.st/about)
`spachero`      |great website for SPACs research |[SpacHero](https://www.spachero.com/)
`uwhales`       |good website for SPACs research |[UnusualWhales](https://unusualwhales.com/)
`valuation`     |valuation of sectors, industry, country |[Finviz](https://finviz.com)
`performance`   |performance of sectors, industry, country |[Finviz](https://finviz.com)
`spectrum`      |spectrum of sectors, industry, country |[Finviz](https://finviz.com)
`latest`        |latest news |[Seeking Alpha](https://seekingalpha.com/)
`trending`      |trending news |[Seeking Alpha](https://seekingalpha.com/)
`ratings`       |top ratings updates |[MarketBeat](https://marketbeat.com)
`darkpool`      |dark pool tickers with growing activity |[FINRA](https://www.finra.org)
`darkshort`     |dark pool short position|[Stockgrid](https://stockgrid.io)
`shortvol`      |short interest and days to cover |[Stockgrid](https://stockgrid.io)

&nbsp;

## Behavioural Analysis [»](behavioural_analysis/README.md)

Command|Description
----|----
[FinBrain](https://finbrain.tech)|
`finbrain`      |sentiment from 15+ major news headlines
`stats`         |sentiment stats including comparison with sector
[Reddit](https://reddit.com)|
`wsb`           |show what WSB gang is up to in subreddit wallstreetbets
`watchlist`     |show other users watchlist
`popular`       |show popular tickers
`spac_c`        |show other users spacs announcements from subreddit SPACs community
`spac`          |show other users spacs announcements from other subs
[Stocktwits](https://stocktwits.com/)|
`bullbear`      |estimate quick sentiment from last 30 messages on board
`messages`      |output up to the 30 last messages on the board
`trending`      |trending stocks
`stalker`       |stalk stocktwits user's last message
[Twitter](https://twitter.com/)|
`infer`         |infer about stock's sentiment from latest tweets
`sentiment`     |in-depth sentiment prediction from tweets over time
[Google](https://google.com/)|
`mentions`      |interest over time based on stock's mentions
`regions`       |regions that show highest interest in stock
`queries`       |top related queries with this stock
`rise`          |top rising related queries with stock

&nbsp;

## Research [»](research/README.md)

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

## Fundamental Analysis [»](fundamental_analysis/README.md)

Command|Description
----- | ---------
`screener`      |screen info about the company ([Finviz](https://finviz.com/))
`mgmt`          |management team of the company ([Business Insider](https://markets.businessinsider.com/))
`score`         |investing score from Warren Buffett, Joseph Piotroski and Benjamin Graham  ([FMP](https://financialmodelingprep.com/))
[Market Watch API](https://markets.businessinsider.com/) |
`income`        |income statement of the company
`balance`       |balance sheet of the company
`cash`          |cash flow statement of the company
[Yahoo Finance API](https://finance.yahoo.com/) |
`info`          |information scope of the company
`shrs`          |shareholders of the company
`sust`          |sustainability values of the company
`cal`           |calendar earnings and estimates of the company
[Alpha Vantage API](https://www.alphavantage.co/) |
`overview`      |overview of the company
`income`        |income statements of the company
`balance`       |balance sheet of the company
`cash`          |cash flow of the company
`earnings`      |earnings dates and reported EPS
[Financial Modeling Prep API](https://financialmodelingprep.com/) |
`profile`       |profile of the company
`quote`         |quote of the company
`enterprise`    |enterprise value of the company over time
`dcf`           |discounted cash flow of the company over time
`income`        |income statements of the company
`balance`       |balance sheet of the company
`cash`          |cash flow of the company
`metrics`       |key metrics of the company
`ratios`        |financial ratios of the company
`growth`        |financial statement growth of the company

&nbsp;

## Technical Analysis [»](technical_analysis/README.md)

Command | Description | Sources
------ | ------ | ------
`view`         | view historical data and trendlines| [Finviz](https://finviz.com/quote.ashx?t=tsla)
`summary`      | technical summary report| [FinBrain](https://finbrain.tech)
`recom`        | recommendation based on Technical Indicators| [Tradingview](https://uk.tradingview.com/widget/technical-analysis/)
`pr`           | pattern recognition| [Finnhub](https://finnhub.io)
[overlap](https://github.com/twopirllc/pandas-ta/tree/master/pandas_ta/overlap) |
`ema`         | exponential moving average | [Wikipedia](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average), [Investopedia](https://www.investopedia.com/terms/e/ema.asp)
`sma`         |simple moving average | [Wikipedia](https://en.wikipedia.org/wiki/Moving_average#Simple_moving_average_(boxcar_filter)), [Investopedia](https://www.investopedia.com/terms/s/sma.asp)
`vwap`        |volume weighted average price | [Wikipedia](https://en.wikipedia.org/wiki/Volume-weighted_average_price), [Investopedia](https://www.investopedia.com/terms/v/vwap.asp)
[momentum](https://github.com/twopirllc/pandas-ta/tree/master/pandas_ta/momentum) |
`cci`         |commodity channel index | [Wikipedia](https://en.wikipedia.org/wiki/Commodity_channel_index), [Investopedia](https://www.investopedia.com/terms/c/commoditychannelindex.asp)
`macd`        |moving average convergence/divergence | [Wikipedia](https://en.wikipedia.org/wiki/MACD), [Investopedia](https://www.investopedia.com/terms/m/macd.asp)
`rsi`         |relative strength index | [Wikipedia](https://en.wikipedia.org/wiki/Relative_strength_index), [Investopedia](https://www.investopedia.com/terms/r/rsi.asp)
`stoch`       |stochastic oscillator | [Wikipedia](https://en.wikipedia.org/wiki/Stochastic_oscillator), [Investopedia](https://www.investopedia.com/terms/s/stochasticoscillator.asp)
[trend](https://github.com/twopirllc/pandas-ta/tree/master/pandas_ta/trend) |
`adx`         |average directional movement index | [Wikipedia](https://en.wikipedia.org/wiki/Average_directional_movement_index), [Investopedia](https://www.investopedia.com/terms/a/adx.asp)
`aroon`       |aroon indicator | [Investopedia](https://www.investopedia.com/terms/a/aroon.asp)
[volatility](https://github.com/twopirllc/pandas-ta/tree/master/pandas_ta/volatility) |
`bbands`      |bollinger bands | [Wikipedia](https://en.wikipedia.org/wiki/Bollinger_Bands), [Investopedia](https://www.investopedia.com/terms/b/bollingerbands.asp)
[volume](https://github.com/twopirllc/pandas-ta/tree/master/pandas_ta/volume) |
`ad`          |chaikin accumulation/distribution line values | [Wikipedia](https://en.wikipedia.org/wiki/Accumulation/distribution_index), [Investopedia](https://www.investopedia.com/terms/a/accumulationdistribution.asp)
`obv`         |on balance volume | [Wikipedia](https://en.wikipedia.org/wiki/On-balance_volume), [Investopedia](https://www.investopedia.com/terms/o/onbalancevolume.asp)

&nbsp;

## Due Diligence [»](due_diligence/README.md)

Command|Description|Source
------ | --------|----
`news`          |latest news of the company |[Finviz](https://finviz.com/)
`red`           |gets due diligence from another user's post |[Reddit](https://reddit.com)
`analyst`       |analyst prices and ratings of the company |[Finviz](https://finviz.com/)
`rating`        |rating of the company from strong sell to strong buy | [FMP](https://financialmodelingprep.com/)
`pt`            |price targets over time |[Business Insider](https://www.businessinsider.com/)
`rot`           |ratings over time |[Finnhub](https://finnhub.io)
`est`           |quarter and year analysts earnings estimates |[Business Insider](https://www.businessinsider.com/)
`ins`           |insider activity over time |[Business Insider](https://www.businessinsider.com/)
`insider`       |insider trading of the company |[Finviz](https://finviz.com/)
`sec`           |SEC filings |[MarketWatch](https://www.marketwatch.com/)
`short`         |short interest |[Quandl](https://www.quandl.com/)
`warnings`      |company warnings according to Sean Seah book |[MarketWatch](https://www.marketwatch.com/)
`dp`            |dark pools (ATS) vs OTC data [FINRA](https://www.finra.org/#/)
`ftd`           |display fails-to-deliver data [SEC](https://www.sec.gov)
`shortview`     |shows price vs short interest volume [Stockgrid](https://stockgrid.io)
`darkpos`       |net short vs position [Stockgrid](https://stockgrid.io)
`supplier`      |list of suppliers [csimarket](https://csimarket.com)
`customer`      |list of customers [csimarket](https://csimarket.com)

&nbsp;

## Prediction Techniques [»](prediction_techniques/README.md)

Command|Technique|Sources
------ | ------------|---
`knn`         |k-Nearest Neighbors | [Wikipedia](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm)
`linear`      |linear regression (polynomial 1) | [Wikipedia](https://en.wikipedia.org/wiki/Linear_regression), [Investopedia](https://www.investopedia.com/terms/r/regression.asp)
`quadratic`   |quadratic regression (polynomial 2) | [Wikipedia](https://en.wikipedia.org/wiki/Polynomial_regression), [Investopedia](https://www.investopedia.com/terms/r/regression.asp)
`cubic`       |cubic regression (polynomial 3) | [Wikipedia](https://en.wikipedia.org/wiki/Polynomial_regression), [Investopedia](https://www.investopedia.com/terms/r/regression.asp)
`regression`  |regression (other polynomial) | [Wikipedia](https://en.wikipedia.org/wiki/Polynomial_regression), [Investopedia](https://www.investopedia.com/terms/r/regression.asp)
`arima`       |autoregressive integrated moving average | [Wikipedia](https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average), [Investopedia](https://www.investopedia.com/terms/a/autoregressive-integrated-moving-average-arima.asp)
`mlp`         |MultiLayer Perceptron | [Wikipedia](https://en.wikipedia.org/wiki/Multilayer_perceptron)
`rnn`         |Recurrent Neural Network  | [Wikipedia](https://en.wikipedia.org/wiki/Recurrent_neural_network)
`lstm`        |Long Short-Term Memory  | [Wikipedia](https://en.wikipedia.org/wiki/Long_short-term_memory), [Details](https://colah.github.io/posts/2015-08-Understanding-LSTMs/)
`conv1d`      |1D Convolution Neural Net| [Wikipedia](https://en.wikipedia.org/wiki/Convolutional_neural_network)
&nbsp;

## Portfolio Analysis [»](portfolio_analysis/README.md)

Command|Description
------ | ------------
`load`   | load portfolio from csv file
`group`  | view holdings by a user input group

&nbsp;

## Brokers [»](brokers/README.md)

Command|Description|Brokers
------ | ------------|---
`login`   | login to your brokers
`rhhold`  | view robinhood holdings | [Robinhood](https://robinhood.com/us/en/)
`rhhist`  | plot robinhood portfolio history | [Robinhood](https://robinhood.com/us/en/)
`alphold` | view alpaca holdings | [Alpaca](https://app.alpaca.markets/login)
`alphist` | view alpaca portfolio history | [Alpaca](https://app.alpaca.markets/login)
`allyhold`| view ally holdings | [Ally](https://www.ally.com/invest/)
`hold`    | view net holdings across all logins
`degiro`  | degiro standalone menu | [Degiro](https://trader.degiro.nl/login/#/login)

Degiro command|Description
------ | ------------
`cancel`| cancel an order using the `id`
`companynews`| view news about a company with it's isin
`create`    |  create an order
`hold`     |   view holdings
`lastnews`  |  view latest news
`login`      | connect to degiro's api
`logout`     | disconnect from degiro's api
`lookup`    |  view search for a product by name
`pending`   | view pending orders
`topnews`   |  view top news preview
`update`    |  view top news preview

&nbsp;

## Portfolio Optimization [»](portfolio_optimization/README.md)

Command|Description
------|------
`add`| add ticker to optimize
`select`| overwrite current tickers with new tickers
`equal`| equally weighted
`property`| weight according to selected info property (e.g. marketCap)
`maxsharpe`| optimizes for maximal Sharpe ratio (a.k.a the tangency portfolio)
`minvol`| optimizes for minimum volatility
`maxquadutil`| maximises the quadratic utility, given some risk aversion
`effret`| maximises return for a given target risk
`effrisk`| minimises risk for a given target return
`ef`| show the efficient frontier

&nbsp;

## Cryptocurrency [»](cryptocurrency/README.md)

Command|Description
------ | ------------
[coingecko](#https://www.coingecko.com/en)|
`load`| load cryptocurrency data
`view`| view loaded cryptocurrency data
`trend`| view top 7 coins
[coinmarketcap](#http://coinmarketcap.com)|
`top` | view top coins from coinmarketcap
[binance](#http://binance.us)|
`select` | select coin/currency to use and load candle data
`book`| show order book
`candle`| show candles
`balance`| show coin balance

&nbsp;

## Comparison Analysis [»](comparison_analysis/README.md)

Command|Description|Source
------ | --------|----
`get`           |get similar companies |[Polygon](https://polygon.io)
`select`        |select similar companies
`historical`    |historical price data comparison |[Yahoo Finance](https://finance.yahoo.com/)
`hcorr`         |historical price correlation |[Yahoo Finance](https://finance.yahoo.com/)
`income`        |income financials comparison |[MarketWatch](https://www.marketwatch.com/)
`balance`       |balance financials comparison |[MarketWatch](https://www.marketwatch.com/)
`cashflow`      |cashflow comparison |[MarketWatch](https://www.marketwatch.com/)
`sentiment`     |sentiment analysis comparison |[FinBrain](https://finbrain.tech)
`scorr`         |sentiment correlation |[FinBrain](https://finbrain.tech)

&nbsp;

## Exploratory Data Analysis [»](exploratory_data_analysis/README.md)

Command|Description|Source
------ | --------|----
`get`           |get similar companies |[Polygon](https://polygon.io)
`select`        |select similar companies
`historical`    |historical price data comparison |[Yahoo Finance](https://finance.yahoo.com/)
`hcorr`         |historical price correlation |[Yahoo Finance](https://finance.yahoo.com/)
`income`        |income financials comparison |[MarketWatch](https://www.marketwatch.com/)
`balance`       |balance financials comparison |[MarketWatch](https://www.marketwatch.com/)
`cashflow`      |cashflow comparison |[MarketWatch](https://www.marketwatch.com/)
`sentiment`     |sentiment analysis comparison |[FinBrain](https://finbrain.tech)
`scorr`         |sentiment correlation |[FinBrain](https://finbrain.tech)

&nbsp;

## Residual Analysis [»](residuals_analysis/README.md)

Command|Description|Source
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

## Economy [»](econ/README.md)

Command|Description|Source
------ | -------- | --------
`feargreed`     | CNN Fear Greed Index | <https://money.cnn.com/data/fear-and-greed/>
`events`        | economic impact events | <https://finnhub.io>
`fred`          | display customized FRED data | <https://fred.stlouisfed.org>
`vixcls`        | Volatility Index | <https://fred.stlouisfed.org>
`gdp`           | Gross Domestic Product | <https://fred.stlouisfed.org>
`unrate`        | Unemployment Rate | <https://fred.stlouisfed.org>
`dgs1`          | 1-Year Treasury Constant Maturity Rate | <https://fred.stlouisfed.org>
`dgs5`          | 5-Year Treasury Constant Maturity Rate | <https://fred.stlouisfed.org>
`dgs10`         | 10-Year Treasury Constant Maturity Rate | <https://fred.stlouisfed.org>
`dgs30`         | 30-Year Treasury Constant Maturity Rate | <https://fred.stlouisfed.org>
`mortgage30us`  | 30-Year Fixed Rate Mortgage Average | <https://fred.stlouisfed.org>
`fedfunds`      | Effective Federal Funds Rate | <https://fred.stlouisfed.org>
`aaa`           | Moody's Seasoned AAA Corporate Bond Yield | <https://fred.stlouisfed.org>
`dexcaus`       | Canada / U.S. Foreign Exchange Rate (CAD per 1 USD) | <https://fred.stlouisfed.org>
`overview`      | Market overview  |  <https://www.wsj.com/market-data>
`indices`       | US indices overview  |  <https://www.wsj.com/market-data>
`futures`       | Futures/commodities overview  |  <https://www.wsj.com/market-data>
`us_bonds`      | US bonds overview  |  <https://www.wsj.com/market-data>
`gl_bonds`      | Global bonds overview  |  <https://www.wsj.com/market-data>
`currencies`    | Global currencies overview  |  <https://www.wsj.com/market-data>


&nbsp;

## Options [»](options/README.md)

Command|Description|Source
------ | --------|----
`exp`           | see/set expiry date
`volume`        | volume + open interest options trading plot |[Yahoo Finance](https://finance.yahoo.com/)
`vcalls`        | calls volume + open interest plot |[Yahoo Finance](https://finance.yahoo.com/)
`vputs`         | puts volume + open interest plot |[Yahoo Finance](https://finance.yahoo.com/)
`chains`        | displays option chains    |[Tradier](https://developer.tradier.com/)
`info`          | display option information | [Barchart](https://barchart.com/)

&nbsp;

## Screener [»](screener/README.md)

Command|Description|Source
------ | --------|----
view           |view available presets | [presets]((screener/presets/README.md))
set            |set one of the available presets
historical     |view historical price |[Yahoo Finance](https://finance.yahoo.com/)
[Finviz](https://finviz.com/screener.ashx) |
overview       |overview (e.g. Sector, Industry, Market Cap, Volume)
valuation      |valuation (e.g. P/E, PEG, P/S, P/B, EPS this Y)
financial      |financial (e.g. Dividend, ROA, ROE, ROI, Earnings)
ownership      |ownership (e.g. Float, Insider Own, Short Ratio)
performance    |performance (e.g. Perf Week, Perf YTD, Volatility M)
technical      |technical (e.g. Beta, SMA50, 52W Low, RSI, Change)
signals        |view filter signals (e.g. -s top_gainers)

&nbsp;

## Forex [»](forex/README.md)

Command|Description
------ | --------
summary      |display a summary of your account
calendar     |get information about past or upcoming events which may impact the price
list         |list your order history
pending      |get information about pending orders
cancel       |cancel a pending order by ID
positions    |get information about your positions
trades       |see a list of open trades
closetrade   |close a trade by ID
load         |specify an instrument to use
candles      |get a candlestick chart for the forex instrument
price        |show the current price for the forex instrument
order        |place a limit order
orderbook    |display the orderbook if Oanda provides one for the forex instrument
positionbook |display the positionbook if Oanda provides one for the forex instrument

&nbsp;

## Backtesting [»](backtesting/README.md)

Command|Description
------ | --------
`ema`           | buy when price exceeds EMA(l)
`ema_cross`     | buy when EMA(short) > EMA(long)
`rsi`           | buy when RSI < low and sell when RSI > high

## Resource Collection [»](resource_collection/README.md)

Command|Website
----|----
`hfletters`     |<https://miltonfmr.com/hedge-fund-letters/>
`arxiv`         |<https://arxiv.org>
`finra`         |<https://www.finra.org/#/>
`edgar`         |<https://www.sec.gov/edgar.shtml>
`fred`          |<https://fred.stlouisfed.org>
`learn`         |<https://moongangcapital.com/free-stock-market-resources/>

&nbsp;


## Government [»](government/README.md)
Command|Website
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
with ticker provided    |
`raw_congress`          | raw congress trades on the ticker
`congress`              | plot congress trades on the ticker
`raw_senate`            | raw senate trades on the ticker
`senate`                | plot senate trades on the ticker
`raw_house`             | raw house trades on the ticker
`house`                 | plot house trades on the ticker
`raw_contracts`         | raw contracts on the ticker
`contracts`             | plot sum of contracts on the ticker

&nbsp;

## ETF [»](etf/README.md)
command|description
---|----
`web`|open webbroswer to stockanalysis.com
`search`|search for ETFs matching an input
`overview`|get ETF overview
`holdings`|show ETF holdings
`compare`|compare multiple ETFs overview
`screener`|screen ETFs
`gainers`|show top gainers
`decliners`|show top decliners
`active`|show most active
