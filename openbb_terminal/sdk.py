"""OpenBB Terminal SDK."""
# flake8: noqa
# pylint: disable=unused-import,wrong-import-order
# pylint: disable=C0302,W0611,not-callable,ungrouped-imports
from inspect import signature, Parameter
import warnings
import types
import functools
import importlib
from typing import Optional, Callable, List, Union
import logging
from traceback import format_stack

import openbb_terminal.config_terminal as cfg
from openbb_terminal.rich_config import console
from openbb_terminal.reports.reports_controller import ReportController
from openbb_terminal.dashboards.dashboards_controller import DashboardsController

try:
    import darts  # pyright: reportMissingImports=false

    # If you just import darts this will pass during pip install, this creates
    # Failures later on, also importing utils ensures that darts is installed correctly
    from darts import utils

    forecasting = True
except ImportError:
    forecasting = False
    warnings.warn(
        "Forecasting dependencies are not installed."
        " This part of the SDK will not be usable"
    )

from openbb_terminal.config_terminal import theme

from openbb_terminal.helper_classes import TerminalStyle  # noqa: F401

from openbb_terminal import helper_funcs as helper  # noqa: F401
from openbb_terminal.loggers import setup_logging
from openbb_terminal.decorators import log_start_end, sdk_arg_logger
from openbb_terminal.core.log.generation.settings_logger import log_all_settings
from .reports import widget_helpers as widgets  # noqa: F401

from .portfolio.portfolio_model import PortfolioModel as Portfolio
from .cryptocurrency.due_diligence.pycoingecko_model import Coin

logger = logging.getLogger(__name__)

TerminalStyle().applyMPLstyle()

SUPPRESS_LOGGING_CLASSES = {
    ReportController: "ReportController",
    DashboardsController: "DashboardsController",
}


