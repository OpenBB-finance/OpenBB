# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class StocksRoot(Category):
    """OpenBB SDK Stocks Module

    Attributes:
        `candle`: Show candle plot of loaded ticker.\n
        `load`: Load a symbol to perform analysis using the string above as a template.\n
        `process_candle`: Process DataFrame into candle style plot.\n
        `quote`: Display quote from YahooFinance\n
        `search`: Search selected query for tickers.\n
        `tob`: Get top of book bid and ask for ticker on exchange [CBOE.com]\n
    """

    def __init__(self):
        super().__init__()
        self.candle = lib.stocks_helper.display_candle
        self.load = lib.stocks_helper.load
        self.process_candle = lib.stocks_helper.process_candle
        self.quote = lib.stocks_views.display_quote
        self.search = lib.stocks_helper.search
        self.tob = lib.stocks_cboe_model.get_top_of_book


class StocksBehavioralAnalysis(Category):
    """OpenBB SDK Behavioral Analysis Module.

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

    def __init__(self):
        super().__init__()
        self.bullbear = lib.stocks_ba_stocktwits_model.get_bullbear
        self.bullbear_view = lib.stocks_ba_stocktwits_view.display_bullbear
        self.getdd = lib.stocks_ba_reddit_model.get_due_dilligence
        self.headlines = lib.stocks_ba_finbrain_model.get_sentiment
        self.headlines_view = lib.stocks_ba_finbrain_view.display_sentiment_analysis
        self.hist = lib.stocks_ba_sentimentinvestor_model.get_historical
        self.hist_view = lib.stocks_ba_sentimentinvestor_view.display_historical
        self.infer = lib.stocks_ba_twitter_model.load_analyze_tweets
        self.infer_view = lib.stocks_ba_twitter_view.display_inference
        self.mentions = lib.stocks_ba_google_model.get_mentions
        self.mentions_view = lib.stocks_ba_google_view.display_mentions
        self.messages = lib.stocks_ba_stocktwits_model.get_messages
        self.messages_view = lib.stocks_ba_stocktwits_view.display_messages
        self.popular = lib.stocks_ba_reddit_model.get_popular_tickers
        self.popular_view = lib.stocks_ba_reddit_view.display_popular_tickers
        self.queries = lib.stocks_ba_google_model.get_queries
        self.queries_view = lib.stocks_ba_google_view.display_queries
        self.redditsent = lib.stocks_ba_reddit_model.get_posts_about
        self.redditsent_view = lib.stocks_ba_reddit_view.display_redditsent
        self.regions = lib.stocks_ba_google_model.get_regions
        self.regions_view = lib.stocks_ba_google_view.display_regions
        self.rise = lib.stocks_ba_google_model.get_rise
        self.rise_view = lib.stocks_ba_google_view.display_rise
        self.sentiment = lib.stocks_ba_twitter_model.get_sentiment
        self.sentiment_view = lib.stocks_ba_twitter_view.display_sentiment
        self.spac = lib.stocks_ba_reddit_model.get_spac
        self.spacc = lib.stocks_ba_reddit_model.get_spac_community
        self.stalker = lib.stocks_ba_stocktwits_model.get_stalker
        self.text_sent = lib.stocks_ba_reddit_model.get_sentiment
        self.trend = lib.stocks_ba_sentimentinvestor_model.get_trending
        self.trend_view = lib.stocks_ba_sentimentinvestor_view.display_trending
        self.trending = lib.stocks_ba_stocktwits_model.get_trending
        self.watchlist = lib.stocks_ba_reddit_model.get_watchlists
        self.watchlist_view = lib.stocks_ba_reddit_view.display_watchlist
        self.wsb = lib.stocks_ba_reddit_model.get_wsb_community


class StocksComparisonAnalysis(Category):
    """OpenBB SDK Comparison Analysis Module.

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

    def __init__(self):
        super().__init__()
        self.balance = lib.stocks_ca_marketwatch_model.get_balance_comparison
        self.cashflow = lib.stocks_ca_marketwatch_model.get_cashflow_comparison
        self.finnhub_peers = lib.stocks_ca_finnhub_model.get_similar_companies
        self.finviz_peers = lib.stocks_ca_finviz_compare_model.get_similar_companies
        self.hcorr = lib.stocks_ca_yahoo_finance_model.get_correlation
        self.hcorr_view = lib.stocks_ca_yahoo_finance_view.display_correlation
        self.hist = lib.stocks_ca_yahoo_finance_model.get_historical
        self.hist_view = lib.stocks_ca_yahoo_finance_view.display_historical
        self.income = lib.stocks_ca_marketwatch_model.get_income_comparison
        self.income_view = lib.stocks_ca_marketwatch_view.display_income_comparison
        self.polygon_peers = lib.stocks_ca_polygon_model.get_similar_companies
        self.scorr = lib.stocks_ca_finbrain_model.get_sentiment_correlation
        self.scorr_view = lib.stocks_ca_finbrain_view.display_sentiment_correlation
        self.screener = lib.stocks_ca_finviz_compare_model.get_comparison_data
        self.sentiment = lib.stocks_ca_finbrain_model.get_sentiments
        self.sentiment_view = lib.stocks_ca_finbrain_view.display_sentiment_compare
        self.volume = lib.stocks_ca_yahoo_finance_model.get_volume
        self.volume_view = lib.stocks_ca_yahoo_finance_view.display_volume


