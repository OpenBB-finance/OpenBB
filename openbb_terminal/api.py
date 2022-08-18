"""OpenBB Terminal API."""
# pylint: disable=C0302,W0611
from inspect import signature, Parameter
import types
import functools
import importlib
from typing import Optional, Callable

from openbb_terminal.helper_classes import TerminalStyle  # noqa: F401
from .reports import widget_helpers as widgets  # noqa: F401

# THIS IS SOME EXAMPLE OF USAGE FOR USING IT DIRECTLY IN JUPYTER NOTEBOOK
functions = {
    "alt.covid.case_slopes": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_case_slopes"
    },
    "alt.covid.global_cases": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_global_cases"
    },
    "alt.covid.global_deaths": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_global_deaths"
    },
    "alt.oss.github_data": {
        "model": "openbb_terminal.alternative.oss.github_model.get_github_data"
    },
    "alt.oss.repo_summary": {
        "model": "openbb_terminal.alternative.oss.github_model.get_repo_summary",
        "view": "openbb_terminal.alternative.oss.github_view.display_repo_summary",
    },
    "alt.oss.stars_history": {
        "model": "openbb_terminal.alternative.oss.github_model.get_stars_history"
    },
    "alt.oss.top_repos": {
        "model": "openbb_terminal.alternative.oss.github_model.get_top_repos",
        "view": "openbb_terminal.alternative.oss.github_view.display_top_repos",
    },
    "alt.oss.search_repos": {
        "model": "openbb_terminal.alternative.oss.github_model.search_repos"
    },
    "alt.oss._make_request": {
        "model": "openbb_terminal.alternative.oss.runa_model._make_request"
    },
    "alt.oss._retry_session": {
        "model": "openbb_terminal.alternative.oss.runa_model._retry_session"
    },
    "common.behavioural_analysis.sentiment": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_sentiment",
        "view": "openbb_terminal.common.behavioural_analysis.twitter_view.display_sentiment",
    },
    "common.behavioural_analysis.sentiment_stats": {
        "model": "openbb_terminal.common.behavioural_analysis.finnhub_model.get_sentiment_stats",
        "view": "openbb_terminal.common.behavioural_analysis.finnhub_view.display_sentiment_stats",
    },
    "common.behavioural_analysis.mentions": {
        "model": "openbb_terminal.common.behavioural_analysis.google_model.get_mentions",
        "view": "openbb_terminal.common.behavioural_analysis.google_view.display_mentions",
    },
    "common.behavioural_analysis.queries": {
        "model": "openbb_terminal.common.behavioural_analysis.google_model.get_queries",
        "view": "openbb_terminal.common.behavioural_analysis.google_view.display_queries",
    },
    "common.behavioural_analysis.regions": {
        "model": "openbb_terminal.common.behavioural_analysis.google_model.get_regions",
        "view": "openbb_terminal.common.behavioural_analysis.google_view.display_regions",
    },
    "common.behavioural_analysis.rise": {
        "model": "openbb_terminal.common.behavioural_analysis.google_model.get_rise",
        "view": "openbb_terminal.common.behavioural_analysis.google_view.display_rise",
    },
    "common.behavioural_analysis.clean_reddit_text": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.clean_reddit_text"
    },
    "common.behavioural_analysis.comments": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_comments"
    },
    "common.behavioural_analysis.due_dilligence": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_due_dilligence"
    },
    "common.behavioural_analysis.popular_tickers": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_popular_tickers",
        "view": "openbb_terminal.common.behavioural_analysis.reddit_view.display_popular_tickers",
    },
    "common.behavioural_analysis.posts_about": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_posts_about"
    },
    "common.behavioural_analysis.spac": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_spac",
        "view": "openbb_terminal.common.behavioural_analysis.reddit_view.display_spac",
    },
    "common.behavioural_analysis.spac_community": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_spac_community",
        "view": "openbb_terminal.common.behavioural_analysis.reddit_view.display_spac_community",
    },
    "common.behavioural_analysis.watchlists": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_watchlists"
    },
    "common.behavioural_analysis.wsb_community": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_wsb_community",
        "view": "openbb_terminal.common.behavioural_analysis.reddit_view.display_wsb_community",
    },
    "common.behavioural_analysis.check_supported_ticker": {
        "model": "openbb_terminal.common.behavioural_analysis.sentimentinvestor_model.check_supported_ticker"
    },
    "common.behavioural_analysis.historical": {
        "model": "openbb_terminal.common.behavioural_analysis.sentimentinvestor_model.get_historical",
        "view": "openbb_terminal.common.behavioural_analysis.sentimentinvestor_view.display_historical",
    },
    "common.behavioural_analysis.trending": {
        "model": "openbb_terminal.common.behavioural_analysis.sentimentinvestor_model.get_trending",
        "view": "openbb_terminal.common.behavioural_analysis.sentimentinvestor_view.display_trending",
    },
    "common.behavioural_analysis.bullbear": {
        "model": "openbb_terminal.common.behavioural_analysis.stocktwits_model.get_bullbear",
        "view": "openbb_terminal.common.behavioural_analysis.stocktwits_view.display_bullbear",
    },
    "common.behavioural_analysis.messages": {
        "model": "openbb_terminal.common.behavioural_analysis.stocktwits_model.get_messages",
        "view": "openbb_terminal.common.behavioural_analysis.stocktwits_view.display_messages",
    },
    "common.behavioural_analysis.stalker": {
        "model": "openbb_terminal.common.behavioural_analysis.stocktwits_model.get_stalker",
        "view": "openbb_terminal.common.behavioural_analysis.stocktwits_view.display_stalker",
    },
    "common.behavioural_analysis.load_analyze_tweets": {
        "model": "openbb_terminal.common.behavioural_analysis.twitter_model.load_analyze_tweets"
    },
    # "common.prediction_techniques.arima_model": {
    #     "model": "openbb_terminal.common.prediction_techniques.arima_model.get_arima_model"
    # },
    # "common.prediction_techniques.exponential_smoothing_model": {
    #     "model": "openbb_terminal.common.prediction_techniques.ets_model.get_exponential_smoothing_model"
    # },
    # "common.prediction_techniques.knn_model_data": {
    #     "model": "openbb_terminal.common.prediction_techniques.knn_model.get_knn_model_data"
    # },
    # "common.prediction_techniques.mc_brownian": {
    #     "model": "openbb_terminal.common.prediction_techniques.mc_model.get_mc_brownian"
    # },
    # "common.prediction_techniques.build_neural_network_model": {
    #     "model": "openbb_terminal.common.prediction_techniques.neural_networks_model.build_neural_network_model"
    # },
    # "common.prediction_techniques.conv1d_model": {
    #     "model": "openbb_terminal.common.prediction_techniques.neural_networks_model.conv1d_model"
    # },
    # "common.prediction_techniques.lstm_model": {
    #     "model": "openbb_terminal.common.prediction_techniques.neural_networks_model.lstm_model"
    # },
    # "common.prediction_techniques.mlp_model": {
    #     "model": "openbb_terminal.common.prediction_techniques.neural_networks_model.mlp_model"
    # },
    # "common.prediction_techniques.rnn_model": {
    #     "model": "openbb_terminal.common.prediction_techniques.neural_networks_model.rnn_model"
    # },
    # "common.prediction_techniques.regression_model": {
    #     "model": "openbb_terminal.common.prediction_techniques.regression_model.get_regression_model"
    # },
    # "common.prediction_techniques.split_train": {
    #     "model": "openbb_terminal.common.prediction_techniques.regression_model.split_train"
    # },
    "common.quantitative_analysis.calculate_adjusted_var": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.calculate_adjusted_var"
    },
    "common.quantitative_analysis.es": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_es",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_es",
    },
    "common.quantitative_analysis.normality": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_normality",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_normality",
    },
    "common.quantitative_analysis.omega": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_omega",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_omega",
    },
    "common.quantitative_analysis.seasonal_decomposition": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_seasonal_decomposition",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_seasonal",
    },
    "common.quantitative_analysis.sharpe": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_sharpe",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_sharpe",
    },
    "common.quantitative_analysis.sortino": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_sortino",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_sortino",
    },
    "common.quantitative_analysis.summary": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_summary",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_summary",
    },
    "common.quantitative_analysis.unitroot": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_unitroot",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_unitroot",
    },
    "common.quantitative_analysis.var": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_var",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_var",
    },
    "common.quantitative_analysis.kurtosis": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_kurtosis",
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_kurtosis",
    },
    "common.quantitative_analysis.quantile": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_quantile",
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_quantile",
    },
    "common.quantitative_analysis.rolling_avg": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_rolling_avg"
    },
    "common.quantitative_analysis.skew": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_skew",
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_skew",
    },
    "common.quantitative_analysis.spread": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_spread",
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_spread",
    },
    "common.technical_analysis.calculate_fib_levels": {
        "model": "openbb_terminal.common.technical_analysis.custom_indicators_model.calculate_fib_levels"
    },
    "common.technical_analysis.cci": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.cci",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_cci",
    },
    "common.technical_analysis.cg": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.cg",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_cg",
    },
    "common.technical_analysis.fisher": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.fisher",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_fisher",
    },
    "common.technical_analysis.macd": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.macd",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_macd",
    },
    "common.technical_analysis.rsi": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.rsi",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_rsi",
    },
    "common.technical_analysis.stoch": {
        "model": "openbb_terminal.common.technical_analysis.momentum_model.stoch",
        "view": "openbb_terminal.common.technical_analysis.momentum_view.display_stoch",
    },
    "common.technical_analysis.ema": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.ema"
    },
    "common.technical_analysis.hma": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.hma"
    },
    "common.technical_analysis.sma": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.sma"
    },
    "common.technical_analysis.vwap": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.vwap"
    },
    "common.technical_analysis.wma": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.wma"
    },
    "common.technical_analysis.zlma": {
        "model": "openbb_terminal.common.technical_analysis.overlap_model.zlma"
    },
    "common.technical_analysis.adx": {
        "model": "openbb_terminal.common.technical_analysis.trend_indicators_model.adx",
        "view": "openbb_terminal.common.technical_analysis.trend_indicators_view.display_adx",
    },
    "common.technical_analysis.aroon": {
        "model": "openbb_terminal.common.technical_analysis.trend_indicators_model.aroon",
        "view": "openbb_terminal.common.technical_analysis.trend_indicators_view.display_aroon",
    },
    "common.technical_analysis.bbands": {
        "model": "openbb_terminal.common.technical_analysis.volatility_model.bbands",
        "view": "openbb_terminal.common.technical_analysis.volatility_view.display_bbands",
    },
    "common.technical_analysis.donchian": {
        "model": "openbb_terminal.common.technical_analysis.volatility_model.donchian",
        "view": "openbb_terminal.common.technical_analysis.volatility_view.display_donchian",
    },
    "common.technical_analysis.kc": {
        "model": "openbb_terminal.common.technical_analysis.volatility_model.kc"
    },
    "common.technical_analysis.ad": {
        "model": "openbb_terminal.common.technical_analysis.volume_model.ad",
        "view": "openbb_terminal.common.technical_analysis.volume_view.display_ad",
    },
    "common.technical_analysis.adosc": {
        "model": "openbb_terminal.common.technical_analysis.volume_model.adosc",
        "view": "openbb_terminal.common.technical_analysis.volume_view.display_adosc",
    },
    "common.technical_analysis.obv": {
        "model": "openbb_terminal.common.technical_analysis.volume_model.obv",
        "view": "openbb_terminal.common.technical_analysis.volume_view.display_obv",
    },
    "crypto.defi._prepare_params": {
        "model": "openbb_terminal.cryptocurrency.defi.coindix_model._prepare_params"
    },
    "crypto.defi.defi_vaults": {
        "model": "openbb_terminal.cryptocurrency.defi.coindix_model.get_defi_vaults",
        "view": "openbb_terminal.cryptocurrency.defi.coindix_view.display_defi_vaults",
    },
    "crypto.defi.anchor_data": {
        "model": "openbb_terminal.cryptocurrency.defi.cryptosaurio_model.get_anchor_data",
        "view": "openbb_terminal.cryptocurrency.defi.cryptosaurio_view.display_anchor_data",
    },
    "crypto.defi.last_uni_swaps": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_last_uni_swaps",
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_last_uni_swaps",
    },
    "crypto.defi.uni_tokens": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_uni_tokens",
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_uni_tokens",
    },
    "crypto.defi.uniswap_pool_recently_added": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_uniswap_pool_recently_added"
    },
    "crypto.defi.query_graph": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.query_graph"
    },
    "crypto.defi.defi_protocol": {
        "model": "openbb_terminal.cryptocurrency.defi.llama_model.get_defi_protocol"
    },
    "crypto.defi.luna_supply_stats": {
        "model": "openbb_terminal.cryptocurrency.defi.smartstake_model.get_luna_supply_stats"
    },
    "crypto.defi.scrape_substack": {
        "model": "openbb_terminal.cryptocurrency.defi.substack_model.scrape_substack"
    },
    "crypto.defi.history_asset_from_terra_address": {
        "model": "openbb_terminal.cryptocurrency.defi.terraengineer_model.get_history_asset_from_terra_address"
    },
    "crypto.defi._adjust_delegation_info": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model._adjust_delegation_info"
    },
    "crypto.defi._make_request": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model._make_request"
    },
    "crypto.defi.account_growth": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_account_growth",
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_account_growth",
    },
    "crypto.defi.proposals": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_proposals"
    },
    "crypto.defi.staking_account_info": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_staking_account_info"
    },
    "crypto.discovery.search_results": {
        "model": "openbb_terminal.cryptocurrency.discovery.coinpaprika_model.get_search_results",
        "view": "openbb_terminal.cryptocurrency.discovery.coinpaprika_view.display_search_results",
    },
    "crypto.discovery._make_request": {
        "model": "openbb_terminal.cryptocurrency.discovery.dappradar_model._make_request"
    },
    "crypto.discovery.coins": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_coins",
        "view": "openbb_terminal.cryptocurrency.discovery.pycoingecko_view.display_coins",
    },
    "crypto.discovery.coins_for_given_exchange": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_coins_for_given_exchange"
    },
    "crypto.discovery.gainers_or_losers": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_gainers_or_losers"
    },
    "crypto.discovery.mapping_matrix_for_exchange": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_mapping_matrix_for_exchange"
    },
    "crypto.discovery.read_file_data": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.read_file_data"
    },
    "crypto.due_diligence.check_valid_binance_str": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.binance_model.check_valid_binance_str"
    },
    "crypto.due_diligence.show_available_pairs_for_given_symbol": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.show_available_pairs_for_given_symbol"
    },
    "crypto.due_diligence.order_book": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinbase_view.display_order_book",
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_order_book",
    },
    "crypto.due_diligence.candles": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_candles",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinbase_view.display_candles",
    },
    "crypto.due_diligence.product_stats": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_product_stats"
    },
    "crypto.due_diligence.trades": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_trades",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinbase_view.display_trades",
    },
    "crypto.due_diligence.trading_pair_info": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_trading_pair_info"
    },
    "crypto.due_diligence.open_interest_per_exchange": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinglass_model.get_open_interest_per_exchange"
    },
    "crypto.due_diligence.basic_coin_info": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.basic_coin_info"
    },
    "crypto.due_diligence.coin": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin"
    },
    "crypto.due_diligence.coin_events_by_id": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_events_by_id"
    },
    "crypto.due_diligence.coin_exchanges_by_id": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_exchanges_by_id"
    },
    "crypto.due_diligence.coin_markets_by_id": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_markets_by_id"
    },
    "crypto.due_diligence.coin_twitter_timeline": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_twitter_timeline"
    },
    "crypto.due_diligence.ohlc_historical": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_ohlc_historical"
    },
    "crypto.due_diligence.tickers_info_for_coin": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_tickers_info_for_coin"
    },
    "crypto.due_diligence.validate_coin": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.validate_coin"
    },
    "crypto.due_diligence.active_addresses": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_active_addresses",
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_active_addresses",
    },
    "crypto.due_diligence.close_price": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_close_price"
    },
    "crypto.due_diligence.exchange_balances": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_exchange_balances",
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_exchange_balances",
    },
    "crypto.due_diligence.exchange_net_position_change": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_exchange_net_position_change",
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_exchange_net_position_change",
    },
    "crypto.due_diligence.hashrate": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_hashrate",
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_hashrate",
    },
    "crypto.due_diligence.non_zero_addresses": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_non_zero_addresses",
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_non_zero_addresses",
    },
    "crypto.due_diligence.format_addresses": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.format_addresses"
    },
    "crypto.due_diligence.fundraising": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_fundraising",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_fundraising",
    },
    "crypto.due_diligence.governance": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_governance",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_governance",
    },
    "crypto.due_diligence.investors": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_investors",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_investors",
    },
    "crypto.due_diligence.links": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_links",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_links",
    },
    "crypto.due_diligence.marketcap_dominance": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_marketcap_dominance",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_marketcap_dominance",
    },
    "crypto.due_diligence.messari_timeseries": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_messari_timeseries",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_messari_timeseries",
    },
    "crypto.due_diligence.project_product_info": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_project_product_info"
    },
    "crypto.due_diligence.roadmap": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_roadmap",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_roadmap",
    },
    "crypto.due_diligence.team": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_team",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_team",
    },
    "crypto.due_diligence.tokenomics": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_tokenomics",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_tokenomics",
    },
    "crypto.due_diligence.check_coin": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.check_coin"
    },
    "crypto.due_diligence.coin_market_chart": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_coin_market_chart"
    },
    "crypto.due_diligence.coin_potential_returns": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_coin_potential_returns",
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_coin_potential_returns",
    },
    "crypto.due_diligence.coin_tokenomics": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_coin_tokenomics"
    },
    "crypto.due_diligence.ohlc": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_ohlc"
    },
    "crypto.due_diligence.github_activity": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.santiment_model.get_github_activity",
        "view": "openbb_terminal.cryptocurrency.due_diligence.santiment_view.display_github_activity",
    },
    "crypto.due_diligence.slug": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.santiment_model.get_slug"
    },
    "crypto.nft.nft_drops": {
        "model": "openbb_terminal.cryptocurrency.nft.nftcalendar_model.get_nft_drops"
    },
    "crypto.nft.collection_stats": {
        "model": "openbb_terminal.cryptocurrency.nft.opensea_model.get_collection_stats",
        "view": "openbb_terminal.cryptocurrency.nft.opensea_view.display_collection_stats",
    },
    "crypto.onchain._extract_dex_trades": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model._extract_dex_trades"
    },
    "crypto.onchain.find_token_address": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.find_token_address"
    },
    "crypto.onchain.daily_dex_volume_for_given_pair": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_daily_dex_volume_for_given_pair"
    },
    "crypto.onchain.dex_trades_by_exchange": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_dex_trades_by_exchange"
    },
    "crypto.onchain.dex_trades_monthly": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_dex_trades_monthly"
    },
    "crypto.onchain.ethereum_unique_senders": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_ethereum_unique_senders",
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_ethereum_unique_senders",
    },
    "crypto.onchain.most_traded_pairs": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_most_traded_pairs",
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_most_traded_pairs",
    },
    "crypto.onchain.spread_for_crypto_pair": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_spread_for_crypto_pair",
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_spread_for_crypto_pair",
    },
    "crypto.onchain.token_volume_on_dexes": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_token_volume_on_dexes"
    },
    "crypto.onchain.query_graph": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.query_graph"
    },
    "crypto.onchain._make_request": {
        "model": "openbb_terminal.cryptocurrency.onchain.blockchain_model._make_request"
    },
    "crypto.onchain.enrich_social_media": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.enrich_social_media"
    },
    "crypto.onchain.address_history": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_address_history",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_address_history",
    },
    "crypto.onchain.address_info": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_address_info",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_address_info",
    },
    "crypto.onchain.token_decimals": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_decimals"
    },
    "crypto.onchain.token_historical_price": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_historical_price"
    },
    "crypto.onchain.token_history": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_history",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_token_history",
    },
    "crypto.onchain.token_info": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_info",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_token_info",
    },
    "crypto.onchain.top_token_holders": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_top_token_holders",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_top_token_holders",
    },
    "crypto.onchain.tx_info": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_tx_info",
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_tx_info",
    },
    "crypto.onchain.make_request": {
        "model": "openbb_terminal.cryptocurrency.onchain.whale_alert_model.make_request"
    },
    "crypto.onchain.split_cols_with_dot": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.split_cols_with_dot"
    },
    "crypto.onchain.whales_transactions": {
        "model": "openbb_terminal.cryptocurrency.onchain.whale_alert_model.get_whales_transactions",
        "view": "openbb_terminal.cryptocurrency.onchain.whale_alert_view.display_whales_transactions",
    },
    "crypto.overview.altcoin_index": {
        "model": "openbb_terminal.cryptocurrency.overview.blockchaincenter_model.get_altcoin_index",
        "view": "openbb_terminal.cryptocurrency.overview.blockchaincenter_view.display_altcoin_index",
    },
    "crypto.overview._get_coins_info_helper": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model._get_coins_info_helper"
    },
    "crypto.overview.coins_info": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_coins_info"
    },
    "crypto.overview.coins_market_info": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_coins_market_info"
    },
    "crypto.overview.contract_platform": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_contract_platform"
    },
    "crypto.overview.exchanges_market": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_exchanges_market"
    },
    "crypto.overview.list_of_exchanges": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_list_of_exchanges"
    },
    "crypto.overview._parse_post": {
        "model": "openbb_terminal.cryptocurrency.overview.cryptopanic_model._parse_post"
    },
    "crypto.overview.news": {
        "model": "openbb_terminal.cryptocurrency.overview.cryptopanic_model.get_news",
        "view": "openbb_terminal.cryptocurrency.overview.cryptopanic_view.display_news",
    },
    "crypto.overview.make_request": {
        "model": "openbb_terminal.cryptocurrency.overview.cryptopanic_model.make_request"
    },
    "crypto.overview.check_valid_coin": {
        "model": "openbb_terminal.cryptocurrency.overview.loanscan_model.check_valid_coin"
    },
    "crypto.overview.check_valid_platform": {
        "model": "openbb_terminal.cryptocurrency.overview.loanscan_model.check_valid_platform"
    },
    "crypto.overview.rates": {
        "model": "openbb_terminal.cryptocurrency.overview.loanscan_model.get_rates"
    },
    "crypto.overview.holdings_overview": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_holdings_overview",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_holdings_overview",
    },
    "crypto.overview.stable_coins": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_stable_coins"
    },
    "crypto.overview.top_crypto_categories": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_top_crypto_categories"
    },
    "crypto.overview.lambda_coin_formatter": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.lambda_coin_formatter"
    },
    "crypto.overview._make_request": {
        "model": "openbb_terminal.cryptocurrency.overview.rekt_model._make_request"
    },
    "crypto.overview._retry_session": {
        "model": "openbb_terminal.cryptocurrency.overview.rekt_model._retry_session"
    },
    "crypto.overview.crypto_hack": {
        "model": "openbb_terminal.cryptocurrency.overview.rekt_model.get_crypto_hack"
    },
    "crypto.overview.crypto_withdrawal_fees": {
        "model": "openbb_terminal.cryptocurrency.overview.withdrawalfees_model.get_crypto_withdrawal_fees",
        "view": "openbb_terminal.cryptocurrency.overview.withdrawalfees_view.display_crypto_withdrawal_fees",
    },
    "crypto.overview.overall_withdrawal_fees": {
        "model": "openbb_terminal.cryptocurrency.overview.withdrawalfees_model.get_overall_withdrawal_fees",
        "view": "openbb_terminal.cryptocurrency.overview.withdrawalfees_view.display_overall_withdrawal_fees",
    },
    "crypto.tools.calculate_apy": {
        "model": "openbb_terminal.cryptocurrency.tools.tools_model.calculate_apy"
    },
    "crypto.tools.calculate_il": {
        "model": "openbb_terminal.cryptocurrency.tools.tools_model.calculate_il"
    },
    "etf.discovery.etf_movers": {
        "model": "openbb_terminal.etf.discovery.wsj_model.etf_movers"
    },
    "etf.screener.etf_screener": {
        "model": "openbb_terminal.etf.screener.screener_model.etf_screener"
    },
    "forex.candle": {
        "model": "openbb_terminal.forex.forex_helper.load",
        "view": "openbb_terminal.forex.forex_helper.display_candle",
    },
    "forex.load": {"model": "openbb_terminal.forex.forex_helper.load"},
    "forex.oanda.account_summary_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.account_summary_request"
    },
    "forex.oanda.cancel_pending_order_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.cancel_pending_order_request"
    },
    "forex.oanda.close_trades_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.close_trades_request"
    },
    "forex.oanda.create_order_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.create_order_request"
    },
    "forex.oanda.fx_price_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.fx_price_request"
    },
    "forex.oanda.calendar_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.get_calendar_request"
    },
    "forex.oanda.candles_dataframe": {
        "model": "openbb_terminal.forex.oanda.oanda_model.get_candles_dataframe"
    },
    "forex.oanda.open_positions_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.open_positions_request"
    },
    "forex.oanda.open_trades_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.open_trades_request"
    },
    "forex.oanda.order_history_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.order_history_request"
    },
    "forex.oanda.orderbook_plot_data_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.orderbook_plot_data_request"
    },
    "forex.oanda.pending_orders_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.pending_orders_request"
    },
    "forex.oanda.positionbook_plot_data_request": {
        "model": "openbb_terminal.forex.oanda.oanda_model.positionbook_plot_data_request"
    },
    "forex.quote": {"model": "openbb_terminal.forex.av_model.get_quote"},
    "forex.forward_rates": {
        "model": "openbb_terminal.forex.fxempire_model.get_forward_rates"
    },
    "portfolio.brokers.ally.ally_positions_to_df": {
        "model": "openbb_terminal.portfolio.brokers.ally.ally_model.ally_positions_to_df"
    },
    "portfolio.brokers.ally.stock_quote": {
        "model": "openbb_terminal.portfolio.brokers.ally.ally_model.get_stock_quote",
        "view": "openbb_terminal.portfolio.brokers.ally.ally_view.display_stock_quote",
    },
    "portfolio.brokers.ally.top_movers": {
        "model": "openbb_terminal.portfolio.brokers.ally.ally_model.get_top_movers"
    },
    "portfolio.brokers.coinbase.account_history": {
        "model": "openbb_terminal.portfolio.brokers.coinbase.coinbase_model.get_account_history"
    },
    "portfolio.brokers.coinbase.accounts": {
        "model": "openbb_terminal.portfolio.brokers.coinbase.coinbase_model.get_accounts"
    },
    "portfolio.brokers.coinbase.deposits": {
        "model": "openbb_terminal.portfolio.brokers.coinbase.coinbase_model.get_deposits",
        "view": "openbb_terminal.portfolio.brokers.coinbase.coinbase_view.display_deposits",
    },
    "portfolio.brokers.robinhood.historical": {
        "model": "openbb_terminal.portfolio.brokers.robinhood.robinhood_model.get_historical",
        "view": "openbb_terminal.portfolio.brokers.robinhood.robinhood_view.display_historical",
    },
    "portfolio.brokers.robinhood.rh_positions_to_df": {
        "model": "openbb_terminal.portfolio.brokers.robinhood.robinhood_model.rh_positions_to_df"
    },
    "portfolio.portfolio_analysis.load_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_analysis.portfolio_model.load_portfolio"
    },
    "portfolio.portfolio_analysis.country": {
        "model": "openbb_terminal.portfolio.portfolio_analysis.yfinance_model.get_country"
    },
    "portfolio.portfolio_optimization.excel_bl_views": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.excel_model.excel_bl_views"
    },
    "portfolio.portfolio_optimization.load_allocation": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.excel_model.load_allocation"
    },
    "portfolio.portfolio_optimization.load_bl_views": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.excel_model.load_bl_views"
    },
    "portfolio.portfolio_optimization.load_configuration": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.excel_model.load_configuration"
    },
    "portfolio.portfolio_optimization.black_litterman": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.black_litterman",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_black_litterman",
    },
    "portfolio.portfolio_optimization.generate_random_portfolios": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.generate_random_portfolios"
    },
    "portfolio.portfolio_optimization.black_litterman_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_black_litterman_portfolio"
    },
    "portfolio.portfolio_optimization.equal_weights": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_equal_weights"
    },
    "portfolio.portfolio_optimization.hcp_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_hcp_portfolio"
    },
    "portfolio.portfolio_optimization.max_decorrelation_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_max_decorrelation_portfolio"
    },
    "portfolio.portfolio_optimization.max_diversification_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_max_diversification_portfolio"
    },
    "portfolio.portfolio_optimization.mean_risk_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_mean_risk_portfolio"
    },
    "portfolio.portfolio_optimization.property_weights": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_property_weights"
    },
    "portfolio.portfolio_optimization.rel_risk_parity_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_rel_risk_parity_portfolio"
    },
    "portfolio.portfolio_optimization.risk_parity_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_risk_parity_portfolio"
    },
    "portfolio.portfolio_optimization.process_returns": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.yahoo_finance_model.process_returns"
    },
    "portfolio.portfolio_optimization.process_stocks": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.yahoo_finance_model.process_stocks"
    },
    "stocks.backtesting.buy_and_hold": {
        "model": "openbb_terminal.stocks.backtesting.bt_model.buy_and_hold"
    },
    "stocks.backtesting.ema_cross_strategy": {
        "model": "openbb_terminal.stocks.backtesting.bt_model.ema_cross_strategy"
    },
    "stocks.backtesting.ema_strategy": {
        "model": "openbb_terminal.stocks.backtesting.bt_model.ema_strategy"
    },
    "stocks.backtesting.data": {
        "model": "openbb_terminal.stocks.backtesting.bt_model.get_data"
    },
    "stocks.backtesting.rsi_strategy": {
        "model": "openbb_terminal.stocks.backtesting.bt_model.rsi_strategy",
        "view": "openbb_terminal.stocks.backtesting.bt_view.display_rsi_strategy",
    },
    "stocks.behavioural_analysis.cramer_daily": {
        "model": "openbb_terminal.stocks.behavioural_analysis.cramer_model.get_cramer_daily",
        "view": "openbb_terminal.stocks.behavioural_analysis.cramer_view.display_cramer_daily",
    },
    "stocks.behavioural_analysis.cramer_ticker": {
        "model": "openbb_terminal.stocks.behavioural_analysis.cramer_model.get_cramer_ticker",
        "view": "openbb_terminal.stocks.behavioural_analysis.cramer_view.display_cramer_ticker",
    },
    "stocks.behavioural_analysis.company_news": {
        "model": "openbb_terminal.stocks.behavioural_analysis.finnhub_model.get_company_news"
    },
    "stocks.behavioural_analysis.process_news_headlines_sentiment": {
        "model": "openbb_terminal.stocks.behavioural_analysis.finnhub_model.process_news_headlines_sentiment"
    },
    "stocks.candle": {
        "model": "openbb_terminal.stocks.stocks_helper.load",
        "view": "openbb_terminal.stocks.stocks_helper.display_candle",
    },
    "stocks.process_candle": {
        "model": "openbb_terminal.stocks.stocks_helper.process_candle"
    },
    "stocks.comparison_analysis.find_smallest_num_data_point": {
        "model": "openbb_terminal.stocks.comparison_analysis.finbrain_model.find_smallest_num_data_point"
    },
    "stocks.comparison_analysis.sentiments": {
        "model": "openbb_terminal.stocks.comparison_analysis.finbrain_model.get_sentiments"
    },
    "stocks.comparison_analysis.similar_companies": {
        "model": "openbb_terminal.stocks.comparison_analysis.polygon_model.get_similar_companies"
    },
    "stocks.comparison_analysis.comparison_data": {
        "model": "openbb_terminal.stocks.comparison_analysis.finviz_compare_model.get_comparison_data"
    },
    "stocks.comparison_analysis.combine_similar_financials": {
        "model": "openbb_terminal.stocks.comparison_analysis.marketwatch_model.combine_similar_financials"
    },
    "stocks.comparison_analysis.financial_comparisons": {
        "model": "openbb_terminal.stocks.comparison_analysis.marketwatch_model.get_financial_comparisons"
    },
    "stocks.comparison_analysis.prepare_comparison_financials": {
        "model": "openbb_terminal.stocks.comparison_analysis.marketwatch_model.prepare_comparison_financials"
    },
    "stocks.comparison_analysis.prepare_df_financials": {
        "model": "openbb_terminal.stocks.comparison_analysis.marketwatch_model.prepare_df_financials"
    },
    "stocks.comparison_analysis.historical": {
        "model": "openbb_terminal.stocks.comparison_analysis.yahoo_finance_model.get_historical",
        "view": "openbb_terminal.stocks.comparison_analysis.yahoo_finance_view.display_historical",
    },
    "stocks.comparison_analysis.sp500_comps_tsne": {
        "model": "openbb_terminal.stocks.comparison_analysis.yahoo_finance_model.get_sp500_comps_tsne"
    },
    "stocks.dark_pool_shorts.getATSdata": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.finra_model.getATSdata"
    },
    "stocks.dark_pool_shorts.getFINRAdata": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.finra_model.getFINRAdata"
    },
    "stocks.dark_pool_shorts.getFINRAdata_offset": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.finra_model.getFINRAdata_offset"
    },
    "stocks.dark_pool_shorts.getFINRAweeks": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.finra_model.getFINRAweeks"
    },
    "stocks.dark_pool_shorts.getTickerFINRAdata": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.finra_model.getTickerFINRAdata"
    },
    "stocks.dark_pool_shorts.short_data_by_exchange": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.nyse_model.get_short_data_by_exchange"
    },
    "stocks.dark_pool_shorts.short_interest": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.quandl_model.get_short_interest",
        "view": "openbb_terminal.stocks.dark_pool_shorts.quandl_view.short_interest",
    },
    "stocks.dark_pool_shorts.catching_diff_url_formats": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.sec_model.catching_diff_url_formats"
    },
    "stocks.dark_pool_shorts.fails_to_deliver": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.sec_model.get_fails_to_deliver",
        "view": "openbb_terminal.stocks.dark_pool_shorts.sec_view.fails_to_deliver",
    },
    "stocks.dark_pool_shorts.dark_pool_short_positions": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_model.get_dark_pool_short_positions",
        "view": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_view.dark_pool_short_positions",
    },
    "stocks.dark_pool_shorts.net_short_position": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_model.get_net_short_position",
        "view": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_view.net_short_position",
    },
    "stocks.dark_pool_shorts.short_interest_days_to_cover": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_model.get_short_interest_days_to_cover",
        "view": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_view.short_interest_days_to_cover",
    },
    "stocks.dark_pool_shorts.short_interest_volume": {
        "model": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_model.get_short_interest_volume",
        "view": "openbb_terminal.stocks.dark_pool_shorts.stockgrid_view.short_interest_volume",
    },
    "stocks.discovery.add_order_total": {
        "model": "openbb_terminal.stocks.discovery.ark_model.add_order_total"
    },
    "stocks.discovery.ipo_calendar": {
        "model": "openbb_terminal.stocks.discovery.finnhub_model.get_ipo_calendar"
    },
    "stocks.discovery.dividend_cal": {
        "model": "openbb_terminal.stocks.discovery.nasdaq_model.get_dividend_cal"
    },
    "stocks.discovery.article_data": {
        "model": "openbb_terminal.stocks.discovery.seeking_alpha_model.get_article_data"
    },
    "stocks.discovery.articles_html": {
        "model": "openbb_terminal.stocks.discovery.seeking_alpha_model.get_articles_html"
    },
    "stocks.discovery.earnings_html": {
        "model": "openbb_terminal.stocks.discovery.seeking_alpha_model.get_earnings_html"
    },
    "stocks.discovery.news": {
        "model": "openbb_terminal.stocks.discovery.seeking_alpha_model.get_news",
        "view": "openbb_terminal.stocks.discovery.seeking_alpha_view.news",
    },
    "stocks.discovery.news_html": {
        "model": "openbb_terminal.stocks.discovery.seeking_alpha_model.get_news_html"
    },
    "stocks.discovery.next_earnings": {
        "model": "openbb_terminal.stocks.discovery.seeking_alpha_model.get_next_earnings"
    },
    "stocks.discovery.trending_list": {
        "model": "openbb_terminal.stocks.discovery.seeking_alpha_model.get_trending_list"
    },
    "stocks.due_diligence.ark_trades_by_ticker": {
        "model": "openbb_terminal.stocks.due_diligence.ark_model.get_ark_trades_by_ticker"
    },
    "stocks.due_diligence.estimates": {
        "model": "openbb_terminal.stocks.due_diligence.business_insider_model.get_estimates",
        "view": "openbb_terminal.stocks.due_diligence.business_insider_view.estimates",
    },
    "stocks.due_diligence.price_target_from_analysts": {
        "model": "openbb_terminal.stocks.due_diligence.business_insider_model.get_price_target_from_analysts",
        "view": "openbb_terminal.stocks.due_diligence.business_insider_view.price_target_from_analysts",
    },
    "stocks.due_diligence.customers": {
        "model": "openbb_terminal.stocks.due_diligence.csimarket_model.get_customers",
        "view": "openbb_terminal.stocks.due_diligence.csimarket_view.customers",
    },
    "stocks.due_diligence.suppliers": {
        "model": "openbb_terminal.stocks.due_diligence.csimarket_model.get_suppliers",
        "view": "openbb_terminal.stocks.due_diligence.csimarket_view.suppliers",
    },
    "stocks.due_diligence.rating_over_time": {
        "model": "openbb_terminal.stocks.due_diligence.finnhub_model.get_rating_over_time",
        "view": "openbb_terminal.stocks.due_diligence.finnhub_view.rating_over_time",
    },
    "stocks.due_diligence.analyst_data": {
        "model": "openbb_terminal.stocks.due_diligence.finviz_model.get_analyst_data"
    },
    "stocks.due_diligence.news": {
        "model": "openbb_terminal.stocks.due_diligence.finviz_model.get_news",
        "view": "openbb_terminal.stocks.due_diligence.finviz_view.news",
    },
    "stocks.due_diligence.rating": {
        "model": "openbb_terminal.stocks.due_diligence.fmp_model.get_rating",
        "view": "openbb_terminal.stocks.due_diligence.fmp_view.rating",
    },
    "stocks.due_diligence.sec_filings": {
        "model": "openbb_terminal.stocks.due_diligence.marketwatch_model.get_sec_filings",
        "view": "openbb_terminal.stocks.due_diligence.marketwatch_view.sec_filings",
    },
    "stocks.fundamental_analysis.color_mscore": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.color_mscore"
    },
    "stocks.fundamental_analysis.color_zscore_mckee": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.color_zscore_mckee"
    },
    "stocks.fundamental_analysis.df_values": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.df_values"
    },
    "stocks.fundamental_analysis.balance_sheet": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_balance_sheet",
        "view": "openbb_terminal.stocks.fundamental_analysis.av_view.display_balance_sheet",
    },
    "stocks.fundamental_analysis.cash_flow": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_cash_flow",
        "view": "openbb_terminal.stocks.fundamental_analysis.av_view.display_cash_flow",
    },
    "stocks.fundamental_analysis.dupont": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_dupont",
        "view": "openbb_terminal.stocks.fundamental_analysis.av_view.display_dupont",
    },
    "stocks.fundamental_analysis.earnings": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_earnings",
        "view": "openbb_terminal.stocks.fundamental_analysis.av_view.display_earnings",
    },
    "stocks.fundamental_analysis.fraud_ratios": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_fraud_ratios"
    },
    "stocks.fundamental_analysis.income_statements": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_income_statements"
    },
    "stocks.fundamental_analysis.key_metrics": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_key_metrics"
    },
    "stocks.fundamental_analysis.overview": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_overview",
        "view": "openbb_terminal.stocks.fundamental_analysis.av_view.display_overview",
    },
    "stocks.fundamental_analysis.replace_df": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.replace_df"
    },
    "stocks.fundamental_analysis.management": {
        "model": "openbb_terminal.stocks.fundamental_analysis.business_insider_model.get_management",
        "view": "openbb_terminal.stocks.fundamental_analysis.business_insider_view.display_management",
    },
    "stocks.fundamental_analysis.clean_dataframes": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.clean_dataframes"
    },
    "stocks.fundamental_analysis.create_dataframe": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.create_dataframe"
    },
    "stocks.fundamental_analysis.frac": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.frac"
    },
    "stocks.fundamental_analysis.generate_path": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.generate_path"
    },
    "stocks.fundamental_analysis.fama_coe": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.get_fama_coe"
    },
    "stocks.fundamental_analysis.historical_5": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.get_historical_5"
    },
    "stocks.fundamental_analysis.similar_dfs": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.get_similar_dfs"
    },
    "stocks.fundamental_analysis.value": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.get_value"
    },
    "stocks.fundamental_analysis.insert_row": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.insert_row"
    },
    "stocks.fundamental_analysis.others_in_sector": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.others_in_sector"
    },
    "stocks.fundamental_analysis.set_cell": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.set_cell"
    },
    "stocks.fundamental_analysis.string_float": {
        "model": "openbb_terminal.stocks.fundamental_analysis.dcf_model.string_float"
    },
    "stocks.fundamental_analysis.filings_analysis": {
        "model": "openbb_terminal.stocks.fundamental_analysis.eclect_us_model.get_filings_analysis"
    },
    "stocks.fundamental_analysis.data": {
        "model": "openbb_terminal.stocks.fundamental_analysis.finviz_model.get_data"
    },
    "stocks.fundamental_analysis.sean_seah_warnings": {
        "model": "openbb_terminal.stocks.fundamental_analysis.market_watch_model.get_sean_seah_warnings",
        "view": "openbb_terminal.stocks.fundamental_analysis.market_watch_view.display_sean_seah_warnings",
    },
    "stocks.fundamental_analysis.prepare_df_financials": {
        "model": "openbb_terminal.stocks.fundamental_analysis.market_watch_model.prepare_df_financials"
    },
    "stocks.fundamental_analysis.financials": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_financials"
    },
    "stocks.fundamental_analysis.calendar_earnings": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_calendar_earnings",
        "view": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_view.display_calendar_earnings",
    },
    "stocks.fundamental_analysis.dividends": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_dividends",
        "view": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_view.display_dividends",
    },
    "stocks.fundamental_analysis.hq": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_hq"
    },
    "stocks.fundamental_analysis.info": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_info",
        "view": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_view.display_info",
    },
    "stocks.fundamental_analysis.mktcap": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_mktcap",
        "view": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_view.display_mktcap",
    },
    "stocks.fundamental_analysis.shareholders": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_shareholders",
        "view": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_view.display_shareholders",
    },
    "stocks.fundamental_analysis.splits": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_splits",
        "view": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_view.display_splits",
    },
    "stocks.fundamental_analysis.sustainability": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_sustainability",
        "view": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_view.display_sustainability",
    },
    "stocks.fundamental_analysis.website": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_website"
    },
    "stocks.fundamental_analysis.yield_curve": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yield_curve_model.get_yield_curve"
    },
    "stocks.fundamental_analysis.yield_curve_year": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yield_curve_model.get_yield_curve_year"
    },
    # "stocks.fundamental_analysis.financial_modeling_prep.clean_metrics_df": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_model.clean_metrics_df"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.balance": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_model.get_balance"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.cash": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_model.get_cash"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.dcf": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_model.get_dcf"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.enterprise": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_view.display_enterprise"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.financial_growth": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_model.get_financial_growth"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.income": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_model.get_income"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.key_metrics": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_view.display_key_metrics"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.key_ratios": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_model.get_key_ratios"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.profile": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_view.display_profile"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.quote": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_view.display_quote"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.score": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_model.get_score"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.balance_sheet": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_view.display_balance_sheet"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.cash_flow": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_view.display_cash_flow"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.discounted_cash_flow": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.
    #     financial_modeling_prep.fmp_view.display_discounted_cash_flow"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.financial_ratios": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.
    #     financial_modeling_prep.fmp_view.display_financial_ratios"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.financial_statement_growth": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.
    #     financial_modeling_prep.fmp_view.display_financial_statement_growth"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.income_statement": {
    #     "model": "openbb_terminal.stocks.
    #     fundamental_analysis.financial_modeling_prep.fmp_view.display_income_statement"
    # },
    # "stocks.fundamental_analysis.financial_modeling_prep.valinvest_score": {
    #     "model": "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_view.valinvest_score"
    # },
    "stocks.government.analyze_qtr_contracts": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.analyze_qtr_contracts"
    },
    "stocks.government.government_trading": {
        "model": "openbb_terminal.stocks.government.quiverquant_model.get_government_trading",
        "view": "openbb_terminal.stocks.government.quiverquant_view.display_government_trading",
    },
    "stocks.insider.insider_activity": {
        "model": "openbb_terminal.stocks.insider.businessinsider_model.get_insider_activity",
        "view": "openbb_terminal.stocks.insider.businessinsider_view.insider_activity",
    },
    "stocks.insider.last_insider_activity": {
        "model": "openbb_terminal.stocks.insider.finviz_model.get_last_insider_activity",
        "view": "openbb_terminal.stocks.insider.finviz_view.last_insider_activity",
    },
    "stocks.insider.check_boolean_list": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_boolean_list"
    },
    "stocks.insider.check_dates": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_dates"
    },
    "stocks.insider.check_in_list": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_in_list"
    },
    "stocks.insider.check_int_in_list": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_int_in_list"
    },
    "stocks.insider.check_open_insider_company_totals": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_open_insider_company_totals"
    },
    "stocks.insider.check_open_insider_date": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_open_insider_date"
    },
    "stocks.insider.check_open_insider_general": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_open_insider_general"
    },
    "stocks.insider.check_open_insider_industry": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_open_insider_industry"
    },
    "stocks.insider.check_open_insider_insider_title": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_open_insider_insider_title"
    },
    "stocks.insider.check_open_insider_others": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_open_insider_others"
    },
    "stocks.insider.check_open_insider_screener": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_open_insider_screener"
    },
    "stocks.insider.check_open_insider_transaction_filing": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_open_insider_transaction_filing"
    },
    "stocks.insider.check_valid_multiple": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_valid_multiple"
    },
    "stocks.insider.check_valid_range": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.check_valid_range"
    },
    "stocks.insider.open_insider_data": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.get_open_insider_data"
    },
    "stocks.insider.open_insider_link": {
        "model": "openbb_terminal.stocks.insider.openinsider_model.get_open_insider_link"
    },
    "stocks.load": {"model": "openbb_terminal.stocks.stocks_helper.load"},
    "stocks.options.put_call_ratio": {
        "model": "openbb_terminal.stocks.options.alphaquery_model.get_put_call_ratio",
        "view": "openbb_terminal.stocks.options.alphaquery_view.display_put_call_ratio",
    },
    "stocks.options.options_info": {
        "model": "openbb_terminal.stocks.options.barchart_model.get_options_info"
    },
    "stocks.options.pnl_calculator": {
        "model": "openbb_terminal.stocks.options.calculator_model.pnl_calculator"
    },
    "stocks.options.option_history": {
        "model": "openbb_terminal.stocks.options.chartexchange_model.get_option_history"
    },
    "stocks.options.unusual_options": {
        "model": "openbb_terminal.stocks.options.fdscanner_model.unusual_options"
    },
    "stocks.options.historical_options": {
        "model": "openbb_terminal.stocks.options.tradier_model.get_historical_options"
    },
    "stocks.options.option_chains": {
        "model": "openbb_terminal.stocks.options.tradier_model.get_option_chains"
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
    "stocks.options.info": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_info"
    },
    "stocks.options.iv_surface": {
        "model": "openbb_terminal.stocks.options.yfinance_model.get_iv_surface"
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
    "stocks.options.hedge.add_hedge_option": {
        "model": "openbb_terminal.stocks.options.hedge.hedge_model.add_hedge_option"
    },
    "stocks.options.hedge.calc_delta": {
        "model": "openbb_terminal.stocks.options.hedge.hedge_model.calc_delta"
    },
    "stocks.options.hedge.calc_gamma": {
        "model": "openbb_terminal.stocks.options.hedge.hedge_model.calc_gamma"
    },
    "stocks.options.hedge.calc_hedge": {
        "model": "openbb_terminal.stocks.options.hedge.hedge_model.calc_hedge"
    },
    "stocks.options.hedge.calc_vega": {
        "model": "openbb_terminal.stocks.options.hedge.hedge_model.calc_vega"
    },
    "stocks.options.screen.check_presets": {
        "model": "openbb_terminal.stocks.options.screen.syncretism_model.check_presets"
    },
    "stocks.options.screen.historical_greeks": {
        "model": "openbb_terminal.stocks.options.screen.syncretism_model.get_historical_greeks"
    },
    "stocks.options.screen.screener_output": {
        "model": "openbb_terminal.stocks.options.screen.syncretism_model.get_screener_output"
    },
    "stocks.quantitative_analysis.capm_information": {
        "model": "openbb_terminal.stocks.quantitative_analysis.factors_model.capm_information"
    },
    "stocks.quantitative_analysis.historical_5": {
        "model": "openbb_terminal.stocks.quantitative_analysis.factors_model.get_historical_5"
    },
    "stocks.screener.screener_data": {
        "model": "openbb_terminal.stocks.screener.finviz_model.get_screener_data"
    },
    "stocks.sector_industry_analysis.filter_stocks": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.filter_stocks"
    },
    "stocks.sector_industry_analysis.companies_per_country_in_industry": {
        "model": "openbb_terminal.stocks.sector_industry_analysis."
        "financedatabase_model.get_companies_per_country_in_industry",
        "view": "openbb_terminal.stocks.sector_industry_analysis."
        "financedatabase_view.display_companies_per_country_in_industry",
    },
    "stocks.sector_industry_analysis.companies_per_country_in_sector": {
        "model": "openbb_terminal.stocks.sector_industry_analysis."
        "financedatabase_model.get_companies_per_country_in_sector",
        "view": "openbb_terminal.stocks.sector_industry_analysis."
        "financedatabase_view.display_companies_per_country_in_sector",
    },
    "stocks.sector_industry_analysis.companies_per_industry_in_country": {
        "model": "openbb_terminal.stocks.sector_industry_analysis."
        "financedatabase_model.get_companies_per_industry_in_country",
        "view": "openbb_terminal.stocks.sector_industry_analysis."
        "financedatabase_view.display_companies_per_industry_in_country",
    },
    "stocks.sector_industry_analysis.companies_per_industry_in_sector": {
        "model": "openbb_terminal.stocks.sector_industry_analysis."
        "financedatabase_model.get_companies_per_industry_in_sector",
        "view": "openbb_terminal.stocks.sector_industry_analysis."
        "financedatabase_view.display_companies_per_industry_in_sector",
    },
    "stocks.sector_industry_analysis.companies_per_sector_in_country": {
        "model": "openbb_terminal.stocks.sector_industry_analysis."
        "financedatabase_model.get_companies_per_sector_in_country",
        "view": "openbb_terminal.stocks.sector_industry_analysis."
        "financedatabase_view.display_companies_per_sector_in_country",
    },
    "stocks.sector_industry_analysis.countries": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_countries"
    },
    "stocks.sector_industry_analysis.industries": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_industries"
    },
    "stocks.sector_industry_analysis.sectors": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_model.get_sectors"
    },
    "stocks.sector_industry_analysis.stocks_data": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.stockanalysis_model.get_stocks_data"
    },
    "stocks.sector_industry_analysis.change_type_dataframes": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.stockanalysis_model.change_type_dataframes"
    },
    "stocks.sector_industry_analysis.match_length_dataframes": {
        "model": "openbb_terminal.stocks.sector_industry_analysis.stockanalysis_model.match_length_dataframes"
    },
    "stocks.technical_analysis.technical_summary_report": {
        "model": "openbb_terminal.stocks.technical_analysis.finbrain_model.get_technical_summary_report",
        "view": "openbb_terminal.stocks.technical_analysis.finbrain_view.technical_summary_report",
    },
    "stocks.technical_analysis.pattern_recognition": {
        "model": "openbb_terminal.stocks.technical_analysis.finnhub_model.get_pattern_recognition"
    },
    "stocks.technical_analysis.finviz_image": {
        "model": "openbb_terminal.stocks.technical_analysis.finviz_model.get_finviz_image"
    },
    "stocks.technical_analysis.tradingview_recommendation": {
        "model": "openbb_terminal.stocks.technical_analysis.tradingview_model.get_tradingview_recommendation"
    },
    "stocks.tradinghours.check_if_open": {
        "model": "openbb_terminal.stocks.tradinghours.bursa_model.check_if_open"
    },
    "stocks.tradinghours.bursa": {
        "model": "openbb_terminal.stocks.tradinghours.bursa_model.get_bursa"
    },
}
"""
api = Loader(functions=functions)
api.stocks.get_news()
api.economy.bigmac(chart=True)
api.economy.bigmac(chart=False)


TO USE THE API DIRECTLY JUST IMPORT IT:
from openbb_terminal.api import openbb (or: from openbb_terminal.api import openbb as api)
"""