functions = {
    "alt.covid.slopes": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_case_slopes",
        "view": "openbb_terminal.alternative.covid.covid_view.display_case_slopes",
    },
    "alt.covid.global_cases": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_global_cases"
    },
    "alt.covid.global_deaths": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_global_deaths"
    },
    "alt.covid.ov": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_covid_ov",
        "view": "openbb_terminal.alternative.covid.covid_view.display_covid_ov",
    },
    "alt.covid.stat": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_covid_stat",
        "view": "openbb_terminal.alternative.covid.covid_view.display_covid_stat",
    },
    "alt.oss.github_data": {
        "model": "openbb_terminal.alternative.oss.github_model.get_github_data"
    },
    "alt.oss.summary": {
        "model": "openbb_terminal.alternative.oss.github_model.get_repo_summary",
        "view": "openbb_terminal.alternative.oss.github_view.display_repo_summary",
    },
    "alt.oss.history": {
        "model": "openbb_terminal.alternative.oss.github_model.get_stars_history",
        "view": "openbb_terminal.alternative.oss.github_view.display_star_history",
    },
    "alt.oss.top": {
        "model": "openbb_terminal.alternative.oss.github_model.get_top_repos",
        "view": "openbb_terminal.alternative.oss.github_view.display_top_repos",
    },
    "alt.oss.search": {
        "model": "openbb_terminal.alternative.oss.github_model.search_repos"
    },
    "alt.oss._make_request": {
        "model": "openbb_terminal.alternative.oss.runa_model._make_request"
    },
    "alt.oss._retry_session": {
        "model": "openbb_terminal.alternative.oss.runa_model._retry_session"
    },
    "alt.oss.ross": {
        "model": "openbb_terminal.alternative.oss.runa_model.get_startups",
        "view": "openbb_terminal.alternative.oss.runa_view.display_rossindex",
    },
    "stocks.ba.headlines": {
        "model": "openbb_terminal.common.behavioural_analysis.finbrain_model.get_sentiment",
        "view": "openbb_terminal.common.behavioural_analysis.finbrain_view.display_sentiment_analysis",
    },
    "stocks.ba.mentions": {
        "model": "openbb_terminal.common.behavioural_analysis.google_model.get_mentions",
        "view": "openbb_terminal.common.behavioural_analysis.google_view.display_mentions",
    },
    "stocks.ba.queries": {
        "model": "openbb_terminal.common.behavioural_analysis.google_model.get_queries"
    },
    "stocks.ba.regions": {
        "model": "openbb_terminal.common.behavioural_analysis.google_model.get_regions",
        "view": "openbb_terminal.common.behavioural_analysis.google_view.display_regions",
    },
    "stocks.ba.rise": {
        "model": "openbb_terminal.common.behavioural_analysis.google_model.get_rise"
    },
    "stocks.ba.getdd": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_due_dilligence"
    },
    "stocks.ba.popular": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_popular_tickers",
        "view": "openbb_terminal.common.behavioural_analysis.reddit_view.display_popular_tickers",
    },
    "stocks.ba.redditsent": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_posts_about",
        "view": "openbb_terminal.common.behavioural_analysis.reddit_view.display_redditsent",
    },
    "stocks.ba.text_sent": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_sentiment"
    },
    "stocks.ba.spac": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_spac"
    },
    "stocks.ba.spacc": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_spac_community"
    },
    "stocks.ba.watchlist": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_watchlists",
        "view": "openbb_terminal.common.behavioural_analysis.reddit_view.display_watchlist",
    },
    "stocks.ba.wsb": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_wsb_community"
    },
    "stocks.ba.hist": {
        "model": "openbb_terminal.common.behavioural_analysis.sentimentinvestor_model.get_historical",
        "view": "openbb_terminal.common.behavioural_analysis.sentimentinvestor_view.display_historical",
    },
    "stocks.ba.trend": {
        "model": "openbb_terminal.common.behavioural_analysis.sentimentinvestor_model.get_trending",
        "view": "openbb_terminal.common.behavioural_analysis.sentimentinvestor_view.display_trending",
    },
    "stocks.ba.bullbear": {
        "model": "openbb_terminal.common.behavioural_analysis.stocktwits_model.get_bullbear",
        "view": "openbb_terminal.common.behavioural_analysis.stocktwits_view.display_bullbear",
    },
    "stocks.ba.messages": {
        "model": "openbb_terminal.common.behavioural_analysis.stocktwits_model.get_messages",
        "view": "openbb_terminal.common.behavioural_analysis.stocktwits_view.display_messages",
    },
    "stocks.ba.stalker": {
        "model": "openbb_terminal.common.behavioural_analysis.stocktwits_model.get_stalker"
    },
    "stocks.ba.trending": {
        "model": "openbb_terminal.common.behavioural_analysis.stocktwits_model.get_trending"
    },
    "stocks.ba.infer": {
        "model": "openbb_terminal.common.behavioural_analysis.twitter_model.load_analyze_tweets",
        "view": "openbb_terminal.common.behavioural_analysis.twitter_view.display_inference",
    },
    "stocks.ba.sentiment": {
        "model": "openbb_terminal.common.behavioural_analysis.twitter_model.get_sentiment",
        "view": "openbb_terminal.common.behavioural_analysis.twitter_view.display_sentiment",
    },
    "etf.news": {
        "model": "openbb_terminal.common.newsapi_model.get_news",
        "view": "openbb_terminal.common.newsapi_view.display_news",
    },
    "common.news": {
        "model": "openbb_terminal.common.feedparser_model.get_news",
    },
    "common.qa.bw": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_view.display_bw",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_bw",
    },
    "common.qa.calculate_adjusted_var": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.calculate_adjusted_var"
    },
    "common.qa.es": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_es",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_es",
    },
    "common.qa.normality": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_normality",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_normality",
    },
    "common.qa.omega": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_omega",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_omega",
    },
    "common.qa.decompose": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_seasonal_decomposition"
    },
    "common.qa.sharpe": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_sharpe",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_sharpe",
    },
    "common.qa.sortino": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_sortino",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_sortino",
    },
    "common.qa.summary": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_summary",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_summary",
    },
    "common.qa.unitroot": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_unitroot",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_unitroot",
    },
    "common.qa.var": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_var",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_var",
    },
    "common.qa.kurtosis": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_kurtosis",
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_kurtosis",
    },
    "common.qa.quantile": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_quantile",
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_quantile",
    },
    "common.qa.rolling": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_rolling_avg",
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_mean_std",
    },
    "common.qa.skew": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_skew",
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_skew",
    },
    "common.qa.spread": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_spread",
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_spread",
    },
    "common.ta.fib": {
        "model": "openbb_terminal.common.technical_analysis.custom_indicators_model.calculate_fib_levels",
        "view": "openbb_terminal.common.technical_analysis.custom_indicators_view.fibonacci_retracement",
    },
    "common.ta.cci": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.cci",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_cci",
    },
    "common.ta.cg": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.cg",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_cg",
    },
    "common.ta.fisher": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.fisher",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_fisher",
    },
    "common.ta.macd": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.macd",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_macd",
    },
    "common.ta.rsi": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.rsi",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_rsi",
    },
    "common.ta.stoch": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.stoch",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_stoch",
    },
    "common.ta.ma": {
        "model": "openbb_terminal.common.technical_analysis.overlap_view.view_ma",
        "view": "openbb_terminal.common.technical_analysis.overlap_view.view_ma",
    },
    "common.ta.ema": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.ema"
    },
    "common.ta.hma": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.hma"
    },
    "common.ta.sma": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.sma"
    },
    "common.ta.vwap": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.vwap",
        "view": "openbb_terminal.common.technical_analysis.overlap_view.view_vwap",
    },
    "common.ta.wma": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.wma"
    },
    "common.ta.zlma": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.zlma"
    },
    "common.ta.adx": {
        "model": "openbb_terminal.common.technical_analysis.trend_indicators_model.adx",
        "view": "openbb_terminal.common.technical_analysis.trend_indicators_view.display_adx",
    },
    "common.ta.aroon": {
        "model": "openbb_terminal.common.technical_analysis.trend_indicators_model.aroon",
        "view": "openbb_terminal.common.technical_analysis.trend_indicators_view.display_aroon",
    },
    "common.ta.bbands": {
        "model": "openbb_terminal.common.technical_analysis.volatility_model.bbands",
        "view": "openbb_terminal.common.technical_analysis.volatility_view.display_bbands",
    },
    "common.ta.donchian": {
        "model": "openbb_terminal.common.technical_analysis.volatility_model.donchian",
        "view": "openbb_terminal.common.technical_analysis.volatility_view.display_donchian",
    },
    "common.ta.kc": {
        "model": "openbb_terminal.common.technical_analysis.volatility_model.kc",
        "view": "openbb_terminal.common.technical_analysis.volatility_view.view_kc",
    },
    "common.ta.ad": {
        "model": "openbb_terminal.common.technical_analysis.volume_model.ad",
        "view": "openbb_terminal.common.technical_analysis.volume_view.display_ad",
    },
    "common.ta.adosc": {
        "model": "openbb_terminal.common.technical_analysis.volume_model.adosc",
        "view": "openbb_terminal.common.technical_analysis.volume_view.display_adosc",
    },
    "common.ta.obv": {
        "model": "openbb_terminal.common.technical_analysis.volume_model.obv",
        "view": "openbb_terminal.common.technical_analysis.volume_view.display_obv",
    },
    "common.ta.atr": {
        "model": "openbb_terminal.common.technical_analysis.volatility_model.atr",
        "view": "openbb_terminal.common.technical_analysis.volatility_view.display_atr",
    },
    "crypto.defi.vaults": {
        "model": "openbb_terminal.cryptocurrency.defi.coindix_model.get_defi_vaults",
        "view": "openbb_terminal.cryptocurrency.defi.coindix_view.display_defi_vaults",
    },
    "crypto.defi.anchor_data": {
        "model": "openbb_terminal.cryptocurrency.defi.cryptosaurio_model.get_anchor_data",
        "view": "openbb_terminal.cryptocurrency.defi.cryptosaurio_view.display_anchor_data",
    },
    "crypto.defi.swaps": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_last_uni_swaps",
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_last_uni_swaps",
    },
    "crypto.defi.pools": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_uni_pools_by_volume",
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_uni_pools",
    },
    "crypto.defi.tokens": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_uni_tokens",
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_uni_tokens",
    },
    "crypto.defi.pairs": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_uniswap_pool_recently_added",
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_recently_added",
    },
    "crypto.defi.stats": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_uniswap_stats",
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_uni_stats",
    },
    "crypto.defi.dtvl": {
        "model": "openbb_terminal.cryptocurrency.defi.llama_model.get_defi_protocol",
        "view": "openbb_terminal.cryptocurrency.defi.llama_view.display_historical_tvl",
    },
    "crypto.defi.ldapps": {
        "model": "openbb_terminal.cryptocurrency.defi.llama_model.get_defi_protocols",
        "view": "openbb_terminal.cryptocurrency.defi.llama_view.display_defi_protocols",
    },
    "crypto.defi.stvl": {
        "model": "openbb_terminal.cryptocurrency.defi.llama_model.get_defi_tvl",
        "view": "openbb_terminal.cryptocurrency.defi.llama_view.display_defi_tvl",
    },
    "crypto.defi.gdapps": {
        "model": "openbb_terminal.cryptocurrency.defi.llama_model.get_grouped_defi_protocols",
        "view": "openbb_terminal.cryptocurrency.defi.llama_view.display_grouped_defi_protocols",
    },
    "crypto.defi.luna_supply": {
        "model": "openbb_terminal.cryptocurrency.defi.smartstake_model.get_luna_supply_stats",
        "view": "openbb_terminal.cryptocurrency.defi.smartstake_view.display_luna_circ_supply_change",
    },
    "crypto.defi.newsletters": {
        "model": "openbb_terminal.cryptocurrency.defi.substack_model.get_newsletters",
        "view": "openbb_terminal.cryptocurrency.defi.substack_view.display_newsletters",
    },
    "crypto.defi.aterra": {
        "model": "openbb_terminal.cryptocurrency.defi.terraengineer_model.get_history_asset_from_terra_address",
        "view": "openbb_terminal.cryptocurrency.defi.terraengineer_view.display_terra_asset_history",
    },
    "crypto.defi.ayr": {
        "model": "openbb_terminal.cryptocurrency.defi.terraengineer_model.get_anchor_yield_reserve",
        "view": "openbb_terminal.cryptocurrency.defi.terraengineer_view.display_anchor_yield_reserve",
    },
    "crypto.defi.gacc": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_account_growth",
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_account_growth",
    },
    "crypto.defi.gov_proposals": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_proposals",
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_gov_proposals",
    },
    "crypto.defi.sinfo": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_staking_account_info",
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_account_staking_info",
    },
    "crypto.defi.sratio": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_staking_ratio_history",
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_staking_ratio_history",
    },
    "crypto.defi.sreturn": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_staking_returns_history",
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_staking_returns_history",
    },
    "crypto.defi.validators": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_validators",
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_validators",
    },
    "crypto.disc.cmctop": {
        "model": "openbb_terminal.cryptocurrency.discovery.coinmarketcap_model.get_cmc_top_n",
        "view": "openbb_terminal.cryptocurrency.discovery.coinmarketcap_view.display_cmc_top_coins",
    },
    "crypto.disc.cpsearch": {
        "model": "openbb_terminal.cryptocurrency.discovery.coinpaprika_model.get_search_results",
        "view": "openbb_terminal.cryptocurrency.discovery.coinpaprika_view.display_search_results",
    },
    "crypto.disc.top_dapps": {
        "model": "openbb_terminal.cryptocurrency.discovery.dappradar_model.get_top_dapps",
        "view": "openbb_terminal.cryptocurrency.discovery.dappradar_view.display_top_dapps",
    },
    "crypto.disc.top_dexes": {
        "model": "openbb_terminal.cryptocurrency.discovery.dappradar_model.get_top_dexes",
        "view": "openbb_terminal.cryptocurrency.discovery.dappradar_view.display_top_dexes",
    },
    "crypto.disc.top_games": {
        "model": "openbb_terminal.cryptocurrency.discovery.dappradar_model.get_top_games",
        "view": "openbb_terminal.cryptocurrency.discovery.dappradar_view.display_top_games",
    },
    "crypto.disc.top_nfts": {
        "model": "openbb_terminal.cryptocurrency.discovery.dappradar_model.get_top_nfts",
        "view": "openbb_terminal.cryptocurrency.discovery.dappradar_view.display_top_nfts",
    },
    "crypto.disc.categories_keys": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_categories_keys"
    },
    "crypto.disc.coin_list": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_coin_list"
    },
    "crypto.disc.coins": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_coins",
        "view": "openbb_terminal.cryptocurrency.discovery.pycoingecko_view.display_coins",
    },
    "crypto.disc.coins_for_given_exchange": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_coins_for_given_exchange"
    },
    "crypto.disc.gainers_or_losers": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_gainers_or_losers"
    },
    "crypto.disc.gainers": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_gainers",
        "view": "openbb_terminal.cryptocurrency.discovery.pycoingecko_view.display_gainers",
    },
    "crypto.disc.losers": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_losers",
        "view": "openbb_terminal.cryptocurrency.discovery.pycoingecko_view.display_losers",
    },
    "crypto.disc.trending": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_trending_coins",
        "view": "openbb_terminal.cryptocurrency.discovery.pycoingecko_view.display_trending",
    },
    "crypto.dd.trading_pairs": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.binance_model._get_trading_pairs"
    },
    "crypto.dd.check_valid_binance_str": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.binance_model.check_valid_binance_str"
    },
    "crypto.dd.all_binance_trading_pairs": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.binance_model.get_all_binance_trading_pairs"
    },
    "crypto.dd.binance_available_quotes_for_each_coin": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.binance_model.get_binance_available_quotes_for_each_coin"
    },
    "crypto.dd.balance": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.binance_view.get_balance",
        "view": "openbb_terminal.cryptocurrency.due_diligence.binance_view.display_balance",
    },
    "crypto.dd.ob": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.ccxt_model.get_orderbook",
        "view": "openbb_terminal.cryptocurrency.due_diligence.ccxt_view.display_order_book",
    },
    "crypto.dd.show_available_pairs_for_given_symbol": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.show_available_pairs_for_given_symbol"
    },
    "crypto.dd.exchanges": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.ccxt_model.get_exchanges"
    },
    "crypto.dd.candles": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_candles",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinbase_view.display_candles",
    },
    "crypto.dd.stats": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_product_stats",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinbase_view.display_stats",
    },
    "crypto.dd.trades": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.ccxt_model.get_trades",
        "view": "openbb_terminal.cryptocurrency.due_diligence.ccxt_view.display_trades",
    },
    "crypto.dd.trading_pair_info": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_trading_pair_info"
    },
    "crypto.dd.oi": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinglass_model.get_open_interest_per_exchange",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinglass_view.display_open_interest",
    },
    "crypto.dd.basic": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.basic_coin_info",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_basic",
    },
    "crypto.dd.coin": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin"
    },
    "crypto.dd.events": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_events_by_id",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_events",
    },
    "crypto.dd.ex": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_exchanges_by_id",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_exchanges",
    },
    "crypto.dd.mkt": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_markets_by_id",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_markets",
    },
    "crypto.dd.twitter": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_twitter_timeline",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_twitter",
    },
    "crypto.dd.ohlc_historical": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_ohlc_historical"
    },
    "crypto.dd.ps": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_tickers_info_for_coin",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_price_supply",
    },
    "crypto.dd.news": {
        "model": "openbb_terminal.cryptocurrency.overview.cryptopanic_model.get_news",
        "view": "openbb_terminal.cryptocurrency.due_diligence.cryptopanic_view.display_news",
    },
    "crypto.dd.headlines": {
        "model": "openbb_terminal.common.behavioural_analysis.finbrain_model.get_sentiment",
        "view": "openbb_terminal.cryptocurrency.due_diligence.finbrain_crypto_view.display_crypto_sentiment_analysis",
    },
    "crypto.dd.active": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_active_addresses",
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_active_addresses",
    },
    "crypto.dd.close": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_close_price",
    },
    "crypto.dd.eb": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_exchange_balances",
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_exchange_balances",
    },
    "crypto.dd.change": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_exchange_net_position_change",
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_exchange_net_position_change",
    },
    "crypto.onchain.hr": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_hashrate",
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_hashrate",
    },
    "crypto.dd.nonzero": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_non_zero_addresses",
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_non_zero_addresses",
    },
    "crypto.dd.get_mt": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_available_timeseries",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_messari_timeseries_list",
    },
    "crypto.dd.fr": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_fundraising",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_fundraising",
    },
    "crypto.dd.gov": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_governance",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_governance",
    },
    "crypto.dd.inv": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_investors",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_investors",
    },
    "crypto.dd.links": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_links",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_links",
    },
    "crypto.dd.mcapdom": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_marketcap_dominance",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_marketcap_dominance",
    },
    "crypto.dd.mt": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_messari_timeseries",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_messari_timeseries",
    },
    "crypto.dd.pi": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_project_product_info",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_project_info",
    },
    "crypto.dd.rm": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_roadmap",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_roadmap",
    },
    "crypto.dd.team": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_team",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_team",
    },
    "crypto.dd.tk": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_tokenomics",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_tokenomics",
    },
    "crypto.dd.coin_market_chart": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_coin_market_chart"
    },
    "crypto.dd.pr": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_coin_potential_returns",
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_coin_potential_returns",
    },
    "crypto.dd.tokenomics": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_coin_tokenomics"
    },
    "crypto.dd.gh": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.santiment_model.get_github_activity",
        "view": "openbb_terminal.cryptocurrency.due_diligence.santiment_view.display_github_activity",
    },
    "crypto.nft.stats": {
        "model": "openbb_terminal.cryptocurrency.nft.opensea_model.get_collection_stats",
        "view": "openbb_terminal.cryptocurrency.nft.opensea_view.display_collection_stats",
    },
    "crypto.nft.fp": {
        "model": "openbb_terminal.cryptocurrency.nft.nftpricefloor_model.get_floor_price",
        "view": "openbb_terminal.cryptocurrency.nft.nftpricefloor_view.display_floor_price",
    },
    "crypto.nft.collections": {
        "model": "openbb_terminal.cryptocurrency.nft.nftpricefloor_model.get_collections",
        "view": "openbb_terminal.cryptocurrency.nft.nftpricefloor_view.display_collections",
    },
    "crypto.onchain.dvcp": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_daily_dex_volume_for_given_pair",
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_daily_volume_for_given_pair",
    },
    "crypto.onchain.lt": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_dex_trades_by_exchange",
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_dex_trades",
    },
    "crypto.onchain.dex_trades_monthly": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_dex_trades_monthly"
    },
    "crypto.onchain.erc20_tokens": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_erc20_tokens"
    },
    "crypto.onchain.ueat": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_ethereum_unique_senders",
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_ethereum_unique_senders",
    },
    "crypto.onchain.ttcp": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_most_traded_pairs",
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_most_traded_pairs",
    },
    "crypto.onchain.baas": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_spread_for_crypto_pair",
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_spread_for_crypto_pair",
    },
    "crypto.onchain.tv": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_token_volume_on_dexes",
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_dex_volume_for_token",
    },
    "crypto.onchain.query_graph": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.query_graph"
    },
    "crypto.onchain.btc_supply": {
        "model": "openbb_terminal.cryptocurrency.onchain.blockchain_model.get_btc_circulating_supply",
        "view": "openbb_terminal.cryptocurrency.onchain.blockchain_view.display_btc_circulating_supply",
    },
    "crypto.onchain.btc_transac": {
        "model": "openbb_terminal.cryptocurrency.onchain.blockchain_model.get_btc_confirmed_transactions",
        "view": "openbb_terminal.cryptocurrency.onchain.blockchain_view.display_btc_confirmed_transactions",
    },
    "crypto.onchain.gwei": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethgasstation_model.get_gwei_fees",
        "view": "openbb_terminal.cryptocurrency.onchain.ethgasstation_view.display_gwei_fees",
    },
    "crypto.onchain.hist": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_address_history",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_address_history",
    },
    "crypto.onchain.balance": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_address_info",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_address_info",
    },
    "crypto.onchain.token_decimals": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_decimals"
    },
    "crypto.onchain.prices": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_historical_price",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_token_historical_prices",
    },
    "crypto.onchain.th": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_history",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_token_history",
    },
    "crypto.onchain.info": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_info",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_token_info",
    },
    "crypto.onchain.holders": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_top_token_holders",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_top_token_holders",
    },
    "crypto.onchain.top": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_top_tokens",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_top_tokens",
    },
    "crypto.onchain.tx": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_tx_info",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_tx_info",
    },
    "crypto.onchain.whales": {
        "model": "openbb_terminal.cryptocurrency.onchain.whale_alert_model.get_whales_transactions",
        "view": "openbb_terminal.cryptocurrency.onchain.whale_alert_view.display_whales_transactions",
    },
    "crypto.ov.altindex": {
        "model": "openbb_terminal.cryptocurrency.overview.blockchaincenter_model.get_altcoin_index",
        "view": "openbb_terminal.cryptocurrency.overview.blockchaincenter_view.display_altcoin_index",
    },
    "crypto.ov.btcrb": {
        "model": "openbb_terminal.cryptocurrency.overview.glassnode_model.get_btc_rainbow",
        "view": "openbb_terminal.cryptocurrency.overview.glassnode_view.display_btc_rainbow",
    },
    "crypto.ov.cbpairs": {
        "model": "openbb_terminal.cryptocurrency.overview.coinbase_model.get_trading_pairs",
        "view": "openbb_terminal.cryptocurrency.overview.coinbase_view.display_trading_pairs",
    },
    "crypto.ov.cpplatforms": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_all_contract_platforms",
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_all_platforms",
    },
    "crypto.ov.cpinfo": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_coins_info",
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_all_coins_info",
    },
    "crypto.ov.cpmarkets": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_coins_market_info",
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_all_coins_market_info",
    },
    "crypto.ov.cpcontracts": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_contract_platform",
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_contracts",
    },
    "crypto.ov.cpexmarkets": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_exchanges_market",
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_exchange_markets",
    },
    "crypto.ov.cpglobal": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_global_market",
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_global_market",
    },
    "crypto.ov.list_of_coins": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_list_of_coins"
    },
    "crypto.ov.cpexchanges": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_list_of_exchanges",
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_all_exchanges",
    },
    "crypto.ov.news": {
        "model": "openbb_terminal.cryptocurrency.overview.cryptopanic_model.get_news",
        "view": "openbb_terminal.cryptocurrency.overview.cryptopanic_view.display_news",
    },
    "crypto.ov.cr": {
        "model": "openbb_terminal.cryptocurrency.overview.loanscan_model.get_rates",
        "view": "openbb_terminal.cryptocurrency.overview.loanscan_view.display_crypto_rates",
    },
    "crypto.ov.cgderivatives": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_derivatives",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_derivatives",
    },
    "crypto.ov.cgexrates": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_exchange_rates",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_exchange_rates",
    },
    "crypto.ov.exchanges": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_exchanges",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_exchanges",
    },
    "crypto.ov.cgproducts": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_finance_products",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_products",
    },
    "crypto.ov.platforms": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_financial_platforms",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_platforms",
    },
    "crypto.ov.cgdefi": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_global_defi_info",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_global_defi_info",
    },
    "crypto.ov.global_info": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_global_info"
    },
    "crypto.ov.cgglobal": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_global_markets_info",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_global_market_info",
    },
    "crypto.ov.cghold": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_holdings_overview",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_holdings_overview",
    },
    "crypto.ov.cgindexes": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_indexes",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_indexes",
    },
    "crypto.ov.cgstables": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_stable_coins",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_stablecoins",
    },
    "crypto.ov.cgcategories": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_top_crypto_categories",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_categories",
    },
    "crypto.ov.cghm": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_coins",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_crypto_heatmap",
    },
    "crypto.ov.crypto_hack": {
        "model": "openbb_terminal.cryptocurrency.overview.rekt_model.get_crypto_hack"
    },
    "crypto.ov.crypto_hack_slugs": {
        "model": "openbb_terminal.cryptocurrency.overview.rekt_model.get_crypto_hack_slugs"
    },
    "crypto.ov.crypto_hacks": {
        "model": "openbb_terminal.cryptocurrency.overview.rekt_model.get_crypto_hacks",
        "view": "openbb_terminal.cryptocurrency.overview.rekt_view.display_crypto_hacks",
    },
    "crypto.ov.wfpe": {
        "model": "openbb_terminal.cryptocurrency.overview.withdrawalfees_model.get_crypto_withdrawal_fees",
        "view": "openbb_terminal.cryptocurrency.overview.withdrawalfees_view.display_crypto_withdrawal_fees",
    },
    "crypto.ov.ewf": {
        "model": "openbb_terminal.cryptocurrency.overview.withdrawalfees_model.get_overall_exchange_withdrawal_fees",
        "view": "openbb_terminal.cryptocurrency.overview.withdrawalfees_view.display_overall_exchange_withdrawal_fees",
    },
    "crypto.ov.wf": {
        "model": "openbb_terminal.cryptocurrency.overview.withdrawalfees_model.get_overall_withdrawal_fees",
        "view": "openbb_terminal.cryptocurrency.overview.withdrawalfees_view.display_overall_withdrawal_fees",
    },
    "crypto.tools.apy": {
        "model": "openbb_terminal.cryptocurrency.tools.tools_model.calculate_apy",
        "view": "openbb_terminal.cryptocurrency.tools.tools_view.display_apy",
    },
    "crypto.tools.il": {
        "model": "openbb_terminal.cryptocurrency.tools.tools_model.calculate_il",
        "view": "openbb_terminal.cryptocurrency.tools.tools_view.display_il",
    },
    "econometrics.clean": {
        "model": "openbb_terminal.econometrics.econometrics_model.clean"
    },
    "econometrics.coint": {
        "model": "openbb_terminal.econometrics.econometrics_model.get_engle_granger_two_step_cointegration_test",
        "view": "openbb_terminal.econometrics.econometrics_view.display_cointegration_test",
    },
    "econometrics.granger": {
        "model": "openbb_terminal.econometrics.econometrics_model.get_granger_causality",
        "view": "openbb_terminal.econometrics.econometrics_view.display_granger",
    },
    "econometrics.norm": {
        "model": "openbb_terminal.econometrics.econometrics_model.get_normality",
        "view": "openbb_terminal.econometrics.econometrics_view.display_norm",
    },
    "econometrics.options": {
        "model": "openbb_terminal.econometrics.econometrics_model.get_options",
        "view": "openbb_terminal.econometrics.econometrics_view.show_options",
    },
    "econometrics.root": {
        "model": "openbb_terminal.econometrics.econometrics_model.get_root",
        "view": "openbb_terminal.econometrics.econometrics_view.display_root",
    },
    "econometrics.load": {"model": "openbb_terminal.common.common_model.load"},
    "econometrics.bgod": {
        "model": "openbb_terminal.econometrics.regression_model.get_bgod",
        "view": "openbb_terminal.econometrics.regression_view.display_bgod",
    },
    "econometrics.bols": {
        "model": "openbb_terminal.econometrics.regression_model.get_bols"
    },
    "econometrics.bpag": {
        "model": "openbb_terminal.econometrics.regression_model.get_bpag",
        "view": "openbb_terminal.econometrics.regression_view.display_bpag",
    },
    "econometrics.comparison": {
        "model": "openbb_terminal.econometrics.regression_model.get_comparison"
    },
    "econometrics.dwat": {
        "model": "openbb_terminal.econometrics.regression_model.get_dwat",
        "view": "openbb_terminal.econometrics.regression_view.display_dwat",
    },
    "econometrics.fdols": {
        "model": "openbb_terminal.econometrics.regression_model.get_fdols"
    },
    "econometrics.fe": {
        "model": "openbb_terminal.econometrics.regression_model.get_fe"
    },
    "econometrics.ols": {
        "model": "openbb_terminal.econometrics.regression_model.get_ols"
    },
    "econometrics.pols": {
        "model": "openbb_terminal.econometrics.regression_model.get_pols"
    },
    "econometrics.re": {
        "model": "openbb_terminal.econometrics.regression_model.get_re"
    },
    "econometrics.get_regression_data": {
        "model": "openbb_terminal.econometrics.regression_model.get_regression_data"
    },
    "econometrics.panel": {
        "model": "openbb_terminal.econometrics.regression_model.get_regressions_results",
        "view": "openbb_terminal.econometrics.regression_view.display_panel",
    },
    "economy.cpi": {
        "model": "openbb_terminal.economy.alphavantage_model.get_cpi",
        "view": "openbb_terminal.economy.alphavantage_view.display_cpi",
    },
    "economy.gdpc": {
        "model": "openbb_terminal.economy.alphavantage_model.get_gdp_capita",
        "view": "openbb_terminal.economy.alphavantage_view.display_gdp_capita",
    },
    "economy.inf": {
        "model": "openbb_terminal.economy.alphavantage_model.get_inflation",
        "view": "openbb_terminal.economy.alphavantage_view.display_inflation",
    },
    "economy.gdp": {
        "model": "openbb_terminal.economy.alphavantage_model.get_real_gdp",
        "view": "openbb_terminal.economy.alphavantage_view.display_real_gdp",
    },
    "economy.rtps": {
        "model": "openbb_terminal.economy.alphavantage_model.get_sector_data",
        "view": "openbb_terminal.economy.alphavantage_view.realtime_performance_sector",
    },
    "economy.tyld": {
        "model": "openbb_terminal.economy.alphavantage_model.get_treasury_yield",
        "view": "openbb_terminal.economy.alphavantage_view.display_treasury_yield",
    },
    "economy.unemp": {
        "model": "openbb_terminal.economy.alphavantage_model.get_unemployment",
        "view": "openbb_terminal.economy.alphavantage_view.display_unemployment",
    },
    "economy.macro": {
        "model": "openbb_terminal.economy.econdb_model.get_aggregated_macro_data",
        "view": "openbb_terminal.economy.econdb_view.show_macro_data",
    },
    "economy.macro_parameters": {
        "model": "openbb_terminal.economy.econdb_model.get_macro_parameters"
    },
    "economy.macro_countries": {
        "model": "openbb_terminal.economy.econdb_model.get_macro_countries"
    },
    "economy.treasury": {
        "model": "openbb_terminal.economy.econdb_model.get_treasuries",
        "view": "openbb_terminal.economy.econdb_view.show_treasuries",
    },
    "economy.treasury_maturities": {
        "model": "openbb_terminal.economy.econdb_model.get_treasury_maturities"
    },
    "economy.future": {"model": "openbb_terminal.economy.finviz_model.get_futures"},
    "economy.spectrum": {
        "model": "openbb_terminal.economy.finviz_model.get_spectrum_data",
        "view": "openbb_terminal.economy.finviz_view.display_spectrum",
    },
    "economy.valuation": {
        "model": "openbb_terminal.economy.finviz_model.get_valuation_data"
    },
    "economy.performance": {
        "model": "openbb_terminal.economy.finviz_model.get_performance_data"
    },
    "economy.perfmap": {
        "model": "openbb_terminal.economy.finviz_model.get_performance_map"
    },
    "economy.fred_series": {
        "model": "openbb_terminal.economy.fred_model.get_aggregated_series_data",
        "view": "openbb_terminal.economy.fred_view.display_fred_series",
    },
    "economy.fred_ids": {"model": "openbb_terminal.economy.fred_model.get_series_ids"},
    "economy.fred_notes": {
        "model": "openbb_terminal.economy.fred_model.get_series_notes"
    },
    "economy.fred_yield_curve": {
        "model": "openbb_terminal.economy.fred_model.get_yield_curve",
        "view": "openbb_terminal.economy.fred_view.display_yield_curve",
    },
    "economy.get_events_countries": {
        "model": "openbb_terminal.economy.investingcom_model.get_events_countries"
    },
    "economy.events": {
        "model": "openbb_terminal.economy.nasdaq_model.get_economic_calendar"
    },
    "economy.get_ycrv_countries": {
        "model": "openbb_terminal.economy.investingcom_model.get_ycrv_countries"
    },
    "economy.ycrv": {
        "model": "openbb_terminal.economy.fred_model.get_yield_curve",
        "view": "openbb_terminal.economy.fred_view.display_yield_curve",
    },
    "economy.country_codes": {
        "model": "openbb_terminal.economy.nasdaq_model.get_country_codes"
    },
    "economy.bigmac": {
        "model": "openbb_terminal.economy.nasdaq_model.get_big_mac_indices",
        "view": "openbb_terminal.economy.nasdaq_view.display_big_mac_index",
    },
    "economy.glbonds": {"model": "openbb_terminal.economy.wsj_model.global_bonds"},
    "economy.currencies": {
        "model": "openbb_terminal.economy.wsj_model.global_currencies"
    },
    "economy.overview": {"model": "openbb_terminal.economy.wsj_model.market_overview"},
    "economy.futures": {"model": "openbb_terminal.economy.wsj_model.top_commodities"},
    "economy.usbonds": {"model": "openbb_terminal.economy.wsj_model.us_bonds"},
    "economy.indices": {"model": "openbb_terminal.economy.wsj_model.us_indices"},
    "economy.index": {
        "model": "openbb_terminal.economy.yfinance_model.get_indices",
        "view": "openbb_terminal.economy.yfinance_view.show_indices",
    },
    "economy.available_indices": {
        "model": "openbb_terminal.economy.yfinance_model.get_available_indices"
    },
    "economy.search_index": {
        "model": "openbb_terminal.economy.yfinance_model.get_search_indices"
    },
    "etf.disc.mover": {
        "model": "openbb_terminal.etf.discovery.wsj_model.etf_movers",
        "view": "openbb_terminal.etf.discovery.wsj_view.show_top_mover",
    },
    "etf.etf_by_category": {
        "model": "openbb_terminal.etf.financedatabase_model.get_etfs_by_category",
        "view": "openbb_terminal.etf.financedatabase_view.display_etf_by_category",
    },
    "etf.ld": {
        "model": "openbb_terminal.etf.financedatabase_model.get_etfs_by_description",
        "view": "openbb_terminal.etf.financedatabase_view.display_etf_by_description",
    },
    "etf.ln": {
        "model": "openbb_terminal.etf.financedatabase_model.get_etfs_by_name",
        "view": "openbb_terminal.etf.financedatabase_view.display_etf_by_name",
    },
    "etf.scr.screen": {
        "model": "openbb_terminal.etf.screener.screener_model.etf_screener",
        "view": "openbb_terminal.etf.screener.screener_view.view_screener",
    },
    "etf.holdings": {
        "model": "openbb_terminal.etf.stockanalysis_model.get_etf_holdings",
        "view": "openbb_terminal.etf.stockanalysis_view.view_holdings",
    },
    "etf.symbols": {
        "model": "openbb_terminal.etf.stockanalysis_model.get_all_names_symbols"
    },
    "etf.overview": {
        "model": "openbb_terminal.etf.stockanalysis_model.get_etf_overview",
        "view": "openbb_terminal.etf.stockanalysis_view.view_overview",
    },
    "etf.etf_by_name": {
        "model": "openbb_terminal.etf.stockanalysis_model.get_etfs_by_name",
        "view": "openbb_terminal.etf.stockanalysis_view.display_etf_by_name",
    },
    "etf.weights": {
        "model": "openbb_terminal.etf.yfinance_model.get_etf_sector_weightings",
        "view": "openbb_terminal.etf.yfinance_view.display_etf_weightings",
    },
    "etf.summary": {
        "model": "openbb_terminal.etf.yfinance_model.get_etf_summary_description",
        "view": "openbb_terminal.etf.yfinance_view.display_etf_description",
    },
    "forex.get_currency_list": {
        "model": "openbb_terminal.forex.av_model.get_currency_list",
    },
    "forex.hist": {
        "model": "openbb_terminal.forex.av_model.get_historical",
    },
    "forex.quote": {
        "model": "openbb_terminal.forex.av_model.get_quote",
        "view": "openbb_terminal.forex.av_view.display_quote",
    },
    "forex.oanda.fwd": {
        "model": "openbb_terminal.forex.fxempire_model.get_forward_rates",
        "view": "openbb_terminal.forex.fxempire_view.display_forward_rates",
    },
    "forex.oanda.summary": {
        "model": "openbb_terminal.forex.oanda.oanda_model.account_summary_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.get_account_summary",
    },
    "forex.oanda.cancel": {
        "model": "openbb_terminal.forex.oanda.oanda_model.cancel_pending_order_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.cancel_pending_order",
    },
    "forex.oanda.close": {
        "model": "openbb_terminal.forex.oanda.oanda_model.close_trades_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.close_trade",
    },
    "forex.oanda.order": {
        "model": "openbb_terminal.forex.oanda.oanda_model.create_order_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.create_order",
    },
    "forex.oanda.price": {
        "model": "openbb_terminal.forex.oanda.oanda_model.fx_price_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.get_fx_price",
    },
    "forex.oanda.calendar": {
        "model": "openbb_terminal.forex.oanda.oanda_model.get_calendar_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.calendar",
    },
    "forex.oanda.candles": {
        "model": "openbb_terminal.forex.oanda.oanda_model.get_candles_dataframe",
        "view": "openbb_terminal.forex.oanda.oanda_view.show_candles",
    },
    "forex.oanda.openpositions": {
        "model": "openbb_terminal.forex.oanda.oanda_model.open_positions_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.get_open_positions",
    },
    "forex.oanda.opentrades": {
        "model": "openbb_terminal.forex.oanda.oanda_model.open_trades_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.get_open_trades",
    },
    "forex.oanda.listorders": {
        "model": "openbb_terminal.forex.oanda.oanda_model.order_history_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.list_orders",
    },
    "forex.oanda.orderbook": {
        "model": "openbb_terminal.forex.oanda.oanda_model.orderbook_plot_data_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.get_order_book",
    },
    "forex.oanda.pending": {
        "model": "openbb_terminal.forex.oanda.oanda_model.pending_orders_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.get_pending_orders",
    },
    "forex.oanda.positionbook": {
        "model": "openbb_terminal.forex.oanda.oanda_model.positionbook_plot_data_request",
        "view": "openbb_terminal.forex.oanda.oanda_view.get_position_book",
    },
    "portfolio.holdv": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_holdings_value",
        "view": "openbb_terminal.portfolio.portfolio_view.display_holdings_value",
    },
    "portfolio.holdp": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_holdings_percentage",
        "view": "openbb_terminal.portfolio.portfolio_view.display_holdings_percentage",
    },
    "portfolio.yret": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_yearly_returns",
        "view": "openbb_terminal.portfolio.portfolio_view.display_yearly_returns",
    },
    "portfolio.mret": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_monthly_returns",
        "view": "openbb_terminal.portfolio.portfolio_view.display_monthly_returns",
    },
    "portfolio.dret": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_daily_returns",
        "view": "openbb_terminal.portfolio.portfolio_view.display_daily_returns",
    },
    "portfolio.max_drawdown_ratio": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_maximum_drawdown",
        "view": "openbb_terminal.portfolio.portfolio_view.display_maximum_drawdown_ratio",
    },
    "portfolio.distr": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_distribution_returns",
        "view": "openbb_terminal.portfolio.portfolio_view.display_distribution_returns",
    },
    "portfolio.maxdd": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_maximum_drawdown",
        "view": "openbb_terminal.portfolio.portfolio_view.display_maximum_drawdown",
    },
    "portfolio.rvol": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_rolling_volatility",
        "view": "openbb_terminal.portfolio.portfolio_view.display_rolling_volatility",
    },
    "portfolio.rsharpe": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_rolling_sharpe",
        "view": "openbb_terminal.portfolio.portfolio_view.display_rolling_sharpe",
    },
    "portfolio.rsortino": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_rolling_sortino",
        "view": "openbb_terminal.portfolio.portfolio_view.display_rolling_sortino",
    },
    "portfolio.rbeta": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_rolling_beta",
        "view": "openbb_terminal.portfolio.portfolio_view.display_rolling_beta",
    },
    "portfolio.summary": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_summary",
    },
    "portfolio.skew": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_skewness",
    },
    "portfolio.kurtosis": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_kurtosis",
    },
    "portfolio.volatility": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_volatility",
    },
    "portfolio.sharpe": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_sharpe_ratio",
    },
    "portfolio.sortino": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_sortino_ratio",
    },
    "portfolio.maxdrawdown": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_maximum_drawdown_ratio",
    },
    "portfolio.rsquare": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_r2_score",
    },
    "portfolio.gaintopain": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_gaintopain_ratio",
    },
    "portfolio.trackerr": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_tracking_error",
    },
    "portfolio.information": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_information_ratio",
    },
    "portfolio.tail": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_tail_ratio",
    },
    "portfolio.commonsense": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_common_sense_ratio",
    },
    "portfolio.jensens": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_jensens_alpha",
    },
    "portfolio.calmar": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_calmar_ratio",
    },
    "portfolio.kelly": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_kelly_criterion",
    },
    "portfolio.payoff": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_payoff_ratio",
    },
    "portfolio.profitfactor": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_profit_factor",
    },
    "portfolio.perf": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_performance_vs_benchmark",
    },
    "portfolio.var": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_var",
    },
    "portfolio.es": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_es",
    },
    "portfolio.om": {
        "model": "openbb_terminal.portfolio.portfolio_model.get_omega",
        "view": "openbb_terminal.portfolio.portfolio_view.display_omega",
    },
    "portfolio.po.load": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.excel_model.load_allocation",
    },
    "portfolio.po.load_bl_views": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.excel_model.load_bl_views",
    },
    "portfolio.po.maxsharpe": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_max_sharpe",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_max_sharpe",
    },
    "portfolio.po.minrisk": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_min_risk",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_min_risk",
    },
    "portfolio.po.maxutil": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_max_util",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_max_util",
    },
    "portfolio.po.maxret": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_max_ret",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_max_ret",
    },
    "portfolio.po.maxdiv": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_max_diversification_portfolio",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_max_div",
    },
    "portfolio.po.maxdecorr": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_max_decorrelation_portfolio",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_max_decorr",
    },
    "portfolio.po.blacklitterman": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_black_litterman_portfolio",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_black_litterman",
    },
    "portfolio.po.ef": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_ef",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_ef",
    },
    "portfolio.po.riskparity": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_risk_parity_portfolio",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_risk_parity",
    },
    "portfolio.po.relriskparity": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_rel_risk_parity_portfolio",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_rel_risk_parity",
    },
    "portfolio.po.meanrisk": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_mean_risk_portfolio",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_mean_risk",
    },
    "portfolio.po.hrp": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_hrp",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_hrp",
    },
    "portfolio.po.herc": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_herc",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_herc",
    },
    "portfolio.po.nco": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_nco",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_nco",
    },
    "portfolio.po.hcp": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_hcp_portfolio",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_hcp",
    },
    "portfolio.po.equal": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_equal_weights",
    },
    "portfolio.po.property": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_property_weights",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_property_weighting",
    },
    "portfolio.po.get_properties": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_properties",
    },
    "portfolio.po.plot": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.additional_plots",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.additional_plots",
    },
    # "stocks.bt.emacross": {
    #     "model": "openbb_terminal.stocks.backtesting.bt_model.emacross_strategy",
    #     "view": "openbb_terminal.stocks.backtesting.bt_view.display_emacross",
    # },
    # "stocks.bt.ema": {
    #     "model": "openbb_terminal.stocks.backtesting.bt_model.ema_strategy",
    #     "view": "openbb_terminal.stocks.backtesting.bt_view.display_simple_ema",
    # },
    # "stocks.bt.rsi": {
    #     "model": "openbb_terminal.stocks.backtesting.bt_model.rsi_strategy",
    #     "view": "openbb_terminal.stocks.backtesting.bt_view.display_rsi_strategy",
    # },
    "stocks.ba.cnews": {
        "model": "openbb_terminal.stocks.behavioural_analysis.finnhub_model.get_company_news"
    },
    "stocks.ba.snews": {
        "model": "openbb_terminal.stocks.behavioural_analysis.finnhub_model.get_headlines_sentiment",
        "view": "openbb_terminal.stocks.behavioural_analysis.finnhub_view.display_stock_price_headlines_sentiment",
    },
    "stocks.ca.sentiment": {
        "model": "openbb_terminal.stocks.comparison_analysis.finbrain_model.get_sentiments",
        "view": "openbb_terminal.stocks.comparison_analysis.finbrain_view.display_sentiment_compare",
    },
    "stocks.ca.scorr": {
        "model": "openbb_terminal.stocks.comparison_analysis.finbrain_model.get_sentiment_correlation",
        "view": "openbb_terminal.stocks.comparison_analysis.finbrain_view.display_sentiment_correlation",
    },
    "stocks.ca.finnhub_peers": {
        "model": "openbb_terminal.stocks.comparison_analysis.finnhub_model.get_similar_companies"
    },
    "stocks.ca.screener": {
        "model": "openbb_terminal.stocks.comparison_analysis.finviz_compare_model.get_comparison_data"
    },
    "stocks.ca.finviz_peers": {
        "model": "openbb_terminal.stocks.comparison_analysis.finviz_compare_model.get_similar_companies"
    },
    "stocks.ca.balance": {
        "model": "openbb_terminal.stocks.comparison_analysis.marketwatch_model.get_balance_comparison"
    },
    "stocks.ca.cashflow": {
        "model": "openbb_terminal.stocks.comparison_analysis.marketwatch_model.get_cashflow_comparison"
    },
    "stocks.ca.income": {
        "model": "openbb_terminal.stocks.comparison_analysis.marketwatch_model.get_income_comparison",
        "view": "openbb_terminal.stocks.comparison_analysis.marketwatch_view.display_income_comparison",
    },
    "stocks.ca.polygon_peers": {
        "model": "openbb_terminal.stocks.comparison_analysis.polygon_model.get_similar_companies",
    },
    "stocks.ca.hist": {
        "model": "openbb_terminal.stocks.comparison_analysis.yahoo_finance_model.get_historical",
        "view": "openbb_terminal.stocks.comparison_analysis.yahoo_finance_view.display_historical",
    },
    "stocks.ca.hcorr": {
        "model": "openbb_terminal.stocks.comparison_analysis.yahoo_finance_model.get_correlation",
        "view": "openbb_terminal.stocks.comparison_analysis.yahoo_finance_view.display_correlation",
    },
    "stocks.ca.volume": {
        "model": "openbb_terminal.stocks.comparison_analysis.yahoo_finance_model.get_volume",
        "view": "openbb_terminal.stocks.comparison_analysis.yahoo_finance_view.display_volume",
    },
    "stocks.dps.prom": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.finra_model.getATSdata",
        "view": "openbb_terminal.stocks.dark_pool_shorts.finra_view.darkpool_otc",
    },
    "stocks.dps.dpotc": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.finra_model.getTickerFINRAdata",
        "view": "openbb_terminal.stocks.dark_pool_shorts.finra_view.darkpool_ats_otc",
    },
    "stocks.dps.ctb": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.ibkr_model.get_cost_to_borrow"
    },
    "stocks.dps.volexch": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.nyse_model.get_short_data_by_exchange",
        "view": "openbb_terminal.stocks.dark_pool_shorts.nyse_view.display_short_by_exchange",
    },
    "stocks.dps.psi_q": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.quandl_model.get_short_interest",
        "view": "openbb_terminal.stocks.dark_pool_shorts.quandl_view.short_interest",
    },
    "stocks.dps.ftd": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.sec_model.get_fails_to_deliver",
        "view": "openbb_terminal.stocks.dark_pool_shorts.sec_view.fails_to_deliver",
    },
    "stocks.dps.hsi": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.shortinterest_model.get_high_short_interest"
    },
    "stocks.dps.pos": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_model.get_dark_pool_short_positions"
    },
    "stocks.dps.spos": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_model.get_net_short_position",
        "view": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_view.net_short_position",
    },
    "stocks.dps.sidtc": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_model.get_short_interest_days_to_cover"
    },
    "stocks.dps.psi_sg": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_model.get_short_interest_volume",
        "view": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_view.short_interest_volume",
    },
    "stocks.dps.shorted": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.yahoofinance_model.get_most_shorted"
    },
    "stocks.disc.arkord": {
        "model": "openbb_terminal.stocks.discovery.ark_model.get_ark_orders"
    },
    "stocks.disc.ipo": {
        "model": "openbb_terminal.stocks.discovery.finnhub_model.get_ipo_calendar"
    },
    "stocks.disc.pipo": {
        "model": "openbb_terminal.stocks.discovery.finnhub_model.get_past_ipo"
    },
    "stocks.disc.fipo": {
        "model": "openbb_terminal.stocks.discovery.finnhub_model.get_future_ipo"
    },
    "stocks.disc.dividends": {
        "model": "openbb_terminal.stocks.discovery.nasdaq_model.get_dividend_cal"
    },
    "stocks.disc.rtat": {
        "model": "openbb_terminal.stocks.discovery.nasdaq_model.get_retail_tickers"
    },
    "stocks.disc.news": {
        "model": "openbb_terminal.stocks.discovery.seeking_alpha_model.get_news"
    },
    "stocks.disc.upcoming": {
        "model": "openbb_terminal.stocks.discovery.seeking_alpha_model.get_next_earnings"
    },
    "stocks.disc.trending": {
        "model": "openbb_terminal.stocks.discovery.seeking_alpha_model.get_trending_list"
    },
    "stocks.disc.lowfloat": {
        "model": "openbb_terminal.stocks.discovery.shortinterest_model.get_low_float"
    },
    "stocks.disc.hotpenny": {
        "model": "openbb_terminal.stocks.discovery.shortinterest_model.get_today_hot_penny_stocks"
    },
    "stocks.disc.active": {
        "model": "openbb_terminal.stocks.discovery.yahoofinance_model.get_active"
    },
    "stocks.disc.asc": {
        "model": "openbb_terminal.stocks.discovery.yahoofinance_model.get_asc"
    },
    "stocks.disc.gainers": {
        "model": "openbb_terminal.stocks.discovery.yahoofinance_model.get_gainers"
    },
    "stocks.disc.gtech": {
        "model": "openbb_terminal.stocks.discovery.yahoofinance_model.get_gtech"
    },
    "stocks.disc.losers": {
        "model": "openbb_terminal.stocks.discovery.yahoofinance_model.get_losers"
    },
    "stocks.disc.ugs": {
        "model": "openbb_terminal.stocks.discovery.yahoofinance_model.get_ugs"
    },
    "stocks.disc.ulc": {
        "model": "openbb_terminal.stocks.discovery.yahoofinance_model.get_ulc"
    },
    "stocks.dd.arktrades": {
        "model": "openbb_terminal.stocks.due_diligence.ark_model.get_ark_trades_by_ticker"
    },
    "stocks.dd.est": {
        "model": "openbb_terminal.stocks.due_diligence.business_insider_model.get_estimates"
    },
    "stocks.dd.pt": {
        "model": "openbb_terminal.stocks.due_diligence.business_insider_model.get_price_target_from_analysts",
        "view": "openbb_terminal.stocks.due_diligence.business_insider_view.price_target_from_analysts",
    },
    "stocks.dd.customer": {
        "model": "openbb_terminal.stocks.due_diligence.csimarket_model.get_customers"
    },
    "stocks.dd.supplier": {
        "model": "openbb_terminal.stocks.due_diligence.csimarket_model.get_suppliers"
    },
    "stocks.dd.rot": {
        "model": "openbb_terminal.stocks.due_diligence.finnhub_model.get_rating_over_time",
        "view": "openbb_terminal.stocks.due_diligence.finnhub_view.rating_over_time",
    },
    "stocks.dd.analyst": {
        "model": "openbb_terminal.stocks.due_diligence.finviz_model.get_analyst_data"
    },
    "stocks.dd.news": {
        "model": "openbb_terminal.stocks.due_diligence.finviz_model.get_news"
    },
    "stocks.dd.rating": {
        "model": "openbb_terminal.stocks.due_diligence.fmp_model.get_rating"
    },
    "stocks.dd.sec": {
        "model": "openbb_terminal.stocks.due_diligence.marketwatch_model.get_sec_filings",
        "view": "openbb_terminal.stocks.due_diligence.marketwatch_view.sec_filings",
    },
    "stocks.fa.av_balance": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_balance_sheet"
    },
    "stocks.fa.av_cash": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_cash_flow",
        "view": "openbb_terminal.stocks.fundamental_analysis.av_view.display_cash_flow",
    },
    "stocks.fa.dupont": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_dupont"
    },
    "stocks.fa.earnings": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_earnings"
    },
    "stocks.fa.fraud": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_fraud_ratios"
    },
    "stocks.fa.av_income": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_income_statements"
    },
    "stocks.fa.av_metrics": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_key_metrics"
    },
    "stocks.fa.av_overview": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_overview"
    },
    "stocks.fa.mgmt": {
        "model": "openbb_terminal.stocks.fundamental_analysis.business_insider_model.get_management"
    },
    "stocks.fa.fama_coe": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.get_fama_coe"
    },
    "stocks.fa.fama_raw": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.get_fama_raw"
    },
    "stocks.fa.historical_5": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.get_historical_5"
    },
    "stocks.fa.similar_dfs": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.get_similar_dfs"
    },
    "stocks.fa.analysis": {
        "model": "openbb_terminal.stocks.fundamental_analysis.eclect_us_model.get_filings_analysis"
    },
    "stocks.fa.fmp_balance": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_balance"
    },
    "stocks.fa.fmp_cash": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_cash"
    },
    "stocks.fa.dcf": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_dcf"
    },
    "stocks.fa.enterprise": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_enterprise"
    },
    "stocks.fa.growth": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_financial_growth"
    },
    "stocks.fa.fmp_income": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_income"
    },
    "stocks.fa.fmp_metrics": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_key_metrics"
    },
    "stocks.fa.fmp_ratios": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_key_ratios"
    },
    "stocks.fa.profile": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_profile"
    },
    "stocks.fa.quote": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_quote"
    },
    "stocks.fa.score": {
        "model": "openbb_terminal.stocks.fundamental_analysis.fmp_model.get_score"
    },
    "stocks.fa.data": {
        "model": "openbb_terminal.stocks.fundamental_analysis.finviz_model.get_data"
    },
    "stocks.fa.poly_financials": {
        "model": "openbb_terminal.stocks.fundamental_analysis.polygon_model.get_financials",
        "view": "openbb_terminal.stocks.fundamental_analysis.polygon_view.display_fundamentals",
    },
    "stocks.fa.cal": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_calendar_earnings"
    },
    "stocks.fa.divs": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_dividends"
    },
    "stocks.fa.yf_financials": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_financials",
        "view": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_view.display_fundamentals",
    },
    "stocks.fa.hq": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_hq"
    },
    "stocks.fa.info": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_info"
    },
    "stocks.fa.mktcap": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_mktcap",
        "view": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_view.display_mktcap",
    },
    "stocks.fa.shrs": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_shareholders"
    },
    "stocks.fa.splits": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_splits",
        "view": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_view.display_splits",
    },
    "stocks.fa.sust": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_sustainability"
    },
    "stocks.fa.website": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_website"
    },
    "stocks.gov.qtrcontracts": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_qtr_contracts",
        "view": "openbb_terminal.stocks.government.quiverquant_view.display_qtr_contracts",
    },
    "stocks.gov.government_trading": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_government_trading"
    },
    "stocks.gov.contracts": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_contracts",
        "view": "openbb_terminal.stocks.government.quiverquant_view.display_contracts",
    },
    "stocks.gov.topbuys": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_government_buys",
        "view": "openbb_terminal.stocks.government.quiverquant_view.display_government_buys",
    },
    "stocks.gov.topsells": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_government_sells",
        "view": "openbb_terminal.stocks.government.quiverquant_view.display_government_sells",
    },
    "stocks.gov.gtrades": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_cleaned_government_trading",
        "view": "openbb_terminal.stocks.government.quiverquant_view.display_government_trading",
    },
    "stocks.gov.histcont": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_hist_contracts",
        "view": "openbb_terminal.stocks.government.quiverquant_view.display_hist_contracts",
    },
    "stocks.gov.lastcontracts": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_last_contracts",
        "view": "openbb_terminal.stocks.government.quiverquant_view.display_last_contracts",
    },
    "stocks.gov.lasttrades": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_last_government"
    },
    "stocks.gov.lobbying": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_lobbying"
    },
    "stocks.gov.toplobbying": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_top_lobbying",
        "view": "openbb_terminal.stocks.government.quiverquant_view.display_top_lobbying",
    },
    "stocks.ins.act": {
        "model": "openbb_terminal.stocks.insider.businessinsider_model.get_insider_activity",
        "view": "openbb_terminal.stocks.insider.businessinsider_view.insider_activity",
    },
    "stocks.ins.lins": {
        "model": "openbb_terminal.stocks.insider.finviz_model.get_last_insider_activity",
        "view": "openbb_terminal.stocks.insider.finviz_view.last_insider_activity",
    },
    "stocks.ins.print_insider_data": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.get_print_insider_data",
        "view": "openbb_terminal.stocks.insider.openinsider_view.print_insider_data",
    },
    "stocks.options.pcr": {
        "model": "openbb_terminal.stocks.options.alphaquery_model.get_put_call_ratio",
        "view": "openbb_terminal.stocks.options.alphaquery_view.display_put_call_ratio",
    },
    "stocks.options.info": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_info",
        "view": "openbb_terminal.stocks.options.barchart_view.print_options_data",
    },
    "stocks.options.hist_ce": {
        "model": "openbb_terminal.stocks.options.chartexchange_model.get_option_history",
        "view": "openbb_terminal.stocks.options.chartexchange_view.display_raw",
    },
    "stocks.options.unu": {
        "model": "openbb_terminal.stocks.options.fdscanner_model.unusual_options",
        "view": "openbb_terminal.stocks.options.fdscanner_view.display_options",
    },
    "stocks.options.hedge.add_hedge_option": {
        "model": "openbb_terminal.stocks.options.hedge.hedge_model.add_hedge_option",
        "view": "openbb_terminal.stocks.options.hedge.hedge_view.add_and_show_greeks",
    },
    "stocks.options.hedge.calc_delta": {
        "model": "openbb_terminal.stocks.options.hedge.hedge_model.calc_delta"
    },
    "stocks.options.hedge.calc_gamma": {
        "model": "openbb_terminal.stocks.options.hedge.hedge_model.calc_gamma"
    },
    "stocks.options.hedge.calc_hedge": {
        "model": "openbb_terminal.stocks.options.hedge.hedge_model.calc_hedge",
        "view": "openbb_terminal.stocks.options.hedge.hedge_view.show_calculated_hedge",
    },
    "stocks.options.hedge.calc_vega": {
        "model": "openbb_terminal.stocks.options.hedge.hedge_model.calc_vega"
    },
    "stocks.options.screen.check_presets": {
        "model": "openbb_terminal.stocks.options.screen.syncretism_model.check_presets"
    },
    "stocks.options.grhist": {
        "model": "openbb_terminal.stocks.options.screen.syncretism_model.get_historical_greeks",
        "view": "openbb_terminal.stocks.options.screen.syncretism_view.view_historical_greeks",
    },
    "stocks.options.screen.screener_output": {
        "model": "openbb_terminal.stocks.options.screen.syncretism_model.get_screener_output",
        "view": "openbb_terminal.stocks.options.screen.syncretism_view.view_screener_output",
    },
    "stocks.options.hist_tr": {
        "model": "openbb_terminal.stocks.options.tradier_model.get_historical_options",
        "view": "openbb_terminal.stocks.options.tradier_view.display_historical",
    },
    "stocks.options.chains": {
        "model": "openbb_terminal.stocks.options.tradier_model.get_option_chains",
        "view": "openbb_terminal.stocks.options.tradier_view.display_chains",
    },
    "stocks.options.chains_yf": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_full_option_chain",
        "view": "openbb_terminal.stocks.options.yfinance_view.display_chains",
    },
    "stocks.options.last_price": {
        "model": "openbb_terminal.stocks.options.tradier_model.last_price"
    },
    "stocks.options.option_expirations": {
        "model": "openbb_terminal.stocks.options.yfinance_model.option_expirations"
    },
    "stocks.options.process_chains": {
        "model": "openbb_terminal.stocks.options.tradier_model.process_chains"
    },
    "stocks.options.generate_data": {
        "model": "openbb_terminal.stocks.options.yfinance_model.generate_data"
    },
    "stocks.options.closing": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_closing"
    },
    "stocks.options.dividend": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_dividend"
    },
    "stocks.options.dte": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_dte"
    },
    "stocks.options.vsurf": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_iv_surface",
        "view": "openbb_terminal.stocks.options.yfinance_view.display_vol_surface",
    },
    "stocks.options.vol_yf": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_vol",
        "view": "openbb_terminal.stocks.options.yfinance_view.plot_vol",
    },
    "stocks.options.voi_yf": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_volume_open_interest",
        "view": "openbb_terminal.stocks.options.yfinance_view.plot_volume_open_interest",
    },
    "stocks.options.option_chain": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_option_chain"
    },
    "stocks.options.price": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_price"
    },
    "stocks.options.x_values": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_x_values"
    },
    "stocks.options.y_values": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_y_values"
    },
    "stocks.qa.capm_information": {
        "model": "openbb_terminal.stocks.quantitative_analysis.factors_model.capm_information"
    },
    "stocks.qa.fama_raw": {
        "model": "openbb_terminal.stocks.quantitative_analysis.factors_model.get_fama_raw"
    },
    "stocks.qa.historical_5": {
        "model": "openbb_terminal.stocks.quantitative_analysis.factors_model.get_historical_5"
    },
    "stocks.screener.screener_data": {
        "model": "openbb_terminal.stocks.screener.finviz_model.get_screener_data",
        "view": "openbb_terminal.stocks.screener.finviz_view.screener",
    },
    "stocks.screener.historical": {
        "model": "openbb_terminal.stocks.screener.yahoofinance_model.historical",
        "view": "openbb_terminal.stocks.screener.yahoofinance_view.historical",
    },
    "stocks.sia.filter_stocks": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.filter_stocks"
    },
    "stocks.sia.cpci": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_companies_per_country_in_industry",
        "view": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_view.display_companies_per_country_in_industry",
    },
    "stocks.sia.cpcs": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_companies_per_country_in_sector",
        "view": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_view.display_companies_per_country_in_sector",
    },
    "stocks.sia.cpic": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_companies_per_industry_in_country",
        "view": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_view.display_companies_per_industry_in_country",
    },
    "stocks.sia.cpis": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_companies_per_industry_in_sector",
        "view": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_view.display_companies_per_industry_in_sector",
    },
    "stocks.sia.cps": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_companies_per_sector_in_country",
        "view": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_view.display_companies_per_sector_in_country",
    },
    "stocks.sia.countries": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_countries"
    },
    "stocks.sia.industries": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_industries"
    },
    "stocks.sia.maketcap": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_marketcap"
    },
    "stocks.sia.sectors": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_sectors"
    },
    "stocks.sia.stocks_data": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.stockanalysis_model.get_stocks_data"
    },
    "stocks.ta.summary": {
        "model": "openbb_terminal.stocks.technical_analysis.finbrain_model.get_technical_summary_report",
        "view": "openbb_terminal.stocks.technical_analysis.finbrain_view.technical_summary_report",
    },
    "stocks.ta.view": {
        "model": "openbb_terminal.stocks.technical_analysis.finviz_model.get_finviz_image",
        "view": "openbb_terminal.stocks.technical_analysis.finviz_view.view",
    },
    "stocks.ta.recom": {
        "model": "openbb_terminal.stocks.technical_analysis.tradingview_model.get_tradingview_recommendation",
        "view": "openbb_terminal.stocks.technical_analysis.tradingview_view.print_recommendation",
    },
    "stocks.ta.rsp": {
        "model": "openbb_terminal.stocks.technical_analysis.rsp_model.get_rsp",
        "view": "openbb_terminal.stocks.technical_analysis.rsp_view.display_rsp",
    },
    "stocks.th.check_if_open": {
        "model": "openbb_terminal.stocks.tradinghours.bursa_model.check_if_open"
    },
    "stocks.th.all": {
        "model": "openbb_terminal.stocks.tradinghours.bursa_model.get_all",
        "view": "openbb_terminal.stocks.tradinghours.bursa_view.display_all",
    },
    "stocks.th.closed": {
        "model": "openbb_terminal.stocks.tradinghours.bursa_model.get_closed",
        "view": "openbb_terminal.stocks.tradinghours.bursa_view.display_closed",
    },
    "stocks.th.open": {
        "model": "openbb_terminal.stocks.tradinghours.bursa_model.get_open",
        "view": "openbb_terminal.stocks.tradinghours.bursa_view.display_open",
    },
    "stocks.th.exchange": {
        "model": "openbb_terminal.stocks.tradinghours.bursa_model.get_bursa",
        "view": "openbb_terminal.stocks.tradinghours.bursa_view.display_exchange",
    },
    "stocks.load": {"model": "openbb_terminal.stocks.stocks_helper.load"},
    "etf.load": {"model": "openbb_terminal.stocks.stocks_helper.load"},
    "stocks.process_candle": {
        "model": "openbb_terminal.stocks.stocks_helper.process_candle"
    },
    "stocks.search": {"model": "openbb_terminal.stocks.stocks_helper.search"},
    "stocks.quote": {"model": "openbb_terminal.stocks.stocks_models.load_quote"},
    "stocks.tob": {"model": "openbb_terminal.stocks.cboe_model.get_top_of_book"},
    "stocks.candle": {"model": "openbb_terminal.stocks.stocks_helper.display_candle"},
    "crypto.load": {
        "model": "openbb_terminal.cryptocurrency.cryptocurrency_helpers.load"
    },
    "crypto.price": {"model": "openbb_terminal.cryptocurrency.pyth_model.get_price"},
    "crypto.find": {
        "model": "openbb_terminal.cryptocurrency.cryptocurrency_helpers.find"
    },
    "crypto.chart": {
        "model": "openbb_terminal.cryptocurrency.cryptocurrency_helpers.plot_chart",
        "view": "openbb_terminal.cryptocurrency.cryptocurrency_helpers.plot_chart",
    },
    "crypto.candles": {
        "model": "openbb_terminal.cryptocurrency.cryptocurrency_helpers.plot_candles"
    },
    "etf.candle": {"model": "openbb_terminal.stocks.stocks_helper.display_candle"},
    "forex.candle": {"model": "openbb_terminal.forex.forex_helper.display_candle"},
    "forex.load": {"model": "openbb_terminal.forex.forex_helper.load"},
    "keys.mykeys": {"model": "openbb_terminal.keys_model.get_keys"},
    "keys.set_keys": {"model": "openbb_terminal.keys_model.set_keys"},
    "keys.get_keys_info": {"model": "openbb_terminal.keys_model.get_keys_info"},
    "keys.av": {"model": "openbb_terminal.keys_model.set_av_key"},
    "keys.fmp": {"model": "openbb_terminal.keys_model.set_fmp_key"},
    "keys.quandl": {"model": "openbb_terminal.keys_model.set_quandl_key"},
    "keys.polygon": {"model": "openbb_terminal.keys_model.set_polygon_key"},
    "keys.fred": {"model": "openbb_terminal.keys_model.set_fred_key"},
    "keys.news": {"model": "openbb_terminal.keys_model.set_news_key"},
    "keys.tradier": {"model": "openbb_terminal.keys_model.set_tradier_key"},
    "keys.cmc": {"model": "openbb_terminal.keys_model.set_cmc_key"},
    "keys.finnhub": {"model": "openbb_terminal.keys_model.set_finnhub_key"},
    "keys.iex": {"model": "openbb_terminal.keys_model.set_iex_key"},
    "keys.reddit": {"model": "openbb_terminal.keys_model.set_reddit_key"},
    "keys.twitter": {"model": "openbb_terminal.keys_model.set_twitter_key"},
    "keys.rh": {"model": "openbb_terminal.keys_model.set_rh_key"},
    "keys.degiro": {"model": "openbb_terminal.keys_model.set_degiro_key"},
    "keys.oanda": {"model": "openbb_terminal.keys_model.set_oanda_key"},
    "keys.binance": {"model": "openbb_terminal.keys_model.set_binance_key"},
    "keys.bitquery": {"model": "openbb_terminal.keys_model.set_bitquery_key"},
    "keys.si": {"model": "openbb_terminal.keys_model.set_si_key"},
    "keys.coinbase": {"model": "openbb_terminal.keys_model.set_coinbase_key"},
    "keys.walert": {"model": "openbb_terminal.keys_model.set_walert_key"},
    "keys.glassnode": {"model": "openbb_terminal.keys_model.set_glassnode_key"},
    "keys.coinglass": {"model": "openbb_terminal.keys_model.set_coinglass_key"},
    "keys.cpanic": {"model": "openbb_terminal.keys_model.set_cpanic_key"},
    "keys.ethplorer": {"model": "openbb_terminal.keys_model.set_ethplorer_key"},
    "keys.smartstake": {"model": "openbb_terminal.keys_model.set_smartstake_key"},
    "keys.github": {"model": "openbb_terminal.keys_model.set_github_key"},
    "keys.messari": {"model": "openbb_terminal.keys_model.set_messari_key"},
    "keys.eodhd": {"model": "openbb_terminal.keys_model.set_eodhd_key"},
    "keys.santiment": {"model": "openbb_terminal.keys_model.set_santiment_key"},
    "keys.tokenterminal": {"model": "openbb_terminal.keys_model.set_tokenterminal_key"},
    "keys.shroom": {"model": "openbb_terminal.keys_model.set_shroom_key"},
}
forecast_extras = {
    "forecast.load": {"model": "openbb_terminal.common.common_model.load"},
    "forecast.show": {
        "model": "openbb_terminal.forecast.forecast_view.show_df",
        "view": "openbb_terminal.forecast.forecast_view.show_df",
    },
    "forecast.plot": {
        "model": "openbb_terminal.forecast.forecast_view.display_plot",
        "view": "openbb_terminal.forecast.forecast_view.display_plot",
    },
    "forecast.clean": {"model": "openbb_terminal.forecast.forecast_model.clean"},
    "forecast.combine": {
        "model": "openbb_terminal.forecast.forecast_model.combine_dfs"
    },
    "forecast.desc": {
        "view": "openbb_terminal.forecast.forecast_view.describe_df",
        "model": "openbb_terminal.forecast.forecast_model.describe_df",
    },
    "forecast.corr": {
        "view": "openbb_terminal.forecast.forecast_view.display_corr",
        "model": "openbb_terminal.forecast.forecast_model.corr_df",
    },
    "forecast.season": {
        "model": "openbb_terminal.forecast.forecast_view.display_seasonality"
    },
    "forecast.delete": {
        "model": "openbb_terminal.forecast.forecast_model.delete_column"
    },
    "forecast.rename": {
        "model": "openbb_terminal.forecast.forecast_model.rename_column"
    },
    "forecast.export": {"model": "openbb_terminal.forecast.forecast_view.export_df"},
    "forecast.signal": {"model": "openbb_terminal.forecast.forecast_model.add_signal"},
    "forecast.atr": {"model": "openbb_terminal.forecast.forecast_model.add_atr"},
    "forecast.ema": {"model": "openbb_terminal.forecast.forecast_model.add_ema"},
    "forecast.sto": {"model": "openbb_terminal.forecast.forecast_model.add_sto"},
    "forecast.rsi": {"model": "openbb_terminal.forecast.forecast_model.add_rsi"},
    "forecast.roc": {"model": "openbb_terminal.forecast.forecast_model.add_roc"},
    "forecast.mom": {"model": "openbb_terminal.forecast.forecast_model.add_momentum"},
    "forecast.delta": {"model": "openbb_terminal.forecast.forecast_model.add_delta"},
    "forecast.autoces": {
        "model": "openbb_terminal.forecast.autoces_model.get_autoces_data",
        "view": "openbb_terminal.forecast.autoces_view.display_autoces_forecast",
    },
    "forecast.autoets": {
        "model": "openbb_terminal.forecast.autoets_model.get_autoets_data",
        "view": "openbb_terminal.forecast.autoets_view.display_autoets_forecast",
    },
    "forecast.seasonalnaive": {
        "model": "openbb_terminal.forecast.seasonalnaive_model.get_seasonalnaive_data",
        "view": "openbb_terminal.forecast.seasonalnaive_view.display_seasonalnaive_forecast",
    },
    "forecast.expo": {
        "model": "openbb_terminal.forecast.expo_model.get_expo_data",
        "view": "openbb_terminal.forecast.expo_view.display_expo_forecast",
    },
    "forecast.theta": {
        "model": "openbb_terminal.forecast.theta_model.get_theta_data",
        "view": "openbb_terminal.forecast.theta_view.display_theta_forecast",
    },
    "forecast.linregr": {
        "model": "openbb_terminal.forecast.linregr_model.get_linear_regression_data",
        "view": "openbb_terminal.forecast.linregr_view.display_linear_regression",
    },
    "forecast.regr": {
        "model": "openbb_terminal.forecast.regr_model.get_regression_data",
        "view": "openbb_terminal.forecast.regr_view.display_regression",
    },
    "forecast.rnn": {
        "model": "openbb_terminal.forecast.rnn_model.get_rnn_data",
        "view": "openbb_terminal.forecast.rnn_view.display_rnn_forecast",
    },
    "forecast.brnn": {
        "model": "openbb_terminal.forecast.brnn_model.get_brnn_data",
        "view": "openbb_terminal.forecast.brnn_view.display_brnn_forecast",
    },
    "forecast.nbeats": {
        "model": "openbb_terminal.forecast.nbeats_model.get_NBEATS_data",
        "view": "openbb_terminal.forecast.nbeats_view.display_nbeats_forecast",
    },
    "forecast.tcn": {
        "model": "openbb_terminal.forecast.tcn_model.get_tcn_data",
        "view": "openbb_terminal.forecast.tcn_view.display_tcn_forecast",
    },
    "forecast.trans": {
        "model": "openbb_terminal.forecast.trans_model.get_trans_data",
        "view": "openbb_terminal.forecast.trans_view.display_trans_forecast",
    },
    "forecast.tft": {
        "model": "openbb_terminal.forecast.tft_model.get_tft_data",
        "view": "openbb_terminal.forecast.tft_view.display_tft_forecast",
    },
    "forecast.nhits": {
        "model": "openbb_terminal.forecast.nhits_model.get_nhits_data",
        "view": "openbb_terminal.forecast.nhits_view.display_nhits_forecast",
    },
    "futures.search": {
        "model": "openbb_terminal.futures.yfinance_model.get_search_futures",
        "view": "openbb_terminal.futures.yfinance_view.display_search",
    },
    "futures.historical": {
        "model": "openbb_terminal.futures.yfinance_model.get_historical_futures",
        "view": "openbb_terminal.futures.yfinance_view.display_historical",
    },
    "futures.curve": {
        "model": "openbb_terminal.futures.yfinance_model.get_curve_futures",
        "view": "openbb_terminal.futures.yfinance_view.display_curve",
    },
}