class StocksDueDiligence(Category):
    """OpenBB SDK Due Diligence Module.

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

    def __init__(self):
        super().__init__()
        self.analyst = lib.stocks_dd_finviz_model.get_analyst_data
        self.arktrades = lib.stocks_dd_ark_model.get_ark_trades_by_ticker
        self.customer = lib.stocks_dd_csimarket_model.get_customers
        self.est = lib.stocks_dd_business_insider_model.get_estimates
        self.news = lib.stocks_dd_finviz_model.get_news
        self.pt = lib.stocks_dd_business_insider_model.get_price_target_from_analysts
        self.pt_view = lib.stocks_dd_business_insider_view.price_target_from_analysts
        self.rating = lib.stocks_dd_fmp_model.get_rating
        self.rot = lib.stocks_dd_finnhub_model.get_rating_over_time
        self.rot_view = lib.stocks_dd_finnhub_view.rating_over_time
        self.sec = lib.stocks_dd_marketwatch_model.get_sec_filings
        self.sec_view = lib.stocks_dd_marketwatch_view.sec_filings
        self.supplier = lib.stocks_dd_csimarket_model.get_suppliers


class StocksDiscovery(Category):
    """OpenBB SDK Discovery Module.

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

    def __init__(self):
        super().__init__()
        self.active = lib.stocks_disc_yahoofinance_model.get_active
        self.arkord = lib.stocks_disc_ark_model.get_ark_orders
        self.asc = lib.stocks_disc_yahoofinance_model.get_asc
        self.dividends = lib.stocks_disc_nasdaq_model.get_dividend_cal
        self.fipo = lib.stocks_disc_finnhub_model.get_future_ipo
        self.gainers = lib.stocks_disc_yahoofinance_model.get_gainers
        self.gtech = lib.stocks_disc_yahoofinance_model.get_gtech
        self.hotpenny = lib.stocks_disc_shortinterest_model.get_today_hot_penny_stocks
        self.ipo = lib.stocks_disc_finnhub_model.get_ipo_calendar
        self.losers = lib.stocks_disc_yahoofinance_model.get_losers
        self.lowfloat = lib.stocks_disc_shortinterest_model.get_low_float
        self.news = lib.stocks_disc_seeking_alpha_model.get_news
        self.pipo = lib.stocks_disc_finnhub_model.get_past_ipo
        self.rtat = lib.stocks_disc_nasdaq_model.get_retail_tickers
        self.trending = lib.stocks_disc_seeking_alpha_model.get_trending_list
        self.ugs = lib.stocks_disc_yahoofinance_model.get_ugs
        self.ulc = lib.stocks_disc_yahoofinance_model.get_ulc
        self.upcoming = lib.stocks_disc_seeking_alpha_model.get_next_earnings


