# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.models import stocks_sdk_model as model


class StocksController(model.StocksRoot):
    """OpenBB SDK Stocks Module.

    Submodules:
        `ba`: Behavioral Analysis Module
        `ca`: Comparison Analysis Module
        `dd`: Due Diligence Module
        `disc`: Discovery Module
        `dps`: Darkpool Shorts Module
        `fa`: Fundamental Analysis Module
        `gov`: Government Module
        `ins`: Insiders Module
        `options`: Options Module
        `qa`: Quantitative Analysis Module
        `screener`: Screener Module
        `sia`: Sector Industry Analysis Module
        `ta`: Technical Analysis Module
        `th`: Trading Hours Module

    Attributes:
        `candle`: Show candle plot of loaded ticker.\n
        `load`: Load a symbol to perform analysis using the string above as a template.\n
        `process_candle`: Process DataFrame into candle style plot.\n
        `quote`: Display quote from YahooFinance\n
        `search`: Search selected query for tickers.\n
        `tob`: Get top of book bid and ask for ticker on exchange [CBOE.com]\n
    """

    @property
    def ba(self):
        """OpenBB SDK Stocks Behavioral Analysis Submodule

        Attributes:
            `bullbear`: Gets bullbear sentiment for ticker [Source: stocktwits].\n
            `bullbear_view`: Print bullbear sentiment based on last 30 messages on the board.\n
            `getdd`: Gets due diligence posts from list of subreddits [Source: reddit].\n
            `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain].\n
            `headlines_view`: Plots Sentiment analysis from FinBrain. Prints table if raw is True. [Source: FinBrain]\n
            `hist`: Get hour-level sentiment data for the chosen symbol.\n
            `hist_view`: Display historical sentiment data of a ticker,\n
            `infer`: Load tweets from twitter API and analyzes using VADER.\n
            `infer_view`: Prints Inference sentiment from past n tweets.\n
            `mentions`: Get interest over time from google api [Source: google].\n
            `mentions_view`: Plots weekly bars of stock's interest over time. other users watchlist. [Source: Google].\n
            `messages`: Get last messages for a given ticker [Source: stocktwits].\n
            `messages_view`: Prints up to 30 of the last messages on the board. [Source: Stocktwits].\n
            `popular`: Get popular tickers from list of subreddits [Source: reddit].\n
            `popular_view`: Prints table showing latest popular tickers. [Source: Reddit].\n
            `queries`: Get related queries from google api [Source: google].\n
            `queries_view`: Prints table showing top related queries with this stock's query. [Source: Google].\n
            `redditsent`: Finds posts related to a specific search term in Reddit.\n
            `redditsent_view`: Plots Reddit sentiment about a search term. Prints table showing if display is True.\n
            `regions`: Get interest by region from google api [Source: google].\n
            `regions_view`: Plots bars of regions based on stock's interest. [Source: Google].\n
            `rise`: Get top rising related queries with this stock's query [Source: google].\n
            `rise_view`: Prints top rising related queries with this stock's query. [Source: Google].\n
            `sentiment`: Get sentiments from symbol.\n
            `sentiment_view`: Plots sentiments from symbol\n
            `spac`: Get posts containing SPAC from top subreddits [Source: reddit].\n
            `spacc`: Get top tickers from r/SPACs [Source: reddit].\n
            `stalker`: Gets messages from given user [Source: stocktwits].\n
            `text_sent`: Find the sentiment of a post and related comments.\n
            `trend`: Get sentiment data on the most talked about tickers\n
            `trend_view`: Display most talked about tickers within\n
            `trending`: Get trending tickers from stocktwits [Source: stocktwits].\n
            `watchlist`: Get reddit users watchlists [Source: reddit].\n
            `watchlist_view`: Prints other users watchlist. [Source: Reddit].\n
            `wsb`: Get wsb posts [Source: reddit].\n
        """

        return model.StocksBehavioralAnalysis()

    @property
    def ca(self):
        """OpenBB SDK Stocks Comparison Analysis Submodule

        Attributes:
            `balance`: Get balance data. [Source: Marketwatch].\n
            `cashflow`: Get cashflow data. [Source: Marketwatch]\n
            `finnhub_peers`: Get similar companies from Finhub.\n
            `finviz_peers`: Get similar companies from Finviz.\n
            `hcorr`: Get historical price correlation. [Source: Yahoo Finance]\n
            `hcorr_view`: Correlation heatmap based on historical price comparison\n
            `hist`: Get historical prices for all comparison stocks\n
            `hist_view`: Display historical stock prices. [Source: Yahoo Finance]\n
            `income`: Get income data. [Source: Marketwatch].\n
            `income_view`: Display income data. [Source: Marketwatch].\n
            `polygon_peers`: Get similar companies from Polygon\n
            `scorr`: Get correlation sentiments across similar companies. [Source: FinBrain].\n
            `scorr_view`: Plot correlation sentiments heatmap across similar companies. [Source: FinBrain].\n
            `screener`: Screener Overview.\n
            `sentiment`: Gets Sentiment analysis from several symbols provided by FinBrain's API.\n
            `sentiment_view`: Display sentiment for all ticker. [Source: FinBrain].\n
            `volume`: Get stock volume. [Source: Yahoo Finance]\n
            `volume_view`: Display stock volume. [Source: Yahoo Finance]\n
        """

        return model.StocksComparisonAnalysis()

    @property
    def dd(self):
        """OpenBB SDK Stocks Due Diligence Submodule

        Attributes:
            `analyst`: Get analyst data. [Source: Finviz]\n
            `arktrades`: Gets a dataframe of ARK trades for ticker\n
            `customer`: Print customers from ticker provided\n
            `est`: Get analysts' estimates for a given ticker. [Source: Business Insider]\n
            `news`: Get news from Finviz\n
            `pt`: Get analysts' price targets for a given stock. [Source: Business Insider]\n
            `pt_view`: Display analysts' price targets for a given stock. [Source: Business Insider]\n
            `rating`: Get ratings for a given ticker. [Source: Financial Modeling Prep]\n
            `rot`: Get rating over time data. [Source: Finnhub]\n
            `rot_view`: Rating over time (monthly). [Source: Finnhub]\n
            `sec`: Get SEC filings for a given stock ticker. [Source: Market Watch]\n
            `sec_view`: Display SEC filings for a given stock ticker. [Source: Market Watch]\n
            `supplier`: Get suppliers from ticker provided. [Source: CSIMarket]\n
        """

        return model.StocksDueDiligence()

    @property
    def disc(self):
        """OpenBB SDK Stocks Discovery Submodule

        Attributes:
            `active`: Get stocks ordered in descending order by intraday trade volume. [Source: Yahoo Finance]\n
            `arkord`: Returns ARK orders in a Dataframe\n
            `asc`: Get Yahoo Finance small cap stocks with earnings growth rates better than 25%.\n
            `dividends`: Gets dividend calendar for given date.  Date represents Ex-Dividend Date\n
            `fipo`: Future IPOs dates. [Source: Finnhub]\n
            `gainers`: Get top gainers. [Source: Yahoo Finance]\n
            `gtech`: Get technology stocks with revenue and earnings growth in excess of 25%. [Source: Yahoo Finance]\n
            `hotpenny`: Returns today hot penny stocks\n
            `ipo`: Get IPO calendar\n
            `losers`: Get top losers. [Source: Yahoo Finance]\n
            `lowfloat`: Returns low float DataFrame\n
            `news`: Gets news. [Source: SeekingAlpha]\n
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
        """OpenBB SDK Stocks Darkpool Shorts Submodule

        Attributes:
            `ctb`: Get cost to borrow of stocks [Source: Stocksera]\n
            `ctb_view`: Plot the cost to borrow of a stock. [Source: Stocksera]\n
            `dpotc`: Get all FINRA data associated with a ticker\n
            `dpotc_view`: Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]\n
            `ftd`: Display fails-to-deliver data for a given ticker. [Source: SEC]\n
            `ftd_view`: Display fails-to-deliver data for a given ticker. [Source: SEC]\n
            `hsi`: Returns a high short interest DataFrame\n
            `pos`: Get dark pool short positions. [Source: Stockgrid]\n
            `prom`: Get all FINRA ATS data, and parse most promising tickers based on linear regression\n
            `prom_view`: Display dark pool (ATS) data of tickers with growing trades activity. [Source: FINRA]\n
            `psi_q`: Plots the short interest of a stock. This corresponds to the\n
            `psi_q_view`: Plot the short interest of a stock. This corresponds to the\n
            `psi_sg`: Get price vs short interest volume. [Source: Stockgrid]\n
            `psi_sg_view`: Plot price vs short interest volume. [Source: Stockgrid]\n
            `shorted`: Get most shorted stock screener [Source: Yahoo Finance]\n
            `sidtc`: Get short interest and days to cover. [Source: Stockgrid]\n
            `spos`: Get net short position. [Source: Stockgrid]\n
            `spos_view`: Plot net short position. [Source: Stockgrid]\n
            `volexch`: Gets short data for 5 exchanges [https://ftp.nyse.com] starting at 1/1/2021\n
            `volexch_view`: Display short data by exchange\n
        """

        return model.StocksDarkpoolShorts()

    @property
    def fa(self):
        """OpenBB SDK Stocks Fundamental Analysis Submodule

        Attributes:
            `analysis`: Save time reading SEC filings with the help of machine learning. [Source: https://eclect.us]\n
            `av_balance`: Get balance sheets for company\n
            `av_cash`: Get cash flows for company\n
            `av_cash_view`: Alpha Vantage income statement\n
            `av_income`: Get income statements for company\n
            `av_metrics`: Get key metrics from overview\n
            `av_overview`: Get alpha vantage company overview\n
            `cal`: Get calendar earnings for ticker symbol\n
            `data`: Get fundamental data from finviz\n
            `dcf`: Get stocks dcf from FMP\n
            `divs`: Get historical dividend for ticker\n
            `dupont`: Get dupont ratios\n
            `earnings`: Get earnings calendar for ticker\n
            `enterprise`: Financial Modeling Prep ticker enterprise\n
            `fama_coe`: Use Fama and French to get the cost of equity for a company\n
            `fama_raw`: Get Fama French data\n
            `fmp_balance`: Get balance sheets\n
            `fmp_cash`: Get cash flow\n
            `fmp_income`: Get income statements\n
            `fmp_metrics`: Get key metrics\n
            `fmp_ratios`: Get key ratios\n
            `fraud`: Get fraud ratios based on fundamentals\n
            `growth`: Get financial statement growth\n
            `historical_5`: Get 5 year monthly historical performance for a ticker with dividends filtered\n
            `hq`: Gets google map url for headquarter\n
            `info`: Gets ticker symbol info\n
            `mgmt`: Get company managers from Business Insider\n
            `mktcap`: Get market cap over time for ticker. [Source: Yahoo Finance]\n
            `poly_financials`: Get ticker financial statements from polygon\n
            `poly_financials_view`: Display tickers balance sheet or income statement\n
            `profile`: Get ticker profile from FMP\n
            `quote`: Gets ticker quote from FMP\n
            `score`: Gets value score from fmp\n
            `shrs`: Get shareholders from yahoo\n
            `similar_dfs`: Get dataframes for similar companies\n
            `splits`: Get splits and reverse splits events. [Source: Yahoo Finance]\n
            `splits_view`: Display splits and reverse splits events. [Source: Yahoo Finance]\n
            `sust`: Get sustainability metrics from yahoo\n
            `website`: Gets website of company from yfinance\n
            `yf_financials`: Get cashflow statement for company\n
            `yf_financials_view`: Display tickers balance sheet, income statement or cash-flow\n
        """

        return model.StocksFundamentalAnalysis()

    @property
    def gov(self):
        """OpenBB SDK Stocks Government Submodule

        Attributes:
            `contracts`: Get government contracts for ticker [Source: quiverquant.com]\n
            `contracts_view`: Show government contracts for ticker [Source: quiverquant.com]\n
            `government_trading`: Returns the most recent transactions by members of government\n
            `gtrades`: Government trading for specific ticker [Source: quiverquant.com]\n
            `gtrades_view`: Government trading for specific ticker [Source: quiverquant.com]\n
            `histcont`: Get historical quarterly government contracts [Source: quiverquant.com]\n
            `histcont_view`: Show historical quarterly government contracts [Source: quiverquant.com]\n
            `lastcontracts`: Get last government contracts [Source: quiverquant.com]\n
            `lastcontracts_view`: Last government contracts [Source: quiverquant.com]\n
            `lasttrades`: Get last government trading [Source: quiverquant.com]\n
            `lobbying`: Corporate lobbying details\n
            `qtrcontracts`: Analyzes quarterly contracts by ticker\n
            `qtrcontracts_view`: Quarterly contracts [Source: quiverquant.com]\n
            `topbuys`: Get top buy government trading [Source: quiverquant.com]\n
            `topbuys_view`: Top buy government trading [Source: quiverquant.com]\n
            `toplobbying`: Corporate lobbying details\n
            `toplobbying_view`: Top lobbying tickers based on total spent\n
            `topsells`: Get top sell government trading [Source: quiverquant.com]\n
            `topsells_view`: Top sell government trading [Source: quiverquant.com]\n
        """

        return model.StocksGovernment()

    @property
    def ins(self):
        """OpenBB SDK Stocks Insiders Submodule

        Attributes:
            `act`: Get insider activity. [Source: Business Insider]\n
            `act_view`: Display insider activity. [Source: Business Insider]\n
            `lins`: Get last insider activity for a given stock ticker. [Source: Finviz]\n
            `lins_view`: Display insider activity for a given stock ticker. [Source: Finviz]\n
            `print_insider_data`: Print insider data\n
            `print_insider_data_view`: Print insider data\n
        """

        return model.StocksInsiders()

    @property
    def options(self):
        """OpenBB SDK Stocks Options Submodule

        Submodules:
            `hedge`: Hedge Module
            `screen`: Screen Module

        Attributes:
            `chains_nasdaq`: Get option chain for symbol at a given expiration\n
            `chains_nasdaq_view`: Display option chain for given expiration\n
            `chains_tr`: Display option chains [Source: Tradier]"\n
            `chains_tr_view`: Display option chain\n
            `chains_yf`: Gets option chain from yf for given ticker and expiration\n
            `chains_yf_view`: Display option chains for given ticker and expiration\n
            `closing`: Get closing prices for a given ticker\n
            `dividend`: Gets option chain from yf for given ticker and expiration\n
            `dte`: Gets days to expiration from yfinance option date\n
            `generate_data`: Gets x values, and y values before and after premiums\n
            `grhist`: Get histoical option greeks\n
            `grhist_view`: Plots historical greeks for a given option. [Source: Syncretism]\n
            `hist_ce`: Historic prices for a specific option [chartexchange]\n
            `hist_ce_view`: Return raw stock data[chartexchange]\n
            `hist_tr`: Gets historical option pricing.  This inputs either ticker, expiration, strike or the OCC chain ID and processes\n
            `hist_tr_view`: Plot historical option prices\n
            `info`: Get info for a given ticker\n
            `info_view`: Scrapes Barchart.com for the options information\n
            `last_price`: Makes api request for last price\n
            `option_chain`: Gets option chain from yf for given ticker and expiration\n
            `option_expirations`: Get available expiration dates for given ticker\n
            `pcr`: Gets put call ratio over last time window [Source: AlphaQuery.com]\n
            `pcr_view`: Display put call ratio [Source: AlphaQuery.com]\n
            `price`: Get current price for a given ticker\n
            `process_chains`: Function to take in the requests.get and return a DataFrame\n
            `unu`: Get unusual option activity from fdscanner.com\n
            `unu_view`: Displays the unusual options table\n
            `voi_yf`: Plot volume and open interest\n
            `voi_yf_view`: Plot volume and open interest\n
            `vol_yf`: Plot volume\n
            `vol_yf_view`: Plot volume\n
            `vsurf`: Gets IV surface for calls and puts for ticker\n
            `vsurf_view`: Display vol surface\n
            `x_values`: Generates different price values that need to be tested\n
            `y_values`: Generates y values for corresponding x values\n
        """

        return model.StocksOptions()

    @property
    def qa(self):
        """OpenBB SDK Stocks Quantitative Analysis Submodule

        Attributes:
            `capm_information`: Provides information that relates to the CAPM model\n
            `fama_raw`: Gets base Fama French data to calculate risk\n
            `historical_5`: Get 5 year monthly historical performance for a ticker with dividends filtered\n
        """

        return model.StocksQuantitativeAnalysis()

    @property
    def screener(self):
        """OpenBB SDK Stocks Screener Submodule

        Attributes:
            `historical`: View historical price of stocks that meet preset\n
            `historical_view`: View historical price of stocks that meet preset\n
            `screener_view`: Screener one of the following: overview, valuation, financial, ownership, performance, technical.\n
            `screener_data`: Screener Overview\n
        """

        return model.StocksScreener()

    @property
    def sia(self):
        """OpenBB SDK Stocks Sector Industry Analysis Submodule

        Attributes:
            `countries`: Get all countries in Yahoo Finance data based on sector or industry. [Source: Finance Database]\n
            `cpci`: Get number of companies per country in a specific industry (and specific market cap).\n
            `cpci_view`: Display number of companies per country in a specific industry. [Source: Finance Database]\n
            `cpcs`: Get number of companies per country in a specific sector (and specific market cap).\n
            `cpcs_view`: Display number of companies per country in a specific sector. [Source: Finance Database]\n
            `cpic`: Get number of companies per industry in a specific country (and specific market cap).\n
            `cpic_view`: Display number of companies per industry in a specific country. [Source: Finance Database]\n
            `cpis`: Get number of companies per industry in a specific sector (and specific market cap).\n
            `cpis_view`: Display number of companies per industry in a specific sector. [Source: Finance Database]\n
            `cps`: Get number of companies per sector in a specific country (and specific market cap). [Source: Finance Database]\n
            `cps_view`: Display number of companies per sector in a specific country (and market cap). [Source: Finance Database]\n
            `filter_stocks`: Filter stocks based on country, sector, industry, market cap and exclude exchanges.\n
            `industries`: Get all industries in Yahoo Finance data based on country or sector. [Source: Finance Database]\n
            `marketcap`: Get all market cap division in Yahoo Finance data. [Source: Finance Database]\n
            `sectors`: Get all sectors in Yahoo Finance data based on country or industry. [Source: Finance Database]\n
            `stocks_data`: Get stocks data based on a list of stocks and the finance key. The function searches for the\n
        """

        return model.StocksSectorIndustryAnalysis()

    @property
    def ta(self):
        """OpenBB SDK Stocks Technical Analysis Submodule

        Attributes:
            `recom`: Get tradingview recommendation based on technical indicators\n
            `summary`: Get technical summary report provided by FinBrain's API\n
            `view`: Get finviz image for given ticker\n
        """

        return model.StocksTechnicalAnalysis()

    @property
    def th(self):
        """OpenBB SDK Stocks Trading Hours Submodule

        Attributes:
            `all`: Get all exchanges.\n
            `all_view`: Display all exchanges.\n
            `check_if_open`: Check if market open helper function\n
            `closed`: Get closed exchanges.\n
            `closed_view`: Display closed exchanges.\n
            `exchange`: Get current exchange open hours.\n
            `exchange_view`: Display current exchange trading hours.\n
            `open`: Get open exchanges.\n
            `open_view`: Display open exchanges.\n
        """

        return model.StocksTradingHours()