if forecasting:
    functions = {**functions, **forecast_extras}


def copy_func(
    f: Callable,
    logging_decorator: bool = False,
    virtual_path: str = "",
    chart: bool = False,
) -> Callable:
    """Copy the contents and attributes of the entered function.

    Based on https://stackoverflow.com/a/13503277

    Parameters
    ----------
    f: Callable
        Function to be copied
    logging_decorator: bool
        If True, the copied function will be decorated with the logging decorator
    virtual_path: str
        If not empty, virtual path will be added to the logging
    chart: bool
        If True, the copied function will log info on whether it is a view (chart)

    Returns
    -------
    g: Callable
        New function
    """
    # Removing the logging decorator
    if hasattr(f, "__wrapped__"):
        f = f.__wrapped__  # type: ignore

    g = types.FunctionType(
        f.__code__,
        f.__globals__,
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__

    if logging_decorator:
        log_name = logging.getLogger(g.__module__)
        g = sdk_arg_logger(func=g, log=log_name, virtual_path=virtual_path, chart=chart)
        g = log_start_end(func=g, log=log_name)

    return g


def change_docstring(api_callable, model: Callable, view=None):
    """Change docstring of the entered api_callable.

    Parameters
    ----------
    api_callable: Callable
        Function whose docstring shall be changed
    model: Callable
        model function with docstring
    view: Callable
        view function with docstring, can also be None if no docstring from it shall be added
    Returns
    -------
    Callable
        api_callable with changed docstring
    """
    if view.__doc__ is not None:
        index = view.__doc__.find("Parameters")
        all_parameters = (
            "\nSDK function, use the chart kwarg for getting the view model and it's plot. "
            "See every parameter below:\n\n    "
            + view.__doc__[index:]
            + """chart: bool
    If the view and its chart shall be used"""
        )
        api_callable.__doc__ = (
            all_parameters
            + "\n\nModel doc:\n"
            + model.__doc__
            + "\n\nView doc:\n"
            + view.__doc__
        )
        api_callable.__name__ = model.__name__.replace("get_", "")
        parameters = list(signature(view).parameters.values())
        chart_parameter = [
            Parameter(
                "chart", Parameter.POSITIONAL_OR_KEYWORD, annotation=bool, default=False
            )
        ]
        api_callable.__module__ = model.__module__
        api_callable.__signature__ = signature(view).replace(
            parameters=parameters + chart_parameter
        )
    else:
        api_callable.__doc__ = model.__doc__
        api_callable.__name__ = model.__name__
        api_callable.__module__ = model.__module__
        api_callable.__signature__ = signature(model)

    return api_callable


def check_suppress_logging(suppress_dict: dict) -> bool:
    """
    Check if logging should be suppressed.
    If the dict contains a value that is found in the stack trace,
     the logging should be suppressed.

    Parameters
    ----------
    supress_dict: dict
        Dictionary with values that trigger log suppression

    Returns
    -------
    bool
        True if logging shall be suppressed, False otherwise
    """
    for _, value in suppress_dict.items():
        for ele in format_stack():
            if value in ele:
                return True
    return False


class FunctionFactory:
    """The SDK Function Factory, which creates the callable instance."""

    def __init__(
        self, model: Callable, view: Optional[Callable] = None, virtual_path: str = ""
    ):
        """Initialise the FunctionFactory instance.

        Parameters
        ----------
        model: Callable
            The original model function from the terminal
        view: Callable
            The original view function from the terminal, this shall be set to None if the
            function has no charting
        """
        self.virtual_path = virtual_path
        self.model_only = view is None
        self.model = copy_func(
            f=model, logging_decorator=True, virtual_path=virtual_path
        )
        self.view = None
        if view is not None:
            self.view = copy_func(
                f=view, logging_decorator=True, virtual_path=virtual_path, chart=True
            )

    def api_callable(self, *args, **kwargs):
        """Return a result of the command from the view or the model function based on the chart parameter.

        Parameters
        ----------
        args
        kwargs

        Returns
        -------
        Result from the view or model
        """

        if "chart" not in kwargs:
            kwargs["chart"] = False
        if kwargs["chart"] and (not self.model_only):
            kwargs.pop("chart")
            return self.view(*args, **kwargs)
        kwargs.pop("chart")
        return self.model(*args, **kwargs)


class MenuFiller:
    """A filler callable for the menus."""

    def __init__(self, function: Callable):
        """Instantiate the function."""
        self.__function = function

    def __call__(self, *args, **kwargs):
        """Override the __call__."""
        print(self.__function(*args, **kwargs))

    def __repr__(self):
        """Get human readable representation."""
        return self.__function()


class MainMenu:
    """Main menu."""

    def __call__(self):
        """Print help message."""
        print(self.__repr__())

    def __repr__(self):
        """Get human readable representation."""
        return """This is the OpenBB Terminal SDK.
        Use the SDK to get data directly into your jupyter notebook or directly use it in your application.
        ...
        For more information see the official documentation at: https://openbb-finance.github.io/OpenBBTerminal/SDK/
        """


class Loader:
    """The Loader class."""

    def __init__(self, funcs: dict, suppress_logging: bool = False):

        self.__suppress_logging = suppress_logging
        self.__function_map = self.build_function_map(funcs=funcs)
        self.__check_initialize_logging()
        self.load_menus()

    def __call__(self):
        """Print help message."""
        print(self.__repr__())

    def __repr__(self):
        """Get human readable representation."""
        return """This is the OpenBB Terminal SDK.
        Use the SDK to get data directly into your jupyter notebook or directly use it in your application.
        ...
        For more information see the official documentation at: https://openbb-finance.github.io/OpenBBTerminal/SDK/
        """

    # TODO: Add settings
    def settings(self):
        """Add setting."""
        # pass

    def load_menus(self):
        """Create the SDK structure by setting attributes and saving the functions.

        See openbb.stocks.command
        """

        def menu_message(menu: str, full_path: List[str], function_map: dict):
            """Create a callable function, which prints a menus help message.

            Parameters
            ----------
            menu: str
                Menu for which the help message is generated
            full_path: List[str]
                The list to get to the path
            function_map: dict
                Dictionary with the functions and their virtual paths

            Returns
            -------
            Callable:
                Function which prints help message
            """
            path_str = ".".join(full_path)
            filtered_dict = {k: v for (k, v) in function_map.items() if path_str in k}

            def f():
                string = menu.upper() + " Menu\n\nThe SDK commands of the the menu:"
                for command in filtered_dict:
                    string += "\n\t<openbb>." + command
                return string

            return f

        function_map = self.__function_map
        main_menu = MainMenu()

        for virtual_path, function in function_map.items():
            virtual_path_split = virtual_path.split(".")
            last_virtual_path = virtual_path_split[-1]

            previous_menu = main_menu

            for menu in virtual_path_split[:-1]:
                if not hasattr(previous_menu, menu):
                    partial_path = virtual_path_split[
                        : virtual_path_split.index(menu) + 1
                    ]
                    next_menu = MenuFiller(
                        function=menu_message(menu, partial_path, function_map)
                    )
                    setattr(previous_menu, menu, next_menu)
                previous_menu = getattr(previous_menu, menu)
            setattr(previous_menu, last_virtual_path, function)

        self.openbb = main_menu

    def __check_initialize_logging(self):
        if not self.__suppress_logging:
            self.__initialize_logging()

    @staticmethod
    def __load_module(module_path: str) -> Optional[types.ModuleType]:
        """Load a module from a path.

        Parameters
        ----------
        module_path: str
            Module"s path.

        Returns
        -------
        Optional[ModuleType]:
            Loaded module or None.
        """
        try:
            spec = importlib.util.find_spec(module_path)
            del spec
        except ModuleNotFoundError:
            return None

        return importlib.import_module(module_path)

    @staticmethod
    def __initialize_logging():
        cfg.LOGGING_SUB_APP = "sdk"
        setup_logging()
        log_all_settings()

    @classmethod
    def get_function(cls, function_path: str) -> Union[Callable, None]:
        """Get function from string path.

        Parameters
        ----------
        cls
            Class
        function_path: str
            Function path from repository base root

        Returns
        -------
        Callable
            Function
        """
        module_path, function_name = function_path.rsplit(sep=".", maxsplit=1)
        try:
            module = cls.__load_module(module_path=module_path)
        except Exception as e:
            # This avoids crash on loading SDK under installer application.
            # SDK is used by papermill to generate reports and some dependencies
            # are not compatible. Since the reports are run in a subprocess,
            # this error message is actually not displayed on screen.
            # TODO: Fix this.
            console.print(f"Cannot load: {module_path} -> {e}")
            return None

        try:
            function = getattr(module, function_name)
        except AttributeError:
            function = None
            console.print("[red]Could not find the item below:[red]")
            console.print(f"function: {function_name}")
            console.print(f"module path: {module_path}")
            console.print(f"module: {module}")
        return function

    @classmethod
    def build_function_map(cls, funcs: dict) -> dict:
        """Build dictionary with FunctionFactory instances as items.

        Parameters
        ----------
        funcs: dict
            Dictionary which has string path of view and model functions as keys.
            The items is dictionary with the view and model function as items of the
            respective "view" and "model" keys

        Returns
        -------
        dict
            Dictionary with FunctionFactory instances as items and string path as keys
        """
        function_map = {}

        for virtual_path in funcs.keys():
            model_path = funcs[virtual_path].get("model")
            view_path = funcs[virtual_path].get("view")

            if model_path:
                model_function = cls.get_function(function_path=model_path)
            else:
                model_function = None

            if view_path:
                view_function = cls.get_function(function_path=view_path)
            else:
                view_function = None

            if model_function is not None:
                function_factory = FunctionFactory(
                    model=model_function, view=view_function, virtual_path=virtual_path
                )
                function_with_doc = change_docstring(
                    types.FunctionType(function_factory.api_callable.__code__, {}),
                    model_function,
                    view_function,
                )
                function_map[virtual_path] = types.MethodType(
                    function_with_doc, function_factory
                )

            elif view_function is not None:
                raise Exception(
                    f"View function without model function : {view_function}"
                )

        return function_map


# TO USE THE SDK DIRECTLY JUST IMPORT IT:
# from openbb_terminal.sdk import openbb (or: from openbb_terminal.sdk import openbb as sdk)
openbb = Loader(
    funcs=functions,
    suppress_logging=check_suppress_logging(suppress_dict=SUPPRESS_LOGGING_CLASSES),
).openbb