class StocksDarkpoolShorts(Category):
    """OpenBB SDK Darkpool Shorts Module.

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

    def __init__(self):
        super().__init__()
        self.ctb = lib.stocks_dps_stocksera_model.get_cost_to_borrow
        self.ctb_view = lib.stocks_dps_stocksera_view.plot_cost_to_borrow
        self.dpotc = lib.stocks_dps_finra_model.getTickerFINRAdata
        self.dpotc_view = lib.stocks_dps_finra_view.darkpool_ats_otc
        self.ftd = lib.stocks_dps_sec_model.get_fails_to_deliver
        self.ftd_view = lib.stocks_dps_sec_view.fails_to_deliver
        self.hsi = lib.stocks_dps_shortinterest_model.get_high_short_interest
        self.pos = lib.stocks_dps_stockgrid_model.get_dark_pool_short_positions
        self.prom = lib.stocks_dps_finra_model.getATSdata
        self.prom_view = lib.stocks_dps_finra_view.darkpool_otc
        self.psi_q = lib.stocks_dps_quandl_model.get_short_interest
        self.psi_q_view = lib.stocks_dps_quandl_view.short_interest
        self.psi_sg = lib.stocks_dps_stockgrid_model.get_short_interest_volume
        self.psi_sg_view = lib.stocks_dps_stockgrid_view.short_interest_volume
        self.shorted = lib.stocks_dps_yahoofinance_model.get_most_shorted
        self.sidtc = lib.stocks_dps_stockgrid_model.get_short_interest_days_to_cover
        self.spos = lib.stocks_dps_stockgrid_model.get_net_short_position
        self.spos_view = lib.stocks_dps_stockgrid_view.net_short_position
        self.volexch = lib.stocks_dps_nyse_model.get_short_data_by_exchange
        self.volexch_view = lib.stocks_dps_nyse_view.display_short_by_exchange


class StocksFundamentalAnalysis(Category):
    """OpenBB SDK Fundamental Analysis Module.

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

    def __init__(self):
        super().__init__()
        self.analysis = lib.stocks_fa_eclect_us_model.get_filings_analysis
        self.av_balance = lib.stocks_fa_av_model.get_balance_sheet
        self.av_cash = lib.stocks_fa_av_model.get_cash_flow
        self.av_cash_view = lib.stocks_fa_av_view.display_cash_flow
        self.av_income = lib.stocks_fa_av_model.get_income_statements
        self.av_metrics = lib.stocks_fa_av_model.get_key_metrics
        self.av_overview = lib.stocks_fa_av_model.get_overview
        self.cal = lib.stocks_fa_yahoo_finance_model.get_calendar_earnings
        self.data = lib.stocks_fa_finviz_model.get_data
        self.dcf = lib.stocks_fa_fmp_model.get_dcf
        self.divs = lib.stocks_fa_yahoo_finance_model.get_dividends
        self.dupont = lib.stocks_fa_av_model.get_dupont
        self.earnings = lib.stocks_fa_av_model.get_earnings
        self.enterprise = lib.stocks_fa_fmp_model.get_enterprise
        self.fama_coe = lib.stocks_fa_dcf_model.get_fama_coe
        self.fama_raw = lib.stocks_fa_dcf_model.get_fama_raw
        self.fmp_balance = lib.stocks_fa_fmp_model.get_balance
        self.fmp_cash = lib.stocks_fa_fmp_model.get_cash
        self.fmp_income = lib.stocks_fa_fmp_model.get_income
        self.fmp_metrics = lib.stocks_fa_fmp_model.get_key_metrics
        self.fmp_ratios = lib.stocks_fa_fmp_model.get_key_ratios
        self.fraud = lib.stocks_fa_av_model.get_fraud_ratios
        self.growth = lib.stocks_fa_fmp_model.get_financial_growth
        self.historical_5 = lib.stocks_fa_dcf_model.get_historical_5
        self.hq = lib.stocks_fa_yahoo_finance_model.get_hq
        self.info = lib.stocks_fa_yahoo_finance_model.get_info
        self.mgmt = lib.stocks_fa_business_insider_model.get_management
        self.mktcap = lib.stocks_fa_yahoo_finance_model.get_mktcap
        self.poly_financials = lib.stocks_fa_polygon_model.get_financials
        self.poly_financials_view = lib.stocks_fa_polygon_view.display_fundamentals
        self.profile = lib.stocks_fa_fmp_model.get_profile
        self.quote = lib.stocks_fa_fmp_model.get_quote
        self.score = lib.stocks_fa_fmp_model.get_score
        self.shrs = lib.stocks_fa_yahoo_finance_model.get_shareholders
        self.similar_dfs = lib.stocks_fa_dcf_model.get_similar_dfs
        self.splits = lib.stocks_fa_yahoo_finance_model.get_splits
        self.splits_view = lib.stocks_fa_yahoo_finance_view.display_splits
        self.sust = lib.stocks_fa_yahoo_finance_model.get_sustainability
        self.website = lib.stocks_fa_yahoo_finance_model.get_website
        self.yf_financials = lib.stocks_fa_yahoo_finance_model.get_financials
        self.yf_financials_view = lib.stocks_fa_yahoo_finance_view.display_fundamentals