def copy_func(f) -> Callable:
    """Copies the contents and attributes of the entered function. Based on https://stackoverflow.com/a/13503277

    Parameters
    ----------
    f: Callable
        Function to be copied

    Returns
    -------
    g: Callable
        New function
    """
    g = types.FunctionType(
        f.__code__,
        f.__globals__,
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g


def change_docstring(api_callable, model: Callable, view=None):
    """Changes docstring of the entered api_callable

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
    if view is not None:
        index = view.__doc__.find("Parameters")
        all_parameters = (
            "\nAPI function, use the chart kwarg for getting the view model and it's plot. "
            "See every parmater below:\n\n\t"
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
        api_callable.__signature__ = signature(view).replace(
            parameters=parameters + chart_parameter
        )
    else:
        api_callable.__doc__ = model.__doc__
        api_callable.__name__ = model.__name__
        api_callable.__signature__ = signature(model)

    return api_callable


class FunctionFactory:
    """The API Function Factory, which creates the callable instance"""

    def __init__(self, model: Callable, view: Optional[Callable] = None):
        """Initialises the FunctionFactory instance

        Parameters
        ----------
        model: Callable
            The original model function from the terminal
        view: Callable
            The original view function from the terminal, this shall be set to None if the
            function has no charting
        """
        self.model_only = False
        if view is None:
            self.model_only = True
            self.model = copy_func(model)
        else:
            self.model = copy_func(model)
            self.view = copy_func(view)

    def api_callable(self, *args, **kwargs):
        """This returns the result of the command from the view or the model function based on the chart parameter

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
    """Creates a filler callable for the menus"""

    def __init__(self, function: Callable):
        self.__function = function

    def __call__(self, *args, **kwargs):
        print(self.__function(*args, **kwargs))

    def __repr__(self):
        return self.__function()


class Loader:
    """The Loader class"""

    def __init__(self, funcs: dict):
        print(
            "WARNING! Breaking changes incoming! Especially avoid using kwargs, since some of them will change.\n"
            "You can try <link> branch with the latest changes."
        )
        self.__function_map = self.build_function_map(funcs=funcs)
        self.load_menus()

    def __call__(self):
        """Prints help message"""
        print(self.__repr__())

    def __repr__(self):
        return """This is the API of the OpenBB Terminal.

        Use the API to get data directly into your jupyter notebook or directly use it in your application.

        ...

        For more information see the official documentation at: https://openbb-finance.github.io/OpenBBTerminal/api/
        """

    # TODO: Add settings
    def settings(self):
        pass

    def load_menus(self):
        """Creates the API structure (see openbb.stocks.command) by setting attributes and saving the functions"""

        def menu_message(menu: str, function_map: dict):
            """Creates a callable function, which prints a menus help message

            Parameters
            ----------
            menu: str
                Menu for which the help message is generated
            function_map: dict
                Dictionary with the functions and their virtual paths

            Returns
            -------
            Callable:
                Function which prints help message
            """
            filtered_dict = {k: v for (k, v) in function_map.items() if menu in k}

            def f():
                string = menu.upper() + " Menu\n\nThe api commands of the the menu:"
                for command in filtered_dict:
                    string += "\n\t<openbb>." + command
                return string

            return f

        function_map = self.__function_map
        for virtual_path, function in function_map.items():
            virtual_path_split = virtual_path.split(".")
            last_virtual_path = virtual_path_split[-1]

            previous_menu = self
            for menu in virtual_path_split[:-1]:
                if not hasattr(previous_menu, menu):
                    next_menu = MenuFiller(function=menu_message(menu, function_map))
                    previous_menu.__setattr__(menu, next_menu)
                    previous_menu = previous_menu.__getattribute__(menu)
                else:
                    previous_menu = previous_menu.__getattribute__(menu)
            previous_menu.__setattr__(last_virtual_path, function)

    @staticmethod
    def load_module(module_path: str) -> Optional[types.ModuleType]:
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

    @classmethod
    def get_function(cls, function_path: str) -> Callable:
        """Get function from string path

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
        module = cls.load_module(module_path=module_path)

        return getattr(module, function_name)

    @classmethod
    def build_function_map(cls, funcs: dict) -> dict:
        """Builds dictionary with FunctionFactory instances as items

        Parameters
        ----------
        funcs: dict
            Dictionary which has string path of view and model functions as keys. The items is dictionary with
            the view and model function as items of the respectivee "view" and "model" keys

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
                    model=model_function, view=view_function
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
                    "View function without model function : %s", view_function
                )

        return function_map


openbb = Loader(funcs=functions)
