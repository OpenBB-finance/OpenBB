"""OpenBB Terminal SDK Stocks Controller."""
import logging

import openbb_terminal.sdk_init as lib
from openbb_terminal.sdk_modules.categories import stocks_sdk_model as model

logger = logging.getLogger(__name__)


class Stocks:
    """OpenBB SDK Stocks Module.

    Submodules:
        `ba`: Behavioral Analysis Module
        `screener`: Stocks Screener Module
        `sia`: Stocks Sentiment Analysis Module
        `qa`: Quantitative Analysis Module
        `ta`: Technical Analysis Module
    Attributes:
        `load`: Load Stock Data
        `candle`: Display Candlestick Chart
        `process_candle`: Process DataFrame into candle style plot
        `quote`: Get Ticker Quote
        `tob`: Get top of book bid and ask for ticker on exchange [CBOE.com]
        `search`: Search selected query for tickers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.load = lib.stocks_helper.load
        self.candle = lib.stocks_helper.display_candle
        self.process_candle = lib.stocks_helper.process_candle
        self.quote = lib.stocks_views.display_quote
        self.tob = lib.stocks_cboe_model.get_top_of_book
        self.search = lib.stocks_helper.search

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(\n"
            f"    ba={self.ba!r},\n"
            f"    ca={self.ca!r},\n"
            f"    dd={self.dd!r},\n"
            f"    disc={self.disc!r},\n"
            f"    dps={self.dps!r},\n"
            f"    fa={self.fa!r},\n"
            f"    options={self.options!r},\n"
            f"    qa={self.qa!r},\n"
            f"    screener={self.screener!r},\n"
            f"    sia={self.sia!r},\n"
            f"    ta={self.ta!r},\n"
            f"    th={self.th!r},\n"
            f"    load: Loads stock OHLCV data\n"
            f"    candle: Displays candlestick chart\n"
            f"    process_candle: Processes DataFrame into candle style plot\n"
            f"    quote: Gets ticker quote\n"
            f"    tob: Gets top of book bid and ask for ticker on exchange [CBOE.com]\n"
            f"    search: Searches selected query for tickers.\n)"
        )

    @property
    def ba(self):
        """Stocks Behavioral Analysis Module

        Attributes:
            `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]\n
            `headlines_view`: Sentiment analysis from FinBrain\n
            `mentions`: Get interest over time from google api [Source: google]\n
            `mentions_view`: Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]\n
            `queries`: Get related queries from google api [Source: google]\n
            `regions`: Get interest by region from google api [Source: google]\n
            `regions_view`: Plot bars of regions based on stock's interest. [Source: Google]\n
            `rise`: Get top rising related queries with this stock's query [Source: google]\n
            `rise_view`: Print top rising related queries with this stock's query. [Source: Google]\n
            `getdd`: Gets due diligence posts from list of subreddits [Source: reddit]\n
            `popular`: Get popular tickers from list of subreddits [Source: reddit]\n
            `popular_view`: Print latest popular tickers. [Source: Reddit]\n
            `redditsent`: Finds posts related to a specific search term in Reddit\n
            `redditsent_view`: Determine Reddit sentiment about a search term\n
            `text_sent`: Find the sentiment of a post and related comments\n
            `spac`: Get posts containing SPAC from top subreddits [Source: reddit]\n
            `spacc`: Get top tickers from r/SPACs [Source: reddit]\n
            `watchlist`: Get reddit users watchlists [Source: reddit]\n
            `watchlist_view`: Print other users watchlist. [Source: Reddit]\n
            `wsb`: Get wsb posts [Source: reddit]\n
            `hist`: Get hour-level sentiment data for the chosen symbol\n
            `hist_view`: Display historical sentiment data of a ticker,\n
            `trend`: Get sentiment data on the most talked about tickers\n
            `trend_view`: Display most talked about tickers within\n
            `bullbear`: Gets bullbear sentiment for ticker [Source: stocktwits]\n
            `bullbear_view`: \n
            `messages`: Get last messages for a given ticker [Source: stocktwits]\n
            `messages_view`: Print up to 30 of the last messages on the board. [Source: Stocktwits]\n
            `stalker`: Gets messages from given user [Source: stocktwits]\n
            `trending`: Get trending tickers from stocktwits [Source: stocktwits]\n
            `infer`: Load tweets from twitter API and analyzes using VADER\n
            `infer_view`: Infer sentiment from past n tweets\n
            `sentiment`: Get sentiments from symbol\n
            `sentiment_view`: Plot sentiments from symbol\n
        """
        return model.StocksBehavioralAnalysis()

    @property
    def ca(self):
        """Stocks Comparison Analysis Module

        Attributes:
            `sentiment`: Gets Sentiment analysis from several symbols provided by FinBrain's API\n
            `sentiment_view`: Display sentiment for all ticker. [Source: FinBrain]\n
            `scorr`: Get correlation sentiments across similar companies. [Source: FinBrain]\n
            `scorr_view`: Plot correlation sentiments heatmap across similar companies. [Source: FinBrain]\n
            `finnhub_peers`: Get similar companies from Finhub\n
            `screener`: Screener Overview\n
            `finviz_peers`: Get similar companies from Finviz\n
            `balance`: Get balance data. [Source: Marketwatch]\n
            `cashflow`: Get cashflow data. [Source: Marketwatch]\n
            `income`: Get income data. [Source: Marketwatch]\n
            `income_view`: Display income data. [Source: Marketwatch]\n
            `polygon_peers`: Get similar companies from Polygon\n
            `hist`: Get historical prices for all comparison stocks\n
            `hist_view`: Display historical stock prices. [Source: Yahoo Finance]\n
            `hcorr`: \n
            `hcorr_view`: \n
            `volume`: Get stock volume. [Source: Yahoo Finance]\n
            `volume_view`: Display stock volume. [Source: Yahoo Finance]\n
        """
        return model.StocksComparisonAnalysis()

    @property
    def dd(self):
        """Stocks Due Diligence Module

        Attributes:
            `arktrades`: Gets a dataframe of ARK trades for ticker\n
            `est`: Get analysts' estimates for a given ticker. [Source: Business Insider]\n
            `pt`: Get analysts' price targets for a given stock. [Source: Business Insider]\n
            `pt_view`: Display analysts' price targets for a given stock. [Source: Business Insider]\n
            `customer`: Print customers from ticker provided\n
            `supplier`: Get suppliers from ticker provided. [Source: CSIMarket]\n
            `rot`: Get rating over time data. [Source: Finnhub]\n
            `rot_view`: Rating over time (monthly). [Source: Finnhub]\n
            `analyst`: Get analyst data. [Source: Finviz]\n
            `news`: Get news from Finviz\n
            `rating`: Get ratings for a given ticker. [Source: Financial Modeling Prep]\n
            `sec`: Get SEC filings for a given stock ticker. [Source: Market Watch]\n
            `sec_view`: Display SEC filings for a given stock ticker. [Source: Market Watch]\n
        """
        return model.StocksDueDiligence()

    @property
    def disc(self):
        """Stocks Discovery Module

        Attributes:
            `arkord`: Returns ARK orders in a Dataframe\n
            `ipo`: Get IPO calendar\n
            `pipo`: Past IPOs dates. [Source: Finnhub]\n
            `fipo`: Future IPOs dates. [Source: Finnhub]\n
            `dividends`: Gets dividend calendar for given date.  Date represents Ex-Dividend Date\n
            `rtat`: Gets the top 10 retail stocks per day\n
            `news`: Gets news. [Source: SeekingAlpha]\n
            `upcoming`: Returns a DataFrame with upcoming earnings\n
            `trending`: Returns a list of trending articles\n
            `lowfloat`: Returns low float DataFrame\n
            `hotpenny`: Returns today hot penny stocks\n
            `active`: Get stocks ordered in descending order by intraday trade volume. [Source: Yahoo Finance]\n
            `asc`: Get Yahoo Finance small cap stocks with earnings growth rates better than 25%.\n
            `gainers`: Get top gainers. [Source: Yahoo Finance]\n
            `gtech`: Get technology stocks with revenue and earnings growth in excess of 25%. [Source: Yahoo Finance]\n
            `losers`: Get top losers. [Source: Yahoo Finance]\n
            `ugs`: Get stocks with earnings growth rates better than 25% and relatively low PE and PEG ratios.\n
            `ulc`: Get Yahoo Finance potentially undervalued large cap stocks.\n
        """
        return model.StocksDiscovery()

    @property
    def dps(self):
        """Stocks Darkpool Shorts Module

        Attributes:
            `prom`: Get all FINRA ATS data, and parse most promising tickers based on linear regression\n
            `prom_view`: Display dark pool (ATS) data of tickers with growing trades activity. [Source: FINRA]\n
            `dpotc`: Get all FINRA data associated with a ticker\n
            `dpotc_view`: Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]\n
            `ctb`: Get stocks with highest cost to borrow [Source: Interactive Broker]\n
            `volexch`: Gets short data for 5 exchanges [https://ftp.nyse.com] starting at 1/1/2021\n
            `volexch_view`: Display short data by exchange\n
            `psi_q`: Plots the short interest of a stock. This corresponds to the\n
            `psi_q_view`: Plots the short interest of a stock. This corresponds to the\n
            `ftd`: Display fails-to-deliver data for a given ticker. [Source: SEC]\n
            `ftd_view`: Display fails-to-deliver data for a given ticker. [Source: SEC]\n
            `hsi`: Returns a high short interest DataFrame\n
            `pos`: Get dark pool short positions. [Source: Stockgrid]\n
            `spos`: Get net short position. [Source: Stockgrid]\n
            `spos_view`: Plot net short position. [Source: Stockgrid]\n
            `sidtc`: Get short interest and days to cover. [Source: Stockgrid]\n
            `psi_sg`: Get price vs short interest volume. [Source: Stockgrid]\n
            `psi_sg_view`: Plot price vs short interest volume. [Source: Stockgrid]\n
            `shorted`: Get most shorted stock screener [Source: Yahoo Finance]\n
        """
        return model.StocksDarkPoolShorts()

    @property
    def options(self):
        """Stocks Options Module

        Submodules:
            `screen`: Options Screener Module
            `hedge`: Options Hedge Module

        Attributes:
            `pcr`: Gets put call ratio over last time window [Source: AlphaQuery.com]\n
            `pcr_view`: Display put call ratio [Source: AlphaQuery.com]\n
            `info`: Get info for a given ticker\n
            `info_view`: Scrapes Barchart.com for the options information\n
            `hist_ce`: Historic prices for a specific option [chartexchange]\n
            `hist_ce_view`: Return raw stock data[chartexchange]\n
            `unu`: Get unusual option activity from fdscanner.com\n
            `unu_view`: Displays the unusual options table\n
            `grhist`: Get histoical option greeks\n
            `grhist_view`: Plots historical greeks for a given option. [Source: Syncretism]\n
            `hist_tr`: \n
            `hist_tr_view`: Plot historical option prices\n
            `chains_tr`: Display option chains [Source: Tradier]"\n
            `chains_tr_view`: Display option chain\n
            `chains_yf`: Get full option chains with calculated greeks\n
            `chains_yf_view`: Display option chains for given ticker and expiration\n
            `last_price`: Makes api request for last price\n
            `option_expirations`: Get available expiration dates for given ticker\n
            `process_chains`: Function to take in the requests.get and return a DataFrame\n
            `generate_data`: Gets x values, and y values before and after premiums\n
            `closing`: Get closing prices for a given ticker\n
            `dividend`: Gets option chain from yf for given ticker and expiration\n
            `dte`: Gets days to expiration from yfinance option date\n
            `vsurf`: Gets IV surface for calls and puts for ticker\n
            `vsurf_view`: Display vol surface\n
            `vol_yf`: Plot volume\n
            `vol_yf_view`: Plot volume\n
            `voi_yf`: Plot volume and open interest\n
            `voi_yf_view`: Plot volume and open interest\n
            `option_chain`: Gets option chain from yf for given ticker and expiration\n
            `price`: Get current price for a given ticker\n
            `x_values`: Generates different price values that need to be tested\n
            `y_values`: Generates y values for corresponding x values\n
        """
        return model.StocksOptions()

    @property
    def qa(self):
        """Stocks Quant Analysis Module

        Attributes:
            `capm_information`: Provides information that relates to the CAPM model\n
            `fama_raw`: Gets base Fama French data to calculate risk\n
            `historical_5`: Get 5 year monthly historical performance for a ticker with dividends filtered\n
            `nipples`: Get historical data for a given nipple\n
        """
        return model.StocksQuantitativeAnalysis()

    @property
    def screener(self):
        """Stocks Screener Module

        Attributes:
            `screener_data`: Screener data for one of the following: overview, valuation, financial, ownership, performance, technical.\n  # noqa: E501
            `screener_view`: Display screener data for one of the following: overview, valuation, financial, ownership, performance, technical.\n  # noqa: E501
            `historical`: Gets historical price of stocks that meet preset\n
            `historical_view`: View historical price of stocks that meet preset\n
        """
        return model.StocksScreener()

    @property
    def sia(self):
        """Stocks Sentiment Analysis Module

        Attributes:
            `filter_stocks`: Filter stocks based on country, sector, industry, market cap and exclude exchanges.\n
            `cpci`: Get number of companies per country in a specific industry (and specific market cap).\n
            `cpci_view`: Display number of companies per country in a specific industry. [Source: Finance Database]\n
            `cpcs`: Get number of companies per country in a specific sector (and specific market cap).\n
            `cpcs_view`: Display number of companies per country in a specific sector. [Source: Finance Database]\n
            `cpic`: Get number of companies per industry in a specific country (and specific market cap).\n
            `cpic_view`: Display number of companies per industry in a specific country. [Source: Finance Database]\n
            `cpis`: Get number of companies per industry in a specific sector (and specific market cap).\n
            `cpis_view`: Display number of companies per industry in a specific sector. [Source: Finance Database]\n
            `cps`: Get number of companies per sector in a specific country (and specific market cap). [Source: Finance Database]\n  # noqa: E501
            `cps_view`: Display number of companies per sector in a specific country (and market cap). [Source: Finance Database]\n  # noqa: E501
            `countries`: Get all countries in Yahoo Finance data based on sector or industry. [Source: Finance Database]\n  # noqa: E501
            `industries`: Get all industries in Yahoo Finance data based on country or sector. [Source: Finance Database]\n  # noqa: E501
            `marketcap`: Get all market cap division in Yahoo Finance data. [Source: Finance Database]\n
            `sectors`: Get all sectors in Yahoo Finance data based on country or industry. [Source: Finance Database]\n
            `stocks_data`: Get stocks data based on a list of stocks and the finance key. The function searches for the
                correct financial statement automatically. [Source: StockAnalysis]\n
        """
        return model.StocksSIA()

    @property
    def ta(self):
        """Stocks Technical Analysis Module

        Attributes:
            `summary`: Get technical summary report provided by FinBrain's API\n
            `view`: Get finviz image for given ticker\n
            `recom`: Get tradingview recommendation based on technical indicators\n
        """
        return model.StocksTechnicalAnalysis()

    @property
    def th(self):
        """Stocks Trading Hours Module

        Attributes:
            `check_if_open`: Check if market open helper function\n
            `all`: Get all exchanges.\n
            `all_view`: Display all exchanges.\n
            `closed`: Get closed exchanges.\n
            `closed_view`: Display closed exchanges.\n
            `open`: Get open exchanges.\n
            `open_view`: Display open exchanges.\n
            `exchange`: Get current exchange open hours.\n
            `exchange_view`: Display current exchange trading hours.\n
        """
        return model.StocksTradingHours()

    @property
    def fa(self):
        """Stocks Fundamental Analysis Module

        Attributes:
            `av_balance`: Get balance sheets for company\n
            `av_cash`: Get cash flows for company\n
            `av_cash_view`: Alpha Vantage income statement\n
            `dupont`: Get dupont ratios\n
            `earnings`: Get earnings calendar for ticker\n
            `fraud`: Get fraud ratios based on fundamentals\n
            `av_income`: Get income statements for company\n
            `av_metrics`: Get key metrics from overview\n
            `av_overview`: Get alpha vantage company overview\n
            `mgmt`: Get company managers from Business Insider\n
            `fama_coe`: Use Fama and French to get the cost of equity for a company\n
            `fama_raw`: Get Fama French data\n
            `historical_5`: Get 5 year monthly historical performance for a ticker with dividends filtered\n
            `similar_dfs`: Get dataframes for similar companies\n
            `analysis`: Save time reading SEC filings with the help of machine learning. [Source: https://eclect.us]\n
            `fmp_balance`: Get balance sheets\n
            `fmp_cash`: Get cash flow\n
            `dcf`: Get stocks dcf from FMP\n
            `enterprise`: Financial Modeling Prep ticker enterprise\n
            `growth`: Get financial statement growth\n
            `fmp_income`: Get income statements\n
            `fmp_metrics`: Get key metrics\n
            `fmp_ratios`: Get key ratios\n
            `profile`: Get ticker profile from FMP\n
            `quote`: Gets ticker quote from FMP\n
            `score`: Gets value score from fmp\n
            `data`: Get fundamental data from finviz\n
            `poly_financials`: Get ticker financial statements from polygon\n
            `poly_financials_view`: Display tickers balance sheet or income statement\n
            `cal`: Get calendar earnings for ticker symbol\n
            `divs`: Get historical dividend for ticker\n
            `yf_financials`: Get cashflow statement for company\n
            `yf_financials_view`: Display tickers balance sheet, income statement or cash-flow\n
            `hq`: Gets google map url for headquarter\n
            `info`: Gets ticker symbol info\n
            `mktcap`: Get market cap over time for ticker. [Source: Yahoo Finance]\n
            `shrs`: Get shareholders from yahoo\n
            `splits`: Get splits and reverse splits events. [Source: Yahoo Finance]\n
            `splits_view`: Display splits and reverse splits events. [Source: Yahoo Finance]\n
            `sust`: Get sustainability metrics from yahoo\n
            `website`: Gets website of company from yfinance\n
        """
        return model.StocksFundamentalAnalysis()