class StocksGovernment(Category):
    """OpenBB SDK Government Module.

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

    def __init__(self):
        super().__init__()
        self.contracts = lib.stocks_gov_quiverquant_model.get_contracts
        self.contracts_view = lib.stocks_gov_quiverquant_view.display_contracts
        self.government_trading = (
            lib.stocks_gov_quiverquant_model.get_government_trading
        )
        self.gtrades = lib.stocks_gov_quiverquant_model.get_cleaned_government_trading
        self.gtrades_view = lib.stocks_gov_quiverquant_view.display_government_trading
        self.histcont = lib.stocks_gov_quiverquant_model.get_hist_contracts
        self.histcont_view = lib.stocks_gov_quiverquant_view.display_hist_contracts
        self.lastcontracts = lib.stocks_gov_quiverquant_model.get_last_contracts
        self.lastcontracts_view = lib.stocks_gov_quiverquant_view.display_last_contracts
        self.lasttrades = lib.stocks_gov_quiverquant_model.get_last_government
        self.lobbying = lib.stocks_gov_quiverquant_model.get_lobbying
        self.qtrcontracts = lib.stocks_gov_quiverquant_model.get_qtr_contracts
        self.qtrcontracts_view = lib.stocks_gov_quiverquant_view.display_qtr_contracts
        self.topbuys = lib.stocks_gov_quiverquant_model.get_government_buys
        self.topbuys_view = lib.stocks_gov_quiverquant_view.display_government_buys
        self.toplobbying = lib.stocks_gov_quiverquant_model.get_top_lobbying
        self.toplobbying_view = lib.stocks_gov_quiverquant_view.display_top_lobbying
        self.topsells = lib.stocks_gov_quiverquant_model.get_government_sells
        self.topsells_view = lib.stocks_gov_quiverquant_view.display_government_sells


class StocksInsiders(Category):
    """OpenBB SDK Insiders Module.

    Attributes:
        `act`: Get insider activity. [Source: Business Insider]\n
        `act_view`: Display insider activity. [Source: Business Insider]\n
        `lins`: Get last insider activity for a given stock ticker. [Source: Finviz]\n
        `lins_view`: Display insider activity for a given stock ticker. [Source: Finviz]\n
        `print_insider_data`: Print insider data\n
        `print_insider_data_view`: Print insider data\n
    """

    def __init__(self):
        super().__init__()
        self.act = lib.stocks_insider_businessinsider_model.get_insider_activity
        self.act_view = lib.stocks_insider_businessinsider_view.insider_activity
        self.lins = lib.stocks_insider_finviz_model.get_last_insider_activity
        self.lins_view = lib.stocks_insider_finviz_view.last_insider_activity
        self.print_insider_data = (
            lib.stocks_insider_openinsider_model.get_print_insider_data
        )
        self.print_insider_data_view = (
            lib.stocks_insider_openinsider_view.print_insider_data
        )


class StocksOptions(Category):
    """OpenBB SDK Options Module.

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

    def __init__(self):
        super().__init__()
        self.chains_nasdaq = lib.stocks_options_nasdaq_model.get_chain_given_expiration
        self.chains_nasdaq_view = lib.stocks_options_nasdaq_view.display_chains
        self.chains_tr = lib.stocks_options_tradier_model.get_option_chains
        self.chains_tr_view = lib.stocks_options_tradier_view.display_chains
        self.chains_yf = lib.stocks_options_yfinance_model.get_option_chain
        self.chains_yf_view = lib.stocks_options_yfinance_view.display_chains
        self.closing = lib.stocks_options_yfinance_model.get_closing
        self.dividend = lib.stocks_options_yfinance_model.get_dividend
        self.dte = lib.stocks_options_yfinance_model.get_dte
        self.generate_data = lib.stocks_options_yfinance_model.generate_data
        self.grhist = lib.stocks_options_screen_syncretism_model.get_historical_greeks
        self.grhist_view = (
            lib.stocks_options_screen_syncretism_view.view_historical_greeks
        )
        self.hist_ce = lib.stocks_options_chartexchange_model.get_option_history
        self.hist_ce_view = lib.stocks_options_chartexchange_view.display_raw
        self.hist_tr = lib.stocks_options_tradier_model.get_historical_options
        self.hist_tr_view = lib.stocks_options_tradier_view.display_historical
        self.info = lib.stocks_options_yfinance_model.get_info
        self.info_view = lib.stocks_options_barchart_view.print_options_data
        self.last_price = lib.stocks_options_tradier_model.last_price
        self.option_chain = lib.stocks_options_yfinance_model.get_option_chain
        self.option_expirations = lib.stocks_options_yfinance_model.option_expirations
        self.pcr = lib.stocks_options_alphaquery_model.get_put_call_ratio
        self.pcr_view = lib.stocks_options_alphaquery_view.display_put_call_ratio
        self.price = lib.stocks_options_yfinance_model.get_price
        self.process_chains = lib.stocks_options_tradier_model.process_chains
        self.unu = lib.stocks_options_fdscanner_model.unusual_options
        self.unu_view = lib.stocks_options_fdscanner_view.display_options
        self.voi_yf = lib.stocks_options_yfinance_model.get_volume_open_interest
        self.voi_yf_view = lib.stocks_options_yfinance_view.plot_volume_open_interest
        self.vol_yf = lib.stocks_options_yfinance_model.get_vol
        self.vol_yf_view = lib.stocks_options_yfinance_view.plot_vol
        self.vsurf = lib.stocks_options_yfinance_model.get_iv_surface
        self.vsurf_view = lib.stocks_options_yfinance_view.display_vol_surface
        self.x_values = lib.stocks_options_yfinance_model.get_x_values
        self.y_values = lib.stocks_options_yfinance_model.get_y_values


