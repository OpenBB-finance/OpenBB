# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class StocksRoot(Category):
    """Stocks Module

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

    _location_path = "stocks"

    def __init__(self):
        super().__init__()
        self.candle = lib.stocks_helper.display_candle
        self.load = lib.stocks_helper.load
        self.news = lib.common_ultima_newsmonitor_model.get_news
        self.process_candle = lib.stocks_helper.process_candle
        self.quote = lib.stocks_model.get_quote
        self.quote_chart = lib.stocks_view.display_quote
        self.search = lib.stocks_helper.search
        self.tob = lib.stocks_cboe_model.get_top_of_book


class StocksBehavioralAnalysis(Category):
    """Behavioral Analysis Module.

    Attributes:
        `bullbear`: Gets bullbear sentiment for ticker [Source: stocktwits].\n
        `cnews`: Get news from a company. [Source: Finnhub]\n
        `getdd`: Get due diligence posts from list of subreddits [Source: reddit].\n
        `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain].\n
        `headlines_chart`: Plots Sentiment analysis from FinBrain. Prints table if raw is True. [Source: FinBrain]\n
        `infer`: Load tweets from twitter API and analyzes using VADER.\n
        `infer_chart`: Prints Inference sentiment from past n tweets.\n
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
        `sentiment`: Get sentiments from symbol.\n
        `sentiment_chart`: Plots sentiments from symbol\n
        `snews`: Get headlines sentiment using VADER model over time. [Source: Finnhub]\n
        `snews_chart`: Display stock price and headlines sentiment using VADER model over time. [Source: Finnhub]\n
        `spacc`: Get top tickers from r/SPACs [Source: reddit].\n
        `stalker`: Gets messages from given user [Source: stocktwits].\n
        `text_sent`: Find the sentiment of a post and related comments.\n
        `trending`: Get trending tickers from stocktwits [Source: stocktwits].\n
        `wsb`: Get wsb posts [Source: reddit].\n
    """

    _location_path = "stocks.ba"

    def __init__(self):
        super().__init__()
        self.bullbear = lib.stocks_ba_stocktwits_model.get_bullbear
        self.cnews = lib.stocks_ba_finnhub_model.get_company_news
        self.getdd = lib.stocks_ba_reddit_model.get_due_dilligence
        self.headlines = lib.stocks_ba_finbrain_model.get_sentiment
        self.headlines_chart = lib.stocks_ba_finbrain_view.display_sentiment_analysis
        self.infer = lib.stocks_ba_twitter_model.load_analyze_tweets
        self.infer_chart = lib.stocks_ba_twitter_view.display_inference
        self.mentions = lib.stocks_ba_google_model.get_mentions
        self.mentions_chart = lib.stocks_ba_google_view.display_mentions
        self.messages = lib.stocks_ba_stocktwits_model.get_messages
        self.ns = lib.stocks_ba_news_sentiment_model.get_data
        self.ns_chart = lib.stocks_ba_news_sentiment_view.display_articles_data
        self.popular = lib.stocks_ba_reddit_model.get_popular_tickers
        self.queries = lib.stocks_ba_google_model.get_queries
        self.redditsent = lib.stocks_ba_reddit_model.get_posts_about
        self.regions = lib.stocks_ba_google_model.get_regions
        self.regions_chart = lib.stocks_ba_google_view.display_regions
        self.rise = lib.stocks_ba_google_model.get_rise
        self.sentiment = lib.stocks_ba_twitter_model.get_sentiment
        self.sentiment_chart = lib.stocks_ba_twitter_view.display_sentiment
        self.snews = lib.stocks_ba_finnhub_model.get_headlines_sentiment
        self.snews_chart = (
            lib.stocks_ba_finnhub_view.display_stock_price_headlines_sentiment
        )
        self.spacc = lib.stocks_ba_reddit_model.get_spac_community
        self.stalker = lib.stocks_ba_stocktwits_model.get_stalker
        self.text_sent = lib.stocks_ba_reddit_model.get_sentiment
        self.trending = lib.stocks_ba_stocktwits_model.get_trending
        self.wsb = lib.stocks_ba_reddit_model.get_wsb_community


class StocksComparisonAnalysis(Category):
    """Comparison Analysis Module.

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

    _location_path = "stocks.ca"

    def __init__(self):
        super().__init__()
        self.balance = lib.stocks_ca_marketwatch_model.get_balance_comparison
        self.cashflow = lib.stocks_ca_marketwatch_model.get_cashflow_comparison
        self.hcorr = lib.stocks_ca_yahoo_finance_model.get_correlation
        self.hcorr_chart = lib.stocks_ca_yahoo_finance_view.display_correlation
        self.hist = lib.stocks_ca_yahoo_finance_model.get_historical
        self.hist_chart = lib.stocks_ca_yahoo_finance_view.display_historical
        self.income = lib.stocks_ca_marketwatch_model.get_income_comparison
        self.income_chart = lib.stocks_ca_marketwatch_view.display_income_comparison
        self.scorr = lib.stocks_ca_finbrain_model.get_sentiment_correlation
        self.scorr_chart = lib.stocks_ca_finbrain_view.display_sentiment_correlation
        self.screener = lib.stocks_ca_finviz_compare_model.get_comparison_data
        self.sentiment = lib.stocks_ca_finbrain_model.get_sentiments
        self.sentiment_chart = lib.stocks_ca_finbrain_view.display_sentiment_compare
        self.similar = lib.stocks_ca_sdk_helpers.get_similar
        self.volume = lib.stocks_ca_yahoo_finance_model.get_volume
        self.volume_chart = lib.stocks_ca_yahoo_finance_view.display_volume


class StocksDiscovery(Category):
    """Discovery Module.

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

    _location_path = "stocks.disc"

    def __init__(self):
        super().__init__()
        self.active = lib.stocks_disc_yahoofinance_model.get_active
        self.arkord = lib.stocks_disc_ark_model.get_ark_orders
        self.asc = lib.stocks_disc_yahoofinance_model.get_asc
        self.dividends = lib.stocks_disc_nasdaq_model.get_dividend_cal
        self.filings = lib.stocks_fa_fmp_model.get_filings
        self.filings_chart = lib.stocks_disc_fmp_view.display_filings
        self.fipo = lib.stocks_disc_finnhub_model.get_future_ipo
        self.gainers = lib.stocks_disc_yahoofinance_model.get_gainers
        self.gtech = lib.stocks_disc_yahoofinance_model.get_gtech
        self.hotpenny = lib.stocks_disc_shortinterest_model.get_today_hot_penny_stocks
        self.ipo = lib.stocks_disc_finnhub_model.get_ipo_calendar
        self.losers = lib.stocks_disc_yahoofinance_model.get_losers
        self.lowfloat = lib.stocks_disc_shortinterest_model.get_low_float
        self.pipo = lib.stocks_disc_finnhub_model.get_past_ipo
        self.rtat = lib.stocks_disc_nasdaq_model.get_retail_tickers
        self.trending = lib.stocks_disc_seeking_alpha_model.get_trending_list
        self.ugs = lib.stocks_disc_yahoofinance_model.get_ugs
        self.ulc = lib.stocks_disc_yahoofinance_model.get_ulc
        self.upcoming = lib.stocks_disc_seeking_alpha_model.get_next_earnings


class StocksDarkpoolShorts(Category):
    """Darkpool Shorts Module.

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

    _location_path = "stocks.dps"

    def __init__(self):
        super().__init__()
        self.ctb = lib.stocks_dps_ibkr_model.get_cost_to_borrow
        self.dpotc = lib.stocks_dps_finra_model.getTickerFINRAdata
        self.dpotc_chart = lib.stocks_dps_finra_view.darkpool_ats_otc
        self.ftd = lib.stocks_dps_sec_model.get_fails_to_deliver
        self.ftd_chart = lib.stocks_dps_sec_view.fails_to_deliver
        self.hsi = lib.stocks_dps_shortinterest_model.get_high_short_interest
        self.pos = lib.stocks_dps_stockgrid_model.get_dark_pool_short_positions
        self.prom = lib.stocks_dps_finra_model.getATSdata
        self.prom_chart = lib.stocks_dps_finra_view.darkpool_otc
        self.psi_q = lib.stocks_dps_quandl_model.get_short_interest
        self.psi_q_chart = lib.stocks_dps_quandl_view.short_interest
        self.psi_sg = lib.stocks_dps_stockgrid_model.get_short_interest_volume
        self.psi_sg_chart = lib.stocks_dps_stockgrid_view.short_interest_volume
        self.shorted = lib.stocks_dps_yahoofinance_model.get_most_shorted
        self.sidtc = lib.stocks_dps_stockgrid_model.get_short_interest_days_to_cover
        self.spos = lib.stocks_dps_stockgrid_model.get_net_short_position
        self.spos_chart = lib.stocks_dps_stockgrid_view.net_short_position


class StocksFundamentalAnalysis(Category):
    """Fundamental Analysis Module.

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

    _location_path = "stocks.fa"

    def __init__(self):
        super().__init__()
        self.analysis = lib.stocks_fa_eclect_us_model.get_filings_analysis
        self.analyst = lib.stocks_fa_finviz_model.get_analyst_data
        self.balance = lib.stocks_fa_sdk_helpers.get_balance_sheet
        self.cal = lib.stocks_fa_yahoo_finance_model.get_calendar_earnings
        self.cash = lib.stocks_fa_sdk_helpers.get_cash_flow
        self.customer = lib.stocks_fa_csimarket_model.get_customers
        self.dcf = lib.stocks_fa_fmp_model.get_dcf
        self.dcfc = lib.stocks_fa_fmp_model.get_dcf
        self.divs = lib.stocks_fa_yahoo_finance_model.get_dividends
        self.divs_chart = lib.stocks_fa_yahoo_finance_view.display_dividends
        self.dupont = lib.stocks_fa_av_model.get_dupont
        self.earnings = lib.stocks_fa_sdk_helpers.earnings
        self.enterprise = lib.stocks_fa_fmp_model.get_enterprise
        self.epsfc = lib.stocks_fa_seeking_alpha_model.get_estimates_eps
        self.est = lib.stocks_fa_business_insider_model.get_estimates
        self.fama_coe = lib.stocks_fa_dcf_model.get_fama_coe
        self.fama_raw = lib.stocks_fa_dcf_model.get_fama_raw
        self.fraud = lib.stocks_fa_av_model.get_fraud_ratios
        self.growth = lib.stocks_fa_fmp_model.get_financial_growth
        self.historical_5 = lib.stocks_fa_dcf_model.get_historical_5
        self.income = lib.stocks_fa_sdk_helpers.get_income_statement
        self.key = lib.stocks_fa_av_model.get_key_metrics
        self.metrics = lib.stocks_fa_fmp_model.get_key_metrics
        self.mgmt = lib.stocks_fa_business_insider_model.get_management
        self.mktcap = lib.stocks_fa_yahoo_finance_model.get_mktcap
        self.mktcap_chart = lib.stocks_fa_yahoo_finance_view.display_mktcap
        self.news = lib.stocks_fa_finviz_model.get_news
        self.overview = lib.stocks_fa_sdk_helpers.get_overview
        self.pt = lib.stocks_fa_business_insider_model.get_price_target_from_analysts
        self.pt_chart = (
            lib.stocks_fa_business_insider_view.display_price_target_from_analysts
        )
        self.rating = lib.stocks_fa_fmp_model.get_rating
        self.ratios = lib.stocks_fa_fmp_model.get_key_ratios
        self.revfc = lib.stocks_fa_seeking_alpha_model.get_estimates_rev
        self.rot = lib.stocks_fa_finnhub_model.get_rating_over_time
        self.rot_chart = lib.stocks_fa_finnhub_view.rating_over_time
        self.score = lib.stocks_fa_fmp_model.get_score
        self.sec = lib.stocks_fa_nasdaq_model.get_sec_filings
        self.shrs = lib.stocks_fa_yahoo_finance_model.get_shareholders
        self.similar_dfs = lib.stocks_fa_dcf_model.get_similar_dfs
        self.splits = lib.stocks_fa_yahoo_finance_model.get_splits
        self.splits_chart = lib.stocks_fa_yahoo_finance_view.display_splits
        self.supplier = lib.stocks_fa_csimarket_model.get_suppliers


class StocksGovernment(Category):
    """Government Module.

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

    _location_path = "stocks.gov"

    def __init__(self):
        super().__init__()
        self.contracts = lib.stocks_gov_quiverquant_model.get_contracts
        self.contracts_chart = lib.stocks_gov_quiverquant_view.display_contracts
        self.government_trading = (
            lib.stocks_gov_quiverquant_model.get_government_trading
        )
        self.gtrades = lib.stocks_gov_quiverquant_model.get_cleaned_government_trading
        self.gtrades_chart = lib.stocks_gov_quiverquant_view.display_government_trading
        self.histcont = lib.stocks_gov_quiverquant_model.get_hist_contracts
        self.histcont_chart = lib.stocks_gov_quiverquant_view.display_hist_contracts
        self.lastcontracts = lib.stocks_gov_quiverquant_model.get_last_contracts
        self.lastcontracts_chart = (
            lib.stocks_gov_quiverquant_view.display_last_contracts
        )
        self.lasttrades = lib.stocks_gov_quiverquant_model.get_last_government
        self.lobbying = lib.stocks_gov_quiverquant_model.get_lobbying
        self.qtrcontracts = lib.stocks_gov_quiverquant_model.get_qtr_contracts
        self.qtrcontracts_chart = lib.stocks_gov_quiverquant_view.display_qtr_contracts
        self.topbuys = lib.stocks_gov_quiverquant_model.get_government_buys
        self.topbuys_chart = lib.stocks_gov_quiverquant_view.display_government_buys
        self.toplobbying = lib.stocks_gov_quiverquant_model.get_top_lobbying
        self.toplobbying_chart = lib.stocks_gov_quiverquant_view.display_top_lobbying
        self.topsells = lib.stocks_gov_quiverquant_model.get_government_sells
        self.topsells_chart = lib.stocks_gov_quiverquant_view.display_government_sells


class StocksInsiders(Category):
    """Insiders Module.

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

    _location_path = "stocks.ins"

    def __init__(self):
        super().__init__()
        self.act = lib.stocks_insider_businessinsider_model.get_insider_activity
        self.act_chart = lib.stocks_insider_businessinsider_view.insider_activity
        self.blcp = lib.stocks_insider_sdk_helper.blcp
        self.blcs = lib.stocks_insider_sdk_helper.blcs
        self.blip = lib.stocks_insider_sdk_helper.blip
        self.blis = lib.stocks_insider_sdk_helper.blis
        self.blop = lib.stocks_insider_sdk_helper.blop
        self.blos = lib.stocks_insider_sdk_helper.blos
        self.filter = lib.stocks_insider_sdk_helper.insider_filter
        self.lcb = lib.stocks_insider_sdk_helper.lcb
        self.lins = lib.stocks_insider_finviz_model.get_last_insider_activity
        self.lins_chart = lib.stocks_insider_finviz_view.last_insider_activity
        self.lip = lib.stocks_insider_sdk_helper.lip
        self.lis = lib.stocks_insider_sdk_helper.lis
        self.lit = lib.stocks_insider_sdk_helper.lit
        self.lpsb = lib.stocks_insider_sdk_helper.lpsb
        self.print_insider_data = (
            lib.stocks_insider_openinsider_model.get_print_insider_data
        )
        self.print_insider_data_chart = (
            lib.stocks_insider_openinsider_view.print_insider_data
        )
        self.stats = lib.stocks_insider_sdk_helper.stats


class StocksOptions(Category):
    """Options Module.

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

    _location_path = "stocks.options"

    def __init__(self):
        super().__init__()
        self.chains = lib.stocks_options_sdk_helper.get_full_option_chain
        self.dte = lib.stocks_options_helpers.get_dte
        self.eodchain = lib.stocks_options_intrinio_model.get_full_chain_eod
        self.expirations = lib.stocks_options_sdk_helper.get_option_expirations
        self.generate_data = lib.stocks_options_yfinance_model.generate_data
        self.get_strategies = lib.stocks_options_options_chains_model.get_strategies
        self.greeks = lib.stocks_options_sdk_helper.get_greeks
        self.grhist = lib.stocks_options_intrinio_model.get_historical_options
        self.grhist_chart = lib.stocks_options_intrinio_view.view_historical_greeks
        self.hist = lib.stocks_options_sdk_helper.hist
        self.info = lib.stocks_options_barchart_model.get_options_info
        self.info_chart = lib.stocks_options_barchart_view.print_options_data
        self.last_price = lib.stocks_options_tradier_model.get_last_price
        self.load_options_chains = lib.stocks_options_sdk_helper.load_options_chains
        self.oi = lib.stocks_options_view.plot_oi
        self.pcr = lib.stocks_options_alphaquery_model.get_put_call_ratio
        self.pcr_chart = lib.stocks_options_alphaquery_view.display_put_call_ratio
        self.price = lib.stocks_options_sdk_helper.get_option_current_price
        self.unu = lib.stocks_options_fdscanner_model.unusual_options
        self.unu_chart = lib.stocks_options_fdscanner_view.display_options
        self.voi = lib.stocks_options_view.plot_voi
        self.vol = lib.stocks_options_view.plot_vol
        self.vsurf = lib.stocks_options_yfinance_model.get_iv_surface
        self.vsurf_chart = lib.stocks_options_yfinance_view.display_vol_surface


class StocksQuantitativeAnalysis(Category):
    """Quantitative Analysis Module.

    Attributes:
        `beta`: Calculate beta for a ticker and a reference ticker.\n
        `beta_chart`: Display the beta scatterplot + linear regression.\n
        `capm`: Provides information that relates to the CAPM model\n
        `fama_raw`: Gets base Fama French data to calculate risk\n
        `historical_5`: Get 5 year monthly historical performance for a ticker with dividends filtered\n
    """

    _location_path = "stocks.qa"

    def __init__(self):
        super().__init__()
        self.beta = lib.stocks_qa_beta_model.beta_model
        self.beta_chart = lib.stocks_qa_beta_view.beta_view
        self.capm = lib.stocks_qa_factors_model.capm_information
        self.fama_raw = lib.stocks_qa_factors_model.get_fama_raw
        self.historical_5 = lib.stocks_qa_factors_model.get_historical_5


class StocksScreener(Category):
    """Screener Module.

    Attributes:
        `screener_data`: Screener Overview\n
        `screener_data_chart`: Screener one of the following: overview, valuation, financial, ownership, performance, technical.\n
    """

    _location_path = "stocks.screener"

    def __init__(self):
        super().__init__()
        self.screener_data = lib.stocks_screener_finviz_model.get_screener_data
        self.screener_data_chart = lib.stocks_screener_finviz_view.screener


class StocksTechnicalAnalysis(Category):
    """Technical Analysis Module.

    Attributes:
        `recom`: Get tradingview recommendation based on technical indicators\n
        `recom_chart`: Print tradingview recommendation based on technical indicators\n
        `summary`: Get technical summary report provided by FinBrain's API\n
        `summary_chart`: Print technical summary report provided by FinBrain's API\n
    """

    _location_path = "stocks.ta"

    def __init__(self):
        super().__init__()
        self.recom = lib.stocks_ta_tradingview_model.get_tradingview_recommendation
        self.recom_chart = lib.stocks_ta_tradingview_view.print_recommendation
        self.summary = lib.stocks_ta_finbrain_model.get_technical_summary_report
        self.summary_chart = lib.stocks_ta_finbrain_view.technical_summary_report


class StocksTradingHours(Category):
    """Trading Hours Module.

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

    _location_path = "stocks.th"

    def __init__(self):
        super().__init__()
        self.all = lib.stocks_th_bursa_model.get_all
        self.all_chart = lib.stocks_th_bursa_view.display_all
        self.check_if_open = lib.stocks_th_bursa_model.check_if_open
        self.closed = lib.stocks_th_bursa_model.get_closed
        self.closed_chart = lib.stocks_th_bursa_view.display_closed
        self.exchange = lib.stocks_th_bursa_model.get_bursa
        self.exchange_chart = lib.stocks_th_bursa_view.display_exchange
        self.open = lib.stocks_th_bursa_model.get_open
        self.open_chart = lib.stocks_th_bursa_view.display_open
