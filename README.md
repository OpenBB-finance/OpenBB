# GamestonkTerminal 🚀

## About

Gamestonk Terminal is an awesome stock market terminal that has been developed for fun, while I saw my GME shares tanking. But hey, I like the stock 💎🙌.

The implementation (in python) allows to easily add more commands, and expand on their configuration.

Feel free to request features, I'll be happy to work on them on my spare time.

## Table of contents

* [Features](#Features)
  * [Discover Stocks](#Discover_Stocks)
  * [Market Sentiment](#Market_Sentiment)
  * [Research Web pages](#Research_Web_pages)
  * [Fundamental Analysis](#Fundamental_Analysis)
  * [Technical Analysis](#Technical_Analysis)
  * [Due Diligence](#Due_Diligence)
  * [Prediction Techniques](#Prediction_Techniques)
* [Install](#Install)
* [API Keys](#API_Keys)
* [Disclaimer](#Disclaimer)
* [Support](#Support)

## Features <a name="Features"></a>

The main menu allows the following commands:
```
load -t S_TICKER [-s S_START_DATE] [-i {1,5,15,30,60}]
```
   * Load stock ticker to perform analysis on
     * -s : The starting date (format YYYY-MM-DD) of the stock
     * -i : Intraday stock minutes 
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

Note: Until a ticker is loaded, the menu will only show *disc* and *sen* menu, as the others require a ticker being provided.

### [Discover Stocks](discovery/README.md) <a name="Discover_Stocks"></a>
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


### [Market Sentiment](sentiment/README.md) <a name="Market_Sentiment"></a>
Command|Description
----|----
[Reddit](https://reddit.com):| 
`wsb`           |show what WSB gang is up to in subreddit wallstreetbets
`watchlist`     |show other users watchlist
`popular`       |show popular tickers
`spac_c`        |show other users spacs announcements from subreddit SPACs community
`spac`          |show other users spacs announcements from other subs
[Stocktwits](https://stocktwits.com/):| 
`bullbear`      |estimate quick sentiment from last 30 messages on board
`messages`      |output up to the 30 last messages on the board
`trending`      |trending stocks
`stalker`       |stalk stocktwits user's last message
[Twitter](https://twitter.com/):| 
`infer`         |infer about stock's sentiment from latest tweets
`sentiment`     |in-depth sentiment prediction from tweets over time
[Google](https://google.com/):|
`mentions`      |interest over time based on stock's mentions
`regions`       |regions that show highest interest in stock
`queries`       |top related queries with this stock
`rise`          |top rising related queries with stock

### Research Web pages <a name="Research_Web_pages"></a>
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


### [Fundamental Analysis](fundamental_analysis/README.md) <a name="Fundamental_Analysis"></a>

Command|Description
----- | ---------
`screener`      |screen info about the company ([Finviz](https://finviz.com/))
`mgmt`          |management team of the company ([Business Insider](https://www.businessinsider.com/))
Market Watch API | 
`income`        |income statement of the company
`assets`        |assets of the company
`liabilities`   |liabilities and shareholders equity of the company
`operating`     |cash flow operating activities of the company
`investing`     |cash flow investing activities of the company
`financing`     |cash flow financing activities of the company
Yahoo Finance API | 
`info`          |information scope of the company
`shrs`          |shareholders of the company
`sust`          |sustainability values of the company
`cal`           |calendar earnings and estimates of the company
Alpha Vantage API | 
`overview`      |overview of the company
`income`        |income statements of the company
`balance`       |balance sheet of the company
`cash`          |cash flow of the company
`earnings`      |earnings dates and reported EPS
Financial Modeling Prep API | 
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


### [Technical Analysis](technical_analysis/README.md) <a name="Technical_Analysis"></a>
Command | Description | Wikipedia | Investopedia
------ | ------ | ------ | -----
overlap: | 
`ema`         | exponential moving average | [Link](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average) | [Link](https://www.investopedia.com/terms/e/ema.asp)
`sma`         |simple moving average | [Link](https://en.wikipedia.org/wiki/Moving_average#Simple_moving_average_(boxcar_filter))| [Link](https://www.investopedia.com/terms/s/sma.asp)
`vwap`        |volume weighted average price | [Link](https://en.wikipedia.org/wiki/Volume-weighted_average_price)| [Link](https://www.investopedia.com/terms/v/vwap.asp)
momentum: | 
`cci`         |commodity channel index | [Link](https://en.wikipedia.org/wiki/Commodity_channel_index)| [Link](https://www.investopedia.com/terms/c/commoditychannelindex.asp)
`macd`        |moving average convergence/divergence | [Link](https://en.wikipedia.org/wiki/MACD)| [Link](https://www.investopedia.com/terms/m/macd.asp)
`rsi`         |relative strength index | [Link](https://en.wikipedia.org/wiki/Relative_strength_index)| [Link](https://www.investopedia.com/terms/r/rsi.asp)
`stoch`       |stochastic oscillator | [Link](https://en.wikipedia.org/wiki/Stochastic_oscillator)| [Link](https://www.investopedia.com/terms/s/stochasticoscillator.asp)
trend:
`adx`         |average directional movement index | [Link](https://en.wikipedia.org/wiki/Average_directional_movement_index)| [Link](https://www.investopedia.com/terms/a/adx.asp)
`aroon`       |aroon indicator | [Link](https://www.investopedia.com/terms/a/aroon.asp)
volatility: | 
`bbands`      |bollinger bands | [Link](https://en.wikipedia.org/wiki/Bollinger_Bands)| [Link](https://www.investopedia.com/terms/b/bollingerbands.asp)
volume: | 
`ad`          |chaikin accumulation/distribution line values | [Link](https://en.wikipedia.org/wiki/Accumulation/distribution_index)| [Link](https://www.investopedia.com/terms/a/accumulationdistribution.asp)
`obv`         |on balance volume | [Link](https://en.wikipedia.org/wiki/On-balance_volume)| [Link](https://www.investopedia.com/terms/o/onbalancevolume.asp)

### [Due Diligence](due_diligence/README.md) <a name="Due_Diligence"></a>
Command|Explanation
------ | --------
`news`          |latest news of the company ([Finviz](https://finviz.com/))
`red`           |gets due diligence from another user's post ([Reddit](https://reddit.com))
`analyst`       |analyst prices and ratings of the company ([Finviz](https://finviz.com/))
`rating`        |rating of the company from strong sell to strong buy [FMP]
`pt`            |price targets over time ([Business Insider](https://www.businessinsider.com/))
`est`           |quarter and year analysts earnings estimates ([Business Insider](https://www.businessinsider.com/))
`ins`           |insider activity over time ([Business Insider](https://www.businessinsider.com/))
`insider`       |insider trading of the company ([Finviz](https://finviz.com/))
`sec`           |SEC filings ([MarketWatch](https://www.marketwatch.com/))
`short`         |short interest ([Quandl](https://www.quandl.com/))
`warnings`      |company warnings according to Sean Seah book ([MarketWatch](https://www.marketwatch.com/))


### [Prediction Techniques](prediction_techniques/README.md) <a name="Prediction_Techniques"></a>
Command|Algorithm
------ | ----------
`sma`         |simple moving average | [Link](https://en.wikipedia.org/wiki/Moving_average#Simple_moving_average)| [Link](https://www.investopedia.com/terms/s/sma.asp)
`knn`         |k-Nearest Neighbors | [Link](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm))
`linear`      |linear regression (polynomial 1) | [Link](https://en.wikipedia.org/wiki/Linear_regression)| [Link](https://www.investopedia.com/terms/r/regression.asp)
`quadratic`   |quadratic regression (polynomial 2) | [Link](https://en.wikipedia.org/wiki/Polynomial_regression)| [Link](https://www.investopedia.com/terms/r/regression.asp)
`cubic`       |cubic regression (polynomial 3) | [Link](https://en.wikipedia.org/wiki/Polynomial_regression)| [Link](https://www.investopedia.com/terms/r/regression.asp)
`regression`  |regression (other polynomial) | [Link](https://en.wikipedia.org/wiki/Polynomial_regression)| [Link](https://www.investopedia.com/terms/r/regression.asp)
`arima`       |autoregressive integrated moving average | [Link](https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average)| [Link](https://www.investopedia.com/terms/a/autoregressive-integrated-moving-average-arima.asp) 
`prophet`     |Facebook's prophet prediction] | [Link](https://facebook.github.io/prophet/))
`mlp`         |MultiLayer Perceptron | [Link](https://en.wikipedia.org/wiki/Multilayer_perceptron))
`rnn`         |Recurrent Neural Network  | [Link](https://en.wikipedia.org/wiki/Recurrent_neural_network))
`lstm`        |Long Short-Term Memory  | [Link](https://en.wikipedia.org/wiki/Long_short-term_memory))


## Install <a name="Install"></a>

This project was written and tested with Python 3.6.8.

In order to install, you must run:
```
git clone https://github.com/DidierRLopes/GamestonkTerminal
cd GamestonkTerminal/
pip3 install -r requirements.txt
```
Then run:
```
python3 gamestonk_terminal.py
```

Note: The libraries specified in the [requirements.txt](/requirements.txt) file have been tested and work for the purpose of this project, however, these may be older versions. Hence, it is recommended for the user to set up a virtual python environment prior to installing these. This allows to keep dependencies required by different projects in separate places.


## API Keys <a name="API_Keys"></a>

The project is build around several different API calls, whether it is to access historical data or financials.

These are the ones where a key is necessary:
  * Alpha Vantage: https://www.alphavantage.co
  * Financial Modeling Prep: https://financialmodelingprep.com/developer
  * Quandl: https://www.quandl.com/tools/api
  * Reddit: https://www.reddit.com/prefs/apps
  * Twitter: https://developer.twitter.com

When these are obtained, don't forget to update [config_terminal.py](/config_terminal.py).  Alternatively, you can also set them to the following environment variables:  
  * GT_API_KEY_ALPHAVANTAGE
  * GT_API_KEY_FINANCIALMODELINGPREP
  * GT_API_KEY_QUANDL
  * GT_API_REDDIT_CLIENT_ID
  * GT_API_REDDIT_CLIENT_SECRET
  * GT_API_REDDIT_USERNAME
  * GT_API_REDDIT_USER_AGENT
  * GT_API_REDDIT_PASSWORD
  * GT_API_TWITTER_KEY
  * GT_API_TWITTER_SECRET_KEY
  * GT_API_TWITTER_BEARER_TOKEN.

## Disclaimer <a name="Disclaimer"></a>

"A few things I am not. I am not a cat. I am not an institutional investor, nor am I a hedge fund. I do not have clients and I do not provide personalized investment advice for fees or commissions." DFV

## Support <a name="Support"></a>

If you like this project, and would like me to maintain it and keep adding features, feel free to buy me a coffee!

<a href="https://www.buymeacoffee.com/didierlopes" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-yellow.png" alt="Buy Me A Coffee" height="41" width="174"></a>
