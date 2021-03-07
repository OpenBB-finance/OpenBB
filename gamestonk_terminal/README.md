# Features 📈

### Table of contents
* [Discover Stocks](#Discover-Stocks-)
* [Market Sentiment](#Market-Sentiment-)
* [Research Web pages](#Research-Web-pages)
* [Fundamental Analysis](#Fundamental-Analysis-)
* [Technical Analysis](#Technical-Analysis-)
* [Due Diligence](#Due-Diligence-)
* [Prediction Techniques](#Prediction-Techniques-)

## Main

The main menu allows the following commands:
```
load -t S_TICKER [-s S_START_DATE] [-i {1,5,15,30,60}]
```
   * Load stock ticker to perform analysis on
     * -s : The starting date (format YYYY-MM-DD) of the stock
     * -i : Intraday stock minutes

**Note:** Until a ticker is loaded, the menu will only show *disc* and *sen* menu, as the others require a ticker being provided.

```
clear
```
   * Clear previously loaded stock ticker.
```
view -t S_TICKER [-s S_START_DATE] [-i {1,5,15,30,60}] [--type N_TYPE]
```
   * Visualise historical data of a stock. An alpha_vantage key is necessary.
     * -s : The starting date (format YYYY-MM-DD) of the stock
     * -i : Intraday stock minutes
     * --type : 1234 corresponds to types: 1. open; 2. high; 3.low; 4. close; while 14 corresponds to types: 1.open; 4. close

![GNUS](https://user-images.githubusercontent.com/25267873/108925137-f2920e80-7633-11eb-8274-6e3bb6a19592.png)

```
export -f GNUS_data -F csv
```
   * Exports the historical data from this ticker to a file or stdout.
     * -f : Name of file to save the historical data exported (stdout if unspecified). Default: stdout.
     * -F : Export historical data into following formats: csv, json, excel, clipboard. Default: csv.


## Discover Stocks [»](discovery/README.md)
Command|Description|Source
---|---|---
`map`           |S&P500 index stocks map |[Finviz](https://finviz.com)
`sectors`       |show sectors performance |[Alpha Vantage](www.alphavantage.co)
`gainers`       |show latest top gainers |[Yahoo Finance](https://finance.yahoo.com/)
`orders`        |orders by Fidelity Customers |[Fidelity](https://www.fidelity.com/)
`up_earnings`   |upcoming earnings release dates |[Seeking Alpha](https://seekingalpha.com/)
`high_short`    |show top high short interest stocks of over 20% ratio |[High Short Interest](https://www.highshortinterest.com/)
`low_float`     |show low float stocks under 10M shares float |[Low Float](https://www.lowfloat.com/)
`simply_wallst` |Simply Wall St. research data |[Simply Wall St.](https://simplywall.st/about)
`spachero`      |great website for SPACs research |[SpacHero](https://www.spachero.com/)
`uwhales`       |good website for SPACs research |[UnusualWhales](https://unusualwhales.com/)

&nbsp;

## Market Sentiment [»](sentiment/README.md)
Command|Description
----|----
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

## Research Web pages
Command|Website
----|----
`macroaxis`         |www.macroaxis.com
`yahoo`             |www.finance.yahoo.com
`finviz`            |www.finviz.com
`marketwatch`       |www.marketwatch.com
`fool`              |www.fool.com
`businessinsider`   |www.markets.businessinsider.com
`fmp`               |www.financialmodelingprep.com
`fidelity`          |www.eresearch.fidelity.com
`tradingview`       |www.tradingview.com
`marketchameleon`   |www.marketchameleon.com
`stockrow`          |www.stockrow.com
`barchart`          |www.barchart.com
`grufity`           |www.grufity.com
`fintel`            |www.fintel.com
`zacks`             |www.zacks.com
`macrotrends`       |www.macrotrends.net
`newsfilter`        |www.newsfilter.io
`resources`         |www.tradinganalysisresources.com

&nbsp;

### Fundamental Analysis [»](fundamental_analysis/README.md)

Command|Description
----- | ---------
`screener`      |screen info about the company ([Finviz](https://finviz.com/))
`mgmt`          |management team of the company ([Business Insider](https://markets.businessinsider.com/))
[Market Watch API](https://markets.businessinsider.com/) |
`income`        |income statement of the company
`assets`        |assets of the company
`liabilities`   |liabilities and shareholders equity of the company
`operating`     |cash flow operating activities of the company
`investing`     |cash flow investing activities of the company
`financing`     |cash flow financing activities of the company
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
`inc`           |income statements of the company
`bal`           |balance sheet of the company
`cashf`         |cash flow of the company
`metrics`       |key metrics of the company
`ratios`        |financial ratios of the company
`growth`        |financial statement growth of the company

&nbsp;

## Technical Analysis [»](technical_analysis/README.md)
Command | Description | Sources
------ | ------ | ------
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
Command|Explanation|Source
------ | --------|----
`news`          |latest news of the company |[Finviz](https://finviz.com/)
`red`           |gets due diligence from another user's post |[Reddit](https://reddit.com)
`analyst`       |analyst prices and ratings of the company |[Finviz](https://finviz.com/)
`rating`        |rating of the company from strong sell to strong buy | [FMP](https://financialmodelingprep.com/)
`pt`            |price targets over time |[Business Insider](https://www.businessinsider.com/)
`est`           |quarter and year analysts earnings estimates |[Business Insider](https://www.businessinsider.com/)
`ins`           |insider activity over time |[Business Insider](https://www.businessinsider.com/)
`insider`       |insider trading of the company |[Finviz](https://finviz.com/)
`sec`           |SEC filings |[MarketWatch](https://www.marketwatch.com/)
`short`         |short interest |[Quandl](https://www.quandl.com/)
`warnings`      |company warnings according to Sean Seah book |[MarketWatch](https://www.marketwatch.com/)

&nbsp;

## Prediction Techniques [»](prediction_techniques/README.md)
Command|Technique|Sources
------ | ------------|---
`sma`         |simple moving average | [Wikipedia](https://en.wikipedia.org/wiki/Moving_average#Simple_moving_average), [Investopedia](https://www.investopedia.com/terms/s/sma.asp)
`knn`         |k-Nearest Neighbors | [Wikipedia](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm)
`linear`      |linear regression (polynomial 1) | [Wikipedia](https://en.wikipedia.org/wiki/Linear_regression), [Investopedia](https://www.investopedia.com/terms/r/regression.asp)
`quadratic`   |quadratic regression (polynomial 2) | [Wikipedia](https://en.wikipedia.org/wiki/Polynomial_regression), [Investopedia](https://www.investopedia.com/terms/r/regression.asp)
`cubic`       |cubic regression (polynomial 3) | [Wikipedia](https://en.wikipedia.org/wiki/Polynomial_regression), [Investopedia](https://www.investopedia.com/terms/r/regression.asp)
`regression`  |regression (other polynomial) | [Wikipedia](https://en.wikipedia.org/wiki/Polynomial_regression), [Investopedia](https://www.investopedia.com/terms/r/regression.asp)
`arima`       |autoregressive integrated moving average | [Wikipedia](https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average), [Investopedia](https://www.investopedia.com/terms/a/autoregressive-integrated-moving-average-arima.asp)
`prophet`     |Facebook's prophet prediction | [Details](https://facebook.github.io/prophet/)
`mlp`         |MultiLayer Perceptron | [Wikipedia](https://en.wikipedia.org/wiki/Multilayer_perceptron)
`rnn`         |Recurrent Neural Network  | [Wikipedia](https://en.wikipedia.org/wiki/Recurrent_neural_network)
`lstm`        |Long Short-Term Memory  | [Wikipedia](https://en.wikipedia.org/wiki/Long_short-term_memory), [Details](https://colah.github.io/posts/2015-08-Understanding-LSTMs/)