class StocksQuantitativeAnalysis(Category):
    """OpenBB SDK Quantitative Analysis Module.

    Attributes:
        `capm_information`: Provides information that relates to the CAPM model\n
        `fama_raw`: Gets base Fama French data to calculate risk\n
        `historical_5`: Get 5 year monthly historical performance for a ticker with dividends filtered\n
    """

    def __init__(self):
        super().__init__()
        self.capm_information = lib.stocks_qa_factors_model.capm_information
        self.fama_raw = lib.stocks_qa_factors_model.get_fama_raw
        self.historical_5 = lib.stocks_qa_factors_model.get_historical_5


class StocksScreener(Category):
    """OpenBB SDK Screener Module.

    Attributes:
        `historical`: View historical price of stocks that meet preset\n
        `historical_view`: View historical price of stocks that meet preset\n
        `screener_view`: Screener one of the following: overview, valuation, financial, ownership, performance, technical.\n
        `screener_data`: Screener Overview\n
    """

    def __init__(self):
        super().__init__()
        self.historical = lib.stocks_screener_yahoofinance_model.historical
        self.historical_view = lib.stocks_screener_yahoofinance_view.historical
        self.screener_view = lib.stocks_screener_finviz_view.screener
        self.screener_data = lib.stocks_screener_finviz_model.get_screener_data


