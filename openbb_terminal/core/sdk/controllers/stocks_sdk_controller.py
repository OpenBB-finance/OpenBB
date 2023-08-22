# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.models import stocks_sdk_model as model


class StocksController(model.StocksRoot):
    """Stocks Module.

    Submodules:
        `ba`: Behavioral Analysis Module
        `ca`: Comparison Analysis Module
        `disc`: Discovery Module
        `dps`: Darkpool Shorts Module
        `fa`: Fundamental Analysis Module
        `gov`: Government Module
        `ins`: Insiders Module
        `options`: Options Module
        `qa`: Quantitative Analysis Module
        `screener`: Screener Module
        `ta`: Technical Analysis Module
        `th`: Trading Hours Module

    Attributes:
        `candle`: Show candle plot of loaded ticker.\n
        `load`: Load a symbol to perform analysis using the string above as a template.\n
        `news`: Get news for a given term and source. [Source: Ultima Insights News Monitor]\n
        `process_candle`: Process DataFrame into candle style plot.\n
        `quote`: Gets ticker quote from FMP\n
        `quote_chart`: Financial Modeling Prep ticker(s) quote.\n
        `search`: Search selected query for tickers.\n
        `tob`: Get top of book bid and ask for ticker on exchange [CBOE.com]\n
    """

    @property
    def ba(self):
        """Stocks Behavioral Analysis Submodule

        Attributes:
            `bullbear`: Gets bullbear sentiment for ticker [Source: stocktwits].\n
            `cnews`: Get news from a company. [Source: Finnhub]\n
            `getdd`: Get due diligence posts from list of subreddits [Source: reddit].\n
            `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain].\n
            `headlines_chart`: Plots Sentiment analysis from FinBrain. Prints table if raw is True. [Source: FinBrain]\n
            `mentions`: Get interest over time from google api [Source: google].\n
            `mentions_chart`: Plots weekly bars of stock's interest over time. other users watchlist. [Source: Google].\n
            `messages`: Get last messages for a given ticker [Source: stocktwits].\n
            `ns`: Getting Onclusive Data. [Source: Invisage Platform]\n
            `ns_chart`: Display Onclusive Data. [Source: Invisage Plotform]\n
            `popular`: Get popular tickers from list of subreddits [Source: reddit].\n
            `queries`: Get related queries from google api [Source: google].\n
            `redditsent`: Find posts related to a specific search term in Reddit.\n
            `regions`: Get interest by region from google api [Source: google].\n
            `regions_chart`: Plots bars of regions based on stock's interest. [Source: Google].\n
            `rise`: Get top rising related queries with this stock's query [Source: google].\n
            `snews`: Get headlines sentiment using VADER model over time. [Source: Finnhub]\n
            `snews_chart`: Display stock price and headlines sentiment using VADER model over time. [Source: Finnhub]\n
            `stalker`: Gets messages from given user [Source: stocktwits].\n
            `text_sent`: Find the sentiment of a post and related comments.\n
            `trending`: Get trending tickers from stocktwits [Source: stocktwits].\n
            `wsb`: Get wsb posts [Source: reddit].\n
        """

        return model.StocksBehavioralAnalysis()

    @property
    def ca(self):
        """Stocks Comparison Analysis Submodule

        Attributes:
            `balance`: Get balance data. [Source: Marketwatch].\n
            `cashflow`: Get cashflow data. [Source: Marketwatch]\n
            `hcorr`: Get historical price correlation. [Source: Yahoo Finance]\n
            `hcorr_chart`: Correlation heatmap based on historical price comparison\n
            `hist`: Get historical prices for all comparison stocks\n
            `hist_chart`: Display historical stock prices. [Source: Yahoo Finance]\n
            `income`: Get income data. [Source: Marketwatch].\n
            `income_chart`: Display income data. [Source: Marketwatch].\n
            `scorr`: Get correlation sentiments across similar companies. [Source: FinBrain].\n
            `scorr_chart`: Plot correlation sentiments heatmap across similar companies. [Source: FinBrain].\n
            `screener`: Screener Overview.\n
            `sentiment`: Gets Sentiment analysis from several symbols provided by FinBrain's API.\n
            `sentiment_chart`: Display sentiment for all ticker. [Source: FinBrain].\n
            `similar`: Find similar tickers to a given symbol.\n
            `volume`: Get stock volume. [Source: Yahoo Finance]\n
            `volume_chart`: Display stock volume. [Source: Yahoo Finance]\n
        """

        return model.StocksComparisonAnalysis()

    @property
    def disc(self):
        """Stocks Discovery Submodule

        Attributes:
            `active`: Get stocks ordered in descending order by intraday trade volume. [Source: Yahoo Finance]\n
            `arkord`: Returns ARK orders in a Dataframe\n
            `asc`: Get Yahoo Finance small cap stocks with earnings growth rates better than 25%.\n
            `dividends`: Gets dividend calendar for given date.  Date represents Ex-Dividend Date\n
            `filings`: Get SEC Filings RSS feed, disseminated by FMP\n
            `filings_chart`: Display recent forms submitted to the SEC\n
            `fipo`: Future IPOs dates. [Source: Finnhub]\n
            `gainers`: Get top gainers. [Source: Yahoo Finance]\n
            `gtech`: Get technology stocks with revenue and earnings growth in excess of 25%. [Source: Yahoo Finance]\n
            `hotpenny`: Returns today hot penny stocks\n
            `ipo`: Get IPO calendar\n
            `losers`: Get top losers. [Source: Yahoo Finance]\n
            `lowfloat`: Returns low float DataFrame\n
            `pipo`: Past IPOs dates. [Source: Finnhub]\n
            `rtat`: Gets the top 10 retail stocks per day\n
            `trending`: Returns a list of trending articles\n
            `ugs`: Get stocks with earnings growth rates better than 25% and relatively low PE and PEG ratios.\n
            `ulc`: Get Yahoo Finance potentially undervalued large cap stocks.\n
            `upcoming`: Returns a DataFrame with upcoming earnings\n
        """

        return model.StocksDiscovery()

    @property
    def dps(self):
        """Stocks Darkpool Shorts Submodule

        Attributes:
            `ctb`: Get stocks with highest cost to borrow [Source: Interactive Broker]\n
            `dpotc`: Get all FINRA data associated with a ticker\n
            `dpotc_chart`: Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]\n
            `ftd`: Display fails-to-deliver data for a given ticker. [Source: SEC]\n
            `ftd_chart`: Display fails-to-deliver data for a given ticker. [Source: SEC]\n
            `hsi`: Returns a high short interest DataFrame\n
            `pos`: Get dark pool short positions. [Source: Stockgrid]\n
            `prom`: Get all FINRA ATS data, and parse most promising tickers based on linear regression\n
            `prom_chart`: Display dark pool (ATS) data of tickers with growing trades activity. [Source: FINRA]\n
            `psi_q`: Plots the short interest of a stock. This corresponds to the\n
            `psi_q_chart`: Plot the short interest of a stock. This corresponds to the\n
            `psi_sg`: Get price vs short interest volume. [Source: Stockgrid]\n
            `psi_sg_chart`: Plot price vs short interest volume. [Source: Stockgrid]\n
            `shorted`: Get most shorted stock screener [Source: Yahoo Finance]\n
            `sidtc`: Get short interest and days to cover. [Source: Stockgrid]\n
            `spos`: Get net short position. [Source: Stockgrid]\n
            `spos_chart`: Plot net short position. [Source: Stockgrid]\n
        """

        return model.StocksDarkpoolShorts()

    @property
    def fa(self):
        """Stocks Fundamental Analysis Submodule

        Attributes:
            `analysis`: Save time reading SEC filings with the help of machine learning. [Source: https://eclect.us]\n
            `analyst`: Get analyst data. [Source: Finviz]\n
            `balance`: Get balance sheet.\n
            `cal`: Get calendar earnings for ticker symbol\n
            `cash`: Get Cash Flow.\n
            `customer`: Print customers from ticker provided\n
            `dcf`: Get stocks dcf from FMP\n
            `dcfc`: Get stocks dcf from FMP\n
            `divs`: Get historical dividend for ticker\n
            `divs_chart`: Display historical dividends\n
            `dupont`: Get dupont ratios\n
            `earnings`: Get earnings data.\n
            `enterprise`: Financial Modeling Prep ticker enterprise\n
            `epsfc`: Takes the ticker, asks for seekingalphaID and gets eps estimates\n
            `est`: Get analysts' estimates for a given ticker. [Source: Business Insider]\n
            `fama_coe`: Use Fama and French to get the cost of equity for a company\n
            `fama_raw`: Get Fama French data\n
            `fraud`: Get fraud ratios based on fundamentals\n
            `growth`: Get financial statement growth\n
            `historical_5`: Get 5 year monthly historical performance for a ticker with dividends filtered\n
            `income`: Get income statement.\n
            `key`: Get key metrics from overview\n
            `metrics`: Get key metrics\n
            `mgmt`: Get company managers from Business Insider\n
            `mktcap`: Get market cap over time for ticker. [Source: Yahoo Finance]\n
            `mktcap_chart`: Display market cap over time. [Source: Yahoo Finance]\n
            `news`: Get news from Finviz\n
            `overview`: Get overview.\n
            `pt`: Get analysts' price targets for a given stock. [Source: Business Insider]\n
            `pt_chart`: Display analysts' price targets for a given stock. [Source: Business Insider]\n
            `rating`: Get ratings for a given ticker. [Source: Financial Modeling Prep]\n
            `ratios`: Get key ratios\n
            `revfc`: Takes the ticker, asks for seekingalphaID and gets rev estimates\n
            `rot`: Get rating over time data. [Source: Finnhub]\n
            `rot_chart`: Rating over time (monthly). [Source: Finnhub]\n
            `score`: Gets value score from fmp\n
            `sec`: Get SEC filings for a given stock ticker. [Source: Nasdaq]\n
            `shrs`: Get shareholders from yahoo\n
            `similar_dfs`: Get dataframes for similar companies\n
            `splits`: Get splits and reverse splits events. [Source: Yahoo Finance]\n
            `splits_chart`: Display splits and reverse splits events. [Source: Yahoo Finance]\n
            `supplier`: Get suppliers from ticker provided. [Source: CSIMarket]\n
        """

        return model.StocksFundamentalAnalysis()

    @property
    def gov(self):
        """Stocks Government Submodule

        Attributes:
            `contracts`: Get government contracts for ticker [Source: quiverquant.com]\n
            `contracts_chart`: Show government contracts for ticker [Source: quiverquant.com]\n
            `government_trading`: Returns the most recent transactions by members of government\n
            `gtrades`: Government trading for specific ticker [Source: quiverquant.com]\n
            `gtrades_chart`: Government trading for specific ticker [Source: quiverquant.com]\n
            `histcont`: Get historical quarterly government contracts [Source: quiverquant.com]\n
            `histcont_chart`: Show historical quarterly government contracts [Source: quiverquant.com]\n
            `lastcontracts`: Get last government contracts [Source: quiverquant.com]\n
            `lastcontracts_chart`: Last government contracts [Source: quiverquant.com]\n
            `lasttrades`: Get last government trading [Source: quiverquant.com]\n
            `lobbying`: Corporate lobbying details\n
            `qtrcontracts`: Analyzes quarterly contracts by ticker\n
            `qtrcontracts_chart`: Quarterly contracts [Source: quiverquant.com]\n
            `topbuys`: Get top buy government trading [Source: quiverquant.com]\n
            `topbuys_chart`: Top buy government trading [Source: quiverquant.com]\n
            `toplobbying`: Corporate lobbying details\n
            `toplobbying_chart`: Top lobbying tickers based on total spent\n
            `topsells`: Get top sell government trading [Source: quiverquant.com]\n
            `topsells_chart`: Top sell government trading [Source: quiverquant.com]\n
        """

        return model.StocksGovernment()

    @property
    def ins(self):
        """Stocks Insiders Submodule

        Attributes:
            `act`: Get insider activity. [Source: Business Insider]\n
            `act_chart`: Display insider activity. [Source: Business Insider]\n
            `blcp`: Get latest CEO/CFO purchases > 25k\n
            `blcs`: Get latest CEO/CFO sales > 100k\n
            `blip`: Get latest insider purchases > 25k\n
            `blis`: Get latest insider sales > 100k\n
            `blop`: Get latest officer purchases > 25k\n
            `blos`: Get latest officer sales > 100k\n
            `filter`: GEt insider trades based on preset filter\n
            `lcb`: Get latest cluster buys\n
            `lins`: Get last insider activity for a given stock ticker. [Source: Finviz]\n
            `lins_chart`: Display insider activity for a given stock ticker. [Source: Finviz]\n
            `lip`: Get latest insider purchases\n
            `lis`: Get latest insider sales\n
            `lit`: Get latest insider trades\n
            `lpsb`: Get latest penny stock buys\n
            `print_insider_data`: Print insider data\n
            `print_insider_data_chart`: Print insider data\n
            `stats`: Get OpenInsider stats for ticker\n
        """

        return model.StocksInsiders()

    @property
    def options(self):
        """Stocks Options Submodule

        Attributes:
            `chains`: Get Option Chain For A Stock.  No greek data is returned\n
            `dte`: Returns a new column containing the DTE as an integer, including 0.\n
            `eodchain`: Get full EOD option date across all expirations\n
            `expirations`: Get Option Chain Expirations\n
            `generate_data`: Gets x values, and y values before and after premiums\n
            `get_strategies`: Gets options strategies for all, or a list of, DTE(s).\n
            `greeks`: Gets the greeks for a given option\n
            `grhist`: Get historical EOD option prices, with Greeks, for a given OCC chain label.\n
            `grhist_chart`: Plots historical greeks for a given option.\n
            `hist`: Get historical option pricing.\n
            `info`: Scrape barchart for options info\n
            `info_chart`: Scrapes Barchart.com for the options information\n
            `last_price`: Makes api request for last price\n
            `load_options_chains`: Loads all options chains from a specific source, fields returned to each attribute will vary.\n
            `oi`: Plot open interest\n
            `pcr`: Gets put call ratio over last time window [Source: AlphaQuery.com]\n
            `pcr_chart`: Display put call ratio [Source: AlphaQuery.com]\n
            `price`: Get Option current price for a stock.\n
            `unu`: Get unusual option activity from fdscanner.com\n
            `unu_chart`: Displays the unusual options table\n
            `voi`: Plot volume and open interest\n
            `vol`: Plot volume\n
            `vsurf`: Gets IV surface for calls and puts for ticker\n
            `vsurf_chart`: Display vol surface\n
        """

        return model.StocksOptions()

    @property
    def qa(self):
        """Stocks Quantitative Analysis Submodule

        Attributes:
            `beta`: Calculate beta for a ticker and a reference ticker.\n
            `beta_chart`: Display the beta scatterplot + linear regression.\n
            `capm`: Provides information that relates to the CAPM model\n
            `fama_raw`: Gets base Fama French data to calculate risk\n
            `historical_5`: Get 5 year monthly historical performance for a ticker with dividends filtered\n
        """

        return model.StocksQuantitativeAnalysis()

    @property
    def screener(self):
        """Stocks Screener Submodule

        Attributes:
            `screener_data`: Screener Overview\n
            `screener_data_chart`: Screener one of the following: overview, valuation, financial, ownership, performance, technical.\n
        """

        return model.StocksScreener()

    @property
    def ta(self):
        """Stocks Technical Analysis Submodule

        Attributes:
            `recom`: Get tradingview recommendation based on technical indicators\n
            `recom_chart`: Print tradingview recommendation based on technical indicators\n
            `summary`: Get technical summary report provided by FinBrain's API\n
            `summary_chart`: Print technical summary report provided by FinBrain's API\n
        """

        return model.StocksTechnicalAnalysis()

    @property
    def th(self):
        """Stocks Trading Hours Submodule

        Attributes:
            `all`: Get all exchanges.\n
            `all_chart`: Display all exchanges.\n
            `check_if_open`: Check if market open helper function\n
            `closed`: Get closed exchanges.\n
            `closed_chart`: Display closed exchanges.\n
            `exchange`: Get current exchange open hours.\n
            `exchange_chart`: Display current exchange trading hours.\n
            `open`: Get open exchanges.\n
            `open_chart`: Display open exchanges.\n
        """

        return model.StocksTradingHours()
