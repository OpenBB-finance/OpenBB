# STOCKS 📈

* [Commands](#Commands)
   * [Load](#Load)
   * [Quote](#Quote)
   * [Candle](#Candle)
   * [News](#News)
* [Discover Stocks](#Discover-Stocks-)
* [Behavioural Analysis](#Behavioural-Analysis-)
* [Research](#Research-)
* [Fundamental Analysis](#Fundamental-Analysis-)
* [Technical Analysis](#Technical-Analysis-)
* [Due Diligence](#Due-Diligence-)
* [Prediction Techniques](#Prediction-Techniques-)
* [Comparison Analysis](#Comparison-Analysis-)
* [Exploratory Data Analysis](#Exploratory-Data-Analysis-)
* [Residual Analysis](#Residual-Analysis-)
* [Screener](#Screener-)
* [Insider](#Insider-)
* [Backtesting](#Backtesting-)
* [Government](#Government-)

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


## [Discover Stocks »»](discovery/README.md)

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
`darkpool`      |dark pool tickers with growing activity |[FINRA](https://www.finra.org)
`darkshort`     |dark pool short position|[Stockgrid](https://stockgrid.io)
`shortvol`      |short interest and days to cover |[Stockgrid](https://stockgrid.io)
`popular`       |show most popular stocks on social media right now|[Sentiment Investor](https://sentimentinvestor.com)
`emerging`      |show stocks that are being talked about more than usual|[Sentiment Investor](https://sentimentinvestor.com)

&nbsp;

## [Behavioural Analysis »»](behavioural_analysis/README.md)

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
[Sentiment Investor](https://sentimentinvestor.com)|
`metrics`       |core social sentiment metrics for this stock
`social`        |social media figures for stock popularity
`historical`    |plot the past week of data for a selected metric

&nbsp;

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

## [Fundamental Analysis »»](fundamental_analysis/README.md)

Command|Description
----- | ---------
`screener`      |screen info about the company ([Finviz](https://finviz.com/))
`mgmt`          |management team of the company ([Business Insider](https://markets.businessinsider.com/))
`score`         |investing score from Warren Buffett, Joseph Piotroski and Benjamin Graham  ([FMP](https://financialmodelingprep.com/))
`dcf`           |a discounted cash flow with an option to edit in excel
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
`fraud`         |key fraud ratios
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

## [Technical Analysis »»](technical_analysis/README.md)

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
`ad`          |accumulation/distribution line values | [Wikipedia](https://en.wikipedia.org/wiki/Accumulation/distribution_index), [Investopedia](https://www.investopedia.com/terms/a/accumulationdistribution.asp)
`obv`         |on balance volume | [Wikipedia](https://en.wikipedia.org/wiki/On-balance_volume), [Investopedia](https://www.investopedia.com/terms/o/onbalancevolume.asp)
custom|
`fib`          | Fibonocci levels | [Investopedia](https://www.investopedia.com/terms/f/fibonacciretracement.asp)
&nbsp;

## [Due Diligence »»](due_diligence/README.md)

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
`dp`            |dark pools (ATS) vs OTC data | [FINRA](https://www.finra.org/#/)
`ftd`           |display fails-to-deliver data | [SEC](https://www.sec.gov)
`shortview`     |shows price vs short interest volume | [Stockgrid](https://stockgrid.io)
`darkpos`       |net short vs position | [Stockgrid](https://stockgrid.io)
`supplier`      |list of suppliers | [csimarket](https://csimarket.com)
`customer`      |list of customers | [csimarket](https://csimarket.com)

&nbsp;

## [Prediction Techniques »»](prediction_techniques/README.md)

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

## [Comparison Analysis »»](comparison_analysis/README.md)

Command|Description
------ | --------
`select`        |select similar companies
[Polygon](https://polygon.io), [Finhub](https://finnhub.io), [Finviz](https://finviz.com)|
`get`           |get similar companies
[Yahoo Finance](https://finance.yahoo.com/) |
`historical`    |historical price data comparison
`hcorr`         |historical price correlation
[MarketWatch](https://www.marketwatch.com/) |
`income`        |income financials comparison
`balance`       |balance financials comparison
`cashflow`      |cashflow comparison
[FinBrain](https://finbrain.tech) |
`sentiment`     |sentiment analysis comparison
`scorr`         |sentiment correlation
[Finviz](https://finviz.com/screener.ashx) |
`overview`        |brief overview comparison
`valuation`       |brief valuation comparison
`financial`       |brief financial comparison
`ownership`       |brief ownership comparison
`performance`     |brief performance comparison
`technical`       |brief technical comparison


&nbsp;

## [Exploratory Data Analysis »»](exploratory_data_analysis/README.md)

Command|Description
------ | --------
`summary`      | brief summary statistics
`hist`         | histogram with density plot
`cdf`          | cumulative distribution function
`bwy`          | box and whisker yearly plot
`bwm`          | box and whisker monthly plot
`rolling`      | rolling mean and std deviation
`decompose`    | decomposition in cyclic-trend, season, and residuals
`cusum`        | detects abrupt changes using cumulative sum algorithm
`acf`          | (partial) auto-correlation function differentials

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