class StocksSectorIndustryAnalysis(Category):
    """OpenBB SDK Sector Industry Analysis Module.

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

    def __init__(self):
        super().__init__()
        self.countries = lib.stocks_sia_financedatabase_model.get_countries
        self.cpci = (
            lib.stocks_sia_financedatabase_model.get_companies_per_country_in_industry
        )
        self.cpci_view = (
            lib.stocks_sia_financedatabase_view.display_companies_per_country_in_industry
        )
        self.cpcs = (
            lib.stocks_sia_financedatabase_model.get_companies_per_country_in_sector
        )
        self.cpcs_view = (
            lib.stocks_sia_financedatabase_view.display_companies_per_country_in_sector
        )
        self.cpic = (
            lib.stocks_sia_financedatabase_model.get_companies_per_industry_in_country
        )
        self.cpic_view = (
            lib.stocks_sia_financedatabase_view.display_companies_per_industry_in_country
        )
        self.cpis = (
            lib.stocks_sia_financedatabase_model.get_companies_per_industry_in_sector
        )
        self.cpis_view = (
            lib.stocks_sia_financedatabase_view.display_companies_per_industry_in_sector
        )
        self.cps = (
            lib.stocks_sia_financedatabase_model.get_companies_per_sector_in_country
        )
        self.cps_view = (
            lib.stocks_sia_financedatabase_view.display_companies_per_sector_in_country
        )
        self.filter_stocks = lib.stocks_sia_financedatabase_model.filter_stocks
        self.industries = lib.stocks_sia_financedatabase_model.get_industries
        self.marketcap = lib.stocks_sia_financedatabase_model.get_marketcap
        self.sectors = lib.stocks_sia_financedatabase_model.get_sectors
        self.stocks_data = lib.stocks_sia_stockanalysis_model.get_stocks_data


class StocksTechnicalAnalysis(Category):
    """OpenBB SDK Technical Analysis Module.

    Attributes:
        `recom`: Get tradingview recommendation based on technical indicators\n
        `summary`: Get technical summary report provided by FinBrain's API\n
        `view`: Get finviz image for given ticker\n
    """

    def __init__(self):
        super().__init__()
        self.recom = lib.stocks_ta_tradingview_model.get_tradingview_recommendation
        self.summary = lib.stocks_ta_finbrain_model.get_technical_summary_report
        self.view = lib.stocks_ta_finviz_model.get_finviz_image


class StocksTradingHours(Category):
    """OpenBB SDK Trading Hours Module.

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

    def __init__(self):
        super().__init__()
        self.all = lib.stocks_th_bursa_model.get_all
        self.all_view = lib.stocks_th_bursa_view.display_all
        self.check_if_open = lib.stocks_th_bursa_model.check_if_open
        self.closed = lib.stocks_th_bursa_model.get_closed
        self.closed_view = lib.stocks_th_bursa_view.display_closed
        self.exchange = lib.stocks_th_bursa_model.get_bursa
        self.exchange_view = lib.stocks_th_bursa_view.display_exchange
        self.open = lib.stocks_th_bursa_model.get_open
        self.open_view = lib.stocks_th_bursa_view.display_open
