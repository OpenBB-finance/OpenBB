"""OpenBB Terminal SDK Stocks Module."""
import logging
from typing import List
import pandas as pd

import openbb_terminal.sdk_init as lib
from openbb_terminal.sdk_modules.sdk_helpers import Category

logger = logging.getLogger(__name__)


def get_chains(ticker: str, expiry: str, source: str = "yf") -> pd.DataFrame:
    """Gets option chain for given ticker and expiration from given source (Default: 'yr' - Yahoo Finance)

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options for
    expiry: str
        Date to get options for. YYYY-MM-DD
    source: str
        Source to get options from. Default: 'yf' - Yahoo Finance
        Choices: tradier, tr, yf, yahoofinance, nasdaq, nas

    Returns
    -------
    chains: pd.DataFrame
        Options chain
    """
    if source.lower() in ("yf", "yahoofinance"):
        chains = StocksOptions().chains_yf(ticker, expiry)
        chains = pd.concat([chains.calls, chains.puts])
    elif source.lower() in ("tr", "tradier"):
        chains = StocksOptions().chains_tr(ticker, expiry)
    elif source.lower() in ("nasdaq", "nas"):
        chains = StocksOptions().chains_nasdaq(ticker, expiry)
    else:
        raise ValueError("Invalid source. Please choose from yf, tr, or nasdaq")

    return chains


def get_chains_view(
    ticker: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    calls_only: bool = False,
    puts_only: bool = False,
    to_display: List[str] = None,
    export: str = "",
    source: str = "yf",
):
    """Gets option chain for given ticker and expiration from given source (Default: 'yf' - Yahoo Finance)

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options for
    expiry: str
        Date to get options for. YYYY-MM-DD
    min_sp: float
        Minimum strike price to display
    max_sp: float
        Maximum strike price to display
    calls_only: bool
        Only display calls
    puts_only: bool
        Only display puts
    to_display: List[str]
        List of columns to display
    export: str
        Export raw data into csv, json, or xlsx
    source: str
        Source to get options from. Default: 'yf' - Yahoo Finance
        Choices: tradier, tr, yf, yahoofinance, nasdaq, nas

    Returns
    -------
    chains: pd.DataFrame
        Options chain
    """
    if source.lower() in ("yf", "yahoofinance"):
        chains = StocksOptions().chains_yf_view(
            ticker, expiry, min_sp, max_sp, calls_only, puts_only, export
        )
    elif source.lower() in ("tr", "tradier"):
        chains = StocksOptions().chains_tr_view(
            ticker, expiry, to_display, min_sp, max_sp, calls_only, puts_only, export
        )
    elif source.lower() in ("nasdaq", "nas"):
        chains = StocksOptions().chains_nasdaq_view(ticker, expiry, export)
    else:
        raise ValueError("Invalid source. Please choose from yf, tradier, or nasdaq")

    return chains


class StocksQuantitativeAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.capm_information = lib.stocks_qa_factors_model.capm_information
        self.fama_raw = lib.stocks_qa_factors_model.get_fama_raw
        self.historical_5 = lib.stocks_qa_factors_model.get_historical_5


class StocksTechnicalAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.summary = lib.stocks_ta_finbrain_model.get_technical_summary_report
        self.view = lib.stocks_ta_finviz_model.get_finviz_image
        self.recom = lib.stocks_ta_tradingview_model.get_tradingview_recommendation


class StocksComparisonAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.sentiment = lib.stocks_ca_finbrain_model.get_sentiments
        self.sentiment_view = lib.stocks_ca_finbrain_view.display_sentiment_compare
        self.scorr = lib.stocks_ca_finbrain_model.get_sentiment_correlation
        self.scorr_view = lib.stocks_ca_finbrain_view.display_sentiment_correlation
        self.finnhub_peers = lib.stocks_ca_finnhub_model.get_similar_companies
        self.screener = lib.stocks_ca_finviz_compare_model.get_comparison_data
        self.finviz_peers = lib.stocks_ca_finviz_compare_model.get_similar_companies
        self.balance = lib.stocks_ca_marketwatch_model.get_balance_comparison
        self.cashflow = lib.stocks_ca_marketwatch_model.get_cashflow_comparison
        self.income = lib.stocks_ca_marketwatch_model.get_income_comparison
        self.income_view = lib.stocks_ca_marketwatch_view.display_income_comparison
        self.polygon_peers = lib.stocks_ca_polygon_model.get_similar_companies
        self.hist = lib.stocks_ca_yahoo_finance_model.get_historical
        self.hist_view = lib.stocks_ca_yahoo_finance_view.display_historical
        self.hcorr = lib.stocks_ca_yahoo_finance_model.get_correlation
        self.hcorr_view = lib.stocks_ca_yahoo_finance_view.display_correlation
        self.volume = lib.stocks_ca_yahoo_finance_model.get_volume
        self.volume_view = lib.stocks_ca_yahoo_finance_view.display_volume


class StocksDarkPoolShorts(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.prom = lib.stocks_dps_finra_model.getATSdata
        self.prom_view = lib.stocks_dps_finra_view.darkpool_otc
        self.dpotc = lib.stocks_dps_finra_model.getTickerFINRAdata
        self.dpotc_view = lib.stocks_dps_finra_view.darkpool_ats_otc
        self.ctb = lib.stocks_dps_ibkr_model.get_cost_to_borrow
        self.volexch = lib.stocks_dps_nyse_model.get_short_data_by_exchange
        self.volexch_view = lib.stocks_dps_nyse_view.display_short_by_exchange
        self.psi_q = lib.stocks_dps_quandl_model.get_short_interest
        self.psi_q_view = lib.stocks_dps_quandl_view.short_interest
        self.ftd = lib.stocks_dps_sec_model.get_fails_to_deliver
        self.ftd_view = lib.stocks_dps_sec_view.fails_to_deliver
        self.hsi = lib.stocks_dps_shortinterest_model.get_high_short_interest
        self.pos = lib.stocks_dps_stockgrid_model.get_dark_pool_short_positions
        self.spos = lib.stocks_dps_stockgrid_model.get_net_short_position
        self.spos_view = lib.stocks_dps_stockgrid_view.net_short_position
        self.sidtc = lib.stocks_dps_stockgrid_model.get_short_interest_days_to_cover
        self.psi_sg = lib.stocks_dps_stockgrid_model.get_short_interest_volume
        self.psi_sg_view = lib.stocks_dps_stockgrid_view.short_interest_volume
        self.shorted = lib.stocks_dps_yahoofinance_model.get_most_shorted
        self.ctb = lib.stocks_dps_stocksera_model.get_cost_to_borrow
        self.ctb_view = lib.stocks_dps_stocksera_view.plot_cost_to_borrow


class StocksDiscovery(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.arkord = lib.stocks_disc_ark_model.get_ark_orders
        self.ipo = lib.stocks_disc_finnhub_model.get_ipo_calendar
        self.pipo = lib.stocks_disc_finnhub_model.get_past_ipo
        self.fipo = lib.stocks_disc_finnhub_model.get_future_ipo
        self.dividends = lib.stocks_disc_nasdaq_model.get_dividend_cal
        self.rtat = lib.stocks_disc_nasdaq_model.get_retail_tickers
        self.news = lib.stocks_disc_seeking_alpha_model.get_news
        self.upcoming = lib.stocks_disc_seeking_alpha_model.get_next_earnings
        self.trending = lib.stocks_disc_seeking_alpha_model.get_trending_list
        self.lowfloat = lib.stocks_disc_shortinterest_model.get_low_float
        self.hotpenny = lib.stocks_disc_shortinterest_model.get_today_hot_penny_stocks
        self.active = lib.stocks_disc_yahoofinance_model.get_active
        self.asc = lib.stocks_disc_yahoofinance_model.get_asc
        self.gainers = lib.stocks_disc_yahoofinance_model.get_gainers
        self.gtech = lib.stocks_disc_yahoofinance_model.get_gtech
        self.losers = lib.stocks_disc_yahoofinance_model.get_losers
        self.ugs = lib.stocks_disc_yahoofinance_model.get_ugs
        self.ulc = lib.stocks_disc_yahoofinance_model.get_ulc


class StocksDueDiligence(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.arktrades = lib.stocks_dd_ark_model.get_ark_trades_by_ticker
        self.est = lib.stocks_dd_business_insider_model.get_estimates
        self.pt = lib.stocks_dd_business_insider_model.get_price_target_from_analysts
        self.pt_view = lib.stocks_dd_business_insider_view.price_target_from_analysts
        self.customer = lib.stocks_dd_csimarket_model.get_customers
        self.supplier = lib.stocks_dd_csimarket_model.get_suppliers
        self.rot = lib.stocks_dd_finnhub_model.get_rating_over_time
        self.rot_view = lib.stocks_dd_finnhub_view.rating_over_time
        self.analyst = lib.stocks_dd_finviz_model.get_analyst_data
        self.news = lib.stocks_dd_finviz_model.get_news
        self.rating = lib.stocks_dd_fmp_model.get_rating
        self.sec = lib.stocks_dd_marketwatch_model.get_sec_filings
        self.sec_view = lib.stocks_dd_marketwatch_view.sec_filings


class StocksTradingHours(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.check_if_open = lib.stocks_th_bursa_model.check_if_open
        self.all = lib.stocks_th_bursa_model.get_all
        self.all_view = lib.stocks_th_bursa_view.display_all
        self.closed = lib.stocks_th_bursa_model.get_closed
        self.closed_view = lib.stocks_th_bursa_view.display_closed
        self.open = lib.stocks_th_bursa_model.get_open
        self.open_view = lib.stocks_th_bursa_view.display_open
        self.exchange = lib.stocks_th_bursa_model.get_bursa
        self.exchange_view = lib.stocks_th_bursa_view.display_exchange


class StocksSIA(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.filter_stocks = lib.stocks_sia_financedatabase_model.filter_stocks
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
        self.countries = lib.stocks_sia_financedatabase_model.get_countries
        self.industries = lib.stocks_sia_financedatabase_model.get_industries
        self.marketcap = lib.stocks_sia_financedatabase_model.get_marketcap
        self.sectors = lib.stocks_sia_financedatabase_model.get_sectors
        self.stocks_data = lib.stocks_sia_stockanalysis_model.get_stocks_data


class StocksScreener(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.screener_data = lib.stocks_screener_finviz_model.get_screener_data
        self.screener_view = lib.stocks_screener_finviz_view.screener
        self.historical = lib.stocks_screener_yahoofinance_model.historical
        self.historical_view = lib.stocks_screener_yahoofinance_view.historical


class StocksOptionsScreen(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.check_presets = lib.stocks_options_screen_syncretism_model.check_presets
        self.screener_output = (
            lib.stocks_options_screen_syncretism_model.get_screener_output
        )
        self.screener_output_view = (
            lib.stocks_options_screen_syncretism_view.view_screener_output
        )


class StocksOptionsHedge(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.add_hedge_option = lib.stocks_options_hedge_hedge_model.add_hedge_option
        self.add_hedge_option_view = (
            lib.stocks_options_hedge_hedge_view.add_and_show_greeks
        )
        self.calc_delta = lib.stocks_options_hedge_hedge_model.calc_delta
        self.calc_gamma = lib.stocks_options_hedge_hedge_model.calc_gamma
        self.calc_hedge = lib.stocks_options_hedge_hedge_model.calc_hedge
        self.calc_hedge_view = lib.stocks_options_hedge_hedge_view.show_calculated_hedge
        self.calc_vega = lib.stocks_options_hedge_hedge_model.calc_vega


class StocksOptions(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.screen = StocksOptionsScreen()
        self.hedge = StocksOptionsHedge()
        self.pcr = lib.stocks_options_alphaquery_model.get_put_call_ratio
        self.pcr_view = lib.stocks_options_alphaquery_view.display_put_call_ratio
        self.info = lib.stocks_options_yfinance_model.get_info
        self.info_view = lib.stocks_options_barchart_view.print_options_data
        self.hist_ce = lib.stocks_options_chartexchange_model.get_option_history
        self.hist_ce_view = lib.stocks_options_chartexchange_view.display_raw
        self.unu = lib.stocks_options_fdscanner_model.unusual_options
        self.unu_view = lib.stocks_options_fdscanner_view.display_options
        self.grhist = lib.stocks_options_screen_syncretism_model.get_historical_greeks
        self.grhist_view = (
            lib.stocks_options_screen_syncretism_view.view_historical_greeks
        )
        self.hist_tr = lib.stocks_options_tradier_model.get_historical_options
        self.hist_tr_view = lib.stocks_options_tradier_view.display_historical
        self.chains_tr = lib.stocks_options_tradier_model.get_option_chains
        self.chains_tr_view = lib.stocks_options_tradier_view.display_chains
        self.chains_yf = lib.stocks_options_yfinance_model.get_option_chain
        self.chains_yf_view = lib.stocks_options_yfinance_view.display_chains
        self.chains_nasdaq = lib.stocks_options_nasdaq_model.get_chain_given_expiration
        self.chains_nasdaq_view = lib.stocks_options_nasdaq_view.display_chains
        self.last_price = lib.stocks_options_tradier_model.last_price
        self.option_expirations = lib.stocks_options_yfinance_model.option_expirations
        self.process_chains = lib.stocks_options_tradier_model.process_chains
        self.generate_data = lib.stocks_options_yfinance_model.generate_data
        self.closing = lib.stocks_options_yfinance_model.get_closing
        self.dividend = lib.stocks_options_yfinance_model.get_dividend
        self.dte = lib.stocks_options_yfinance_model.get_dte
        self.vsurf = lib.stocks_options_yfinance_model.get_iv_surface
        self.vsurf_view = lib.stocks_options_yfinance_view.display_vol_surface
        self.vol_yf = lib.stocks_options_yfinance_model.get_vol
        self.vol_yf_view = lib.stocks_options_yfinance_view.plot_vol
        self.voi_yf = lib.stocks_options_yfinance_model.get_volume_open_interest
        self.voi_yf_view = lib.stocks_options_yfinance_view.plot_volume_open_interest
        self.option_chain = lib.stocks_options_yfinance_model.get_option_chain
        self.price = lib.stocks_options_yfinance_model.get_price
        self.x_values = lib.stocks_options_yfinance_model.get_x_values
        self.y_values = lib.stocks_options_yfinance_model.get_y_values
        self.chains = get_chains


class StocksInsider(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
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


class StocksGovMenu:
    def __init__(self):
        self.qtrcontracts = lib.stocks_gov_quiverquant_model.get_qtr_contracts
        self.qtrcontracts_view = lib.stocks_gov_quiverquant_view.display_qtr_contracts
        self.gov_trading = lib.stocks_gov_quiverquant_model.get_government_trading
        self.contracts = lib.stocks_gov_quiverquant_model.get_contracts
        self.contracts_view = lib.stocks_gov_quiverquant_view.display_contracts
        self.topbuys = lib.stocks_gov_quiverquant_model.get_government_buys
        self.topbuys_view = lib.stocks_gov_quiverquant_view.display_government_buys
        self.topsells = lib.stocks_gov_quiverquant_model.get_government_sells
        self.topsells_view = lib.stocks_gov_quiverquant_view.display_government_sells
        self.gtrades = lib.stocks_gov_quiverquant_model.get_cleaned_government_trading
        self.gtrades_view = lib.stocks_gov_quiverquant_view.display_government_trading
        self.histcont = lib.stocks_gov_quiverquant_model.get_hist_contracts
        self.histcont_view = lib.stocks_gov_quiverquant_view.display_hist_contracts
        self.lastcontracts = lib.stocks_gov_quiverquant_model.get_last_contracts
        self.lastcontracts_view = lib.stocks_gov_quiverquant_view.display_last_contracts
        self.lasttrades = lib.stocks_gov_quiverquant_model.get_last_government
        self.lobbying = lib.stocks_gov_quiverquant_model.get_lobbying
        self.toplobbying = lib.stocks_gov_quiverquant_model.get_top_lobbying
        self.toplobbying_view = lib.stocks_gov_quiverquant_view.display_top_lobbying


class StocksFundamentalAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.av_balance = lib.stocks_fa_av_model.get_balance_sheet
        self.av_cash = lib.stocks_fa_av_model.get_cash_flow
        self.av_cash_view = lib.stocks_fa_av_view.display_cash_flow
        self.dupont = lib.stocks_fa_av_model.get_dupont
        self.earnings = lib.stocks_fa_av_model.get_earnings
        self.fraud = lib.stocks_fa_av_model.get_fraud_ratios
        self.av_income = lib.stocks_fa_av_model.get_income_statements
        self.av_metrics = lib.stocks_fa_av_model.get_key_metrics
        self.av_overview = lib.stocks_fa_av_model.get_overview
        self.mgmt = lib.stocks_fa_business_insider_model.get_management
        self.fama_coe = lib.stocks_fa_dcf_model.get_fama_coe
        self.fama_raw = lib.stocks_fa_dcf_model.get_fama_raw
        self.historical_5 = lib.stocks_fa_dcf_model.get_historical_5
        self.similar_dfs = lib.stocks_fa_dcf_model.get_similar_dfs
        self.analysis = lib.stocks_fa_eclect_us_model.get_filings_analysis
        self.fmp_balance = lib.stocks_fa_fmp_model.get_balance
        self.fmp_cash = lib.stocks_fa_fmp_model.get_cash
        self.dcf = lib.stocks_fa_fmp_model.get_dcf
        self.enterprise = lib.stocks_fa_fmp_model.get_enterprise
        self.growth = lib.stocks_fa_fmp_model.get_financial_growth
        self.fmp_income = lib.stocks_fa_fmp_model.get_income
        self.fmp_metrics = lib.stocks_fa_fmp_model.get_key_metrics
        self.fmp_ratios = lib.stocks_fa_fmp_model.get_key_ratios
        self.profile = lib.stocks_fa_fmp_model.get_profile
        self.quote = lib.stocks_fa_fmp_model.get_quote
        self.score = lib.stocks_fa_fmp_model.get_score
        self.data = lib.stocks_fa_finviz_model.get_data
        self.poly_financials = lib.stocks_fa_polygon_model.get_financials
        self.poly_financials_view = lib.stocks_fa_polygon_view.display_fundamentals
        self.cal = lib.stocks_fa_yahoo_finance_model.get_calendar_earnings
        self.divs = lib.stocks_fa_yahoo_finance_model.get_dividends
        self.yf_financials = lib.stocks_fa_yahoo_finance_model.get_financials
        self.yf_financials_view = lib.stocks_fa_yahoo_finance_view.display_fundamentals
        self.hq = lib.stocks_fa_yahoo_finance_model.get_hq
        self.info = lib.stocks_fa_yahoo_finance_model.get_info
        self.mktcap = lib.stocks_fa_yahoo_finance_model.get_mktcap
        self.shrs = lib.stocks_fa_yahoo_finance_model.get_shareholders
        self.splits = lib.stocks_fa_yahoo_finance_model.get_splits
        self.splits_view = lib.stocks_fa_yahoo_finance_view.display_splits
        self.sust = lib.stocks_fa_yahoo_finance_model.get_sustainability
        self.website = lib.stocks_fa_yahoo_finance_model.get_website


class StocksBehavioralAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.headlines = lib.ba_finbrain_model.get_sentiment
        self.headlines_view = lib.ba_finbrain_view.display_sentiment_analysis
        self.mentions = lib.ba_google_model.get_mentions
        self.mentions_view = lib.ba_google_view.display_mentions
        self.queries = lib.ba_google_model.get_queries
        self.regions = lib.ba_google_model.get_regions
        self.regions_view = lib.ba_google_view.display_regions
        self.rise = lib.ba_google_model.get_rise
        self.rise_view = lib.ba_google_view.display_rise
        self.getdd = lib.ba_reddit_model.get_due_dilligence
        self.popular = lib.ba_reddit_model.get_popular_tickers
        self.popular_view = lib.ba_reddit_view.display_popular_tickers
        self.redditsent = lib.ba_reddit_model.get_posts_about
        self.redditsent_view = lib.ba_reddit_view.display_redditsent
        self.text_sent = lib.ba_reddit_model.get_sentiment
        self.spac = lib.ba_reddit_model.get_spac
        self.spacc = lib.ba_reddit_model.get_spac_community
        self.watchlist = lib.ba_reddit_model.get_watchlists
        self.watchlist_view = lib.ba_reddit_view.display_watchlist
        self.wsb = lib.ba_reddit_model.get_wsb_community
        self.hist = lib.ba_sentimentinvestor_model.get_historical
        self.hist_view = lib.ba_sentimentinvestor_view.display_historical
        self.trend = lib.ba_sentimentinvestor_model.get_trending
        self.trend_view = lib.ba_sentimentinvestor_view.display_trending
        self.bullbear = lib.ba_stocktwits_model.get_bullbear
        self.bullbear_view = lib.ba_stocktwits_view.display_bullbear
        self.messages = lib.ba_stocktwits_model.get_messages
        self.messages_view = lib.ba_stocktwits_view.display_messages
        self.stalker = lib.ba_stocktwits_model.get_stalker
        self.trending = lib.ba_stocktwits_model.get_trending
        self.infer = lib.ba_twitter_model.load_analyze_tweets
        self.infer_view = lib.ba_twitter_view.display_inference
        self.sentiment = lib.ba_twitter_model.get_sentiment
        self.sentiment_view = lib.ba_twitter_view.display_sentiment
