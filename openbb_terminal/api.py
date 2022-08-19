"""OpenBB Terminal API."""
# flake8: noqa
# pylint: disable=unused-import
from .stocks import stocks_api as stocks
from .alternative import alt_api as alt
from .cryptocurrency import crypto_api as crypto
from .economy import economy_api as economy
from .econometrics import econometrics_api as econometrics
from .etf import etf_api as etf
from .forex import forex_api as forex
from .mutual_funds import mutual_fund_api as funds
from .portfolio import portfolio_api as portfolio
from .reports import widget_helpers as widgets
from .config_terminal import theme

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
    "alt.oss.startups": {
        "model": "openbb_terminal.alternative.oss.runa_model.get_startups"
    },
    "alt.oss.ross": {
        "view": "openbb_terminal.alternative.oss.runa_view.display_rossindex"
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
    "stocks.ba.reddit_sent": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_posts_about",
        "view": "openbb_terminal.common.behavioural_analysis.reddit_view.display_reddit_sent",
    },
    "stocks.ba.text_sent": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_sentiment"
    },
    "stocks.ba.spac": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_spac"
    },
    "stocks.ba.spac_c": {
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
    "common.ba.bullbear": {
        "model": "openbb_terminal.common.behavioural_analysis.stocktwits_model.get_bullbear"
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
    "stocks.ba.bullbear": {
        "view": "openbb_terminal.common.behavioural_analysis.stocktwits_view.display_bullbear"
    },
    "stocks.ba.infer": {
        "model": "openbb_terminal.common.behavioural_analysis.twitter_model.load_analyze_tweets",
        "view": "openbb_terminal.common.behavioural_analysis.twitter_view.display_inference",
    },
    "stocks.ba.sentiment": {
        "model": "openbb_terminal.common.behavioural_analysis.twitter_model.get_sentiment",
        "view": "openbb_terminal.common.behavioural_analysis.twitter_view.display_sentiment",
    },
    "etf.get_news": {"model": "openbb_terminal.common.newsapi_model.get_news"},
    "etf.display_news": {"view": "openbb_terminal.common.newsapi_view.display_news"},
    "common.pred.arima_model": {
        "model": "openbb_terminal.common.prediction_techniques.arima_model.get_arima_model"
    },
    "stocks.pred.arima": {
        "view": "openbb_terminal.common.prediction_techniques.arima_view.display_arima"
    },
    "common.pred.exponential_smoothing_model": {
        "model": "openbb_terminal.common.prediction_techniques.ets_model.get_exponential_smoothing_model"
    },
    "stocks.pred.ets": {
        "view": "openbb_terminal.common.prediction_techniques.ets_view.display_exponential_smoothing"
    },
    "common.pred.knn_model_data": {
        "model": "openbb_terminal.common.prediction_techniques.knn_model.get_knn_model_data"
    },
    "stocks.pred.knn": {
        "view": "openbb_terminal.common.prediction_techniques.knn_view.display_k_nearest_neighbors"
    },
    "common.pred.mc_brownian": {
        "model": "openbb_terminal.common.prediction_techniques.mc_model.get_mc_brownian"
    },
    "stocks.pred.mc": {
        "view": "openbb_terminal.common.prediction_techniques.mc_view.display_mc_forecast"
    },
    "common.pred.build_neural_network_model": {
        "model": "openbb_terminal.common.prediction_techniques.neural_networks_model.build_neural_network_model"
    },
    "common.pred.conv1d_model": {
        "model": "openbb_terminal.common.prediction_techniques.neural_networks_model.conv1d_model"
    },
    "common.pred.lstm_model": {
        "model": "openbb_terminal.common.prediction_techniques.neural_networks_model.lstm_model"
    },
    "common.pred.mlp_model": {
        "model": "openbb_terminal.common.prediction_techniques.neural_networks_model.mlp_model"
    },
    "common.pred.rnn_model": {
        "model": "openbb_terminal.common.prediction_techniques.neural_networks_model.rnn_model"
    },
    "stocks.pred.conv1d": {
        "view": "openbb_terminal.common.prediction_techniques.neural_networks_view.display_conv1d"
    },
    "stocks.pred.lstm": {
        "view": "openbb_terminal.common.prediction_techniques.neural_networks_view.display_lstm"
    },
    "stocks.pred.mlp": {
        "view": "openbb_terminal.common.prediction_techniques.neural_networks_view.display_mlp"
    },
    "stocks.pred.rnn": {
        "view": "openbb_terminal.common.prediction_techniques.neural_networks_view.display_rnn"
    },
    "common.pred.regression_model": {
        "model": "openbb_terminal.common.prediction_techniques.regression_model.get_regression_model"
    },
    "common.pred.split_train": {
        "model": "openbb_terminal.common.prediction_techniques.regression_model.split_train"
    },
    "stocks.pred.regression": {
        "view": "openbb_terminal.common.prediction_techniques.regression_view.display_regression"
    },
    "common.qa.calculate_adjusted_var": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.calculate_adjusted_var"
    },
    "common.qa.es": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_es",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_es",
    },
    "common.qa.normality": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_normality"
    },
    "common.qa.omega": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_omega",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_omega",
    },
    "common.qa.seasonal_decomposition": {
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
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_summary"
    },
    "common.qa.unitroot": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_unitroot"
    },
    "common.qa.var": {
        "model": "openbb_terminal.common.quantitative_analysis.qa_model.get_var",
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_var",
    },
    "stocks.qa.acf": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_acf"
    },
    "stocks.qa.bw": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_bw"
    },
    "stocks.qa.cdf": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_cdf"
    },
    "stocks.qa.cusum": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_cusum"
    },
    "stocks.qa.hist": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_hist"
    },
    "stocks.qa.line": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_line"
    },
    "stocks.qa.normality": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_normality"
    },
    "stocks.qa.qqplot": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_qqplot"
    },
    "stocks.qa.raw": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_raw"
    },
    "stocks.qa.decompose": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_seasonal"
    },
    "stocks.qa.summary": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_summary"
    },
    "stocks.qa.unitroot": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.display_unitroot"
    },
    "common.qa.lambda_color_red": {
        "view": "openbb_terminal.common.quantitative_analysis.qa_view.lambda_color_red"
    },
    "common.qa.kurtosis": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_kurtosis"
    },
    "common.qa.quantile": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_quantile"
    },
    "common.qa.rolling_avg": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_rolling_avg"
    },
    "common.qa.skew": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_skew"
    },
    "common.qa.spread": {
        "model": "openbb_terminal.common.quantitative_analysis.rolling_model.get_spread"
    },
    "stocks.qa.kurtosis": {
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_kurtosis"
    },
    "stocks.qa.rolling": {
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_mean_std"
    },
    "stocks.qa.quantile": {
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_quantile"
    },
    "stocks.qa.skew": {
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_skew"
    },
    "stocks.qa.spread": {
        "view": "openbb_terminal.common.quantitative_analysis.rolling_view.display_spread"
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
    "common.ta.ma": {
        "view": "openbb_terminal.common.technical_analysis.overlap_view.view_ma"
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
    "crypto.defi._prepare_params": {
        "model": "openbb_terminal.cryptocurrency.defi.coindix_model._prepare_params"
    },
    "crypto.defi.defi_vaults": {
        "model": "openbb_terminal.cryptocurrency.defi.coindix_model.get_defi_vaults"
    },
    "crypto.defi.vaults": {
        "view": "openbb_terminal.cryptocurrency.defi.coindix_view.display_defi_vaults"
    },
    "crypto.defi.anchor_data": {
        "model": "openbb_terminal.cryptocurrency.defi.defipulse_model.get_defipulse_index",
        "view": "openbb_terminal.cryptocurrency.defi.cryptosaurio_view.display_anchor_data",
    },
    "crypto.defi.dpi": {
        "view": "openbb_terminal.cryptocurrency.defi.defipulse_view.display_defipulse"
    },
    "crypto.defi.last_uni_swaps": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_last_uni_swaps"
    },
    "crypto.defi.uni_pools_by_volume": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_uni_pools_by_volume"
    },
    "crypto.defi.uni_tokens": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_uni_tokens"
    },
    "crypto.defi.uniswap_pool_recently_added": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_uniswap_pool_recently_added"
    },
    "crypto.defi.uniswap_stats": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.get_uniswap_stats"
    },
    "crypto.defi.query_graph": {
        "model": "openbb_terminal.cryptocurrency.defi.graph_model.query_graph"
    },
    "crypto.defi.swaps": {
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_last_uni_swaps"
    },
    "crypto.defi.pairs": {
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_recently_added"
    },
    "crypto.defi.pools": {
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_uni_pools"
    },
    "crypto.defi.stats": {
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_uni_stats"
    },
    "crypto.defi.tokens": {
        "view": "openbb_terminal.cryptocurrency.defi.graph_view.display_uni_tokens"
    },
    "crypto.defi.defi_protocol": {
        "model": "openbb_terminal.cryptocurrency.defi.llama_model.get_defi_protocol"
    },
    "crypto.defi.defi_protocols": {
        "model": "openbb_terminal.cryptocurrency.defi.llama_model.get_defi_protocols"
    },
    "crypto.defi.defi_tvl": {
        "model": "openbb_terminal.cryptocurrency.defi.llama_model.get_defi_tvl"
    },
    "crypto.defi.ldapps": {
        "view": "openbb_terminal.cryptocurrency.defi.llama_view.display_defi_protocols"
    },
    "crypto.defi.stvl": {
        "view": "openbb_terminal.cryptocurrency.defi.llama_view.display_defi_tvl"
    },
    "crypto.defi.gdapps": {
        "view": "openbb_terminal.cryptocurrency.defi.llama_view.display_grouped_defi_protocols"
    },
    "crypto.defi.dtvl": {
        "view": "openbb_terminal.cryptocurrency.defi.llama_view.display_historical_tvl"
    },
    "crypto.defi.luna_supply_stats": {
        "model": "openbb_terminal.cryptocurrency.defi.smartstake_model.get_luna_supply_stats"
    },
    "crypto.defi.luna_circ_supply_change": {
        "view": "openbb_terminal.cryptocurrency.defi.smartstake_view.display_luna_circ_supply_change"
    },
    "crypto.defi.newsletters": {
        "model": "openbb_terminal.cryptocurrency.defi.substack_model.get_newsletters"
    },
    "crypto.defi.scrape_substack": {
        "model": "openbb_terminal.cryptocurrency.defi.substack_model.scrape_substack"
    },
    "crypto.defi.newsletter": {
        "view": "openbb_terminal.cryptocurrency.defi.substack_view.display_newsletters"
    },
    "crypto.defi.history_asset_from_terra_address": {
        "model": "openbb_terminal.cryptocurrency.defi.terraengineer_model.get_history_asset_from_terra_address"
    },
    "crypto.defi.ayr": {
        "view": "openbb_terminal.cryptocurrency.defi.terraengineer_view.display_anchor_yield_reserve"
    },
    "crypto.defi.aterra": {
        "view": "openbb_terminal.cryptocurrency.defi.terraengineer_view.display_terra_asset_history"
    },
    "crypto.defi._adjust_delegation_info": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model._adjust_delegation_info"
    },
    "crypto.defi._make_request": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model._make_request"
    },
    "crypto.defi.account_growth": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_account_growth"
    },
    "crypto.defi.proposals": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_proposals"
    },
    "crypto.defi.staking_account_info": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_staking_account_info"
    },
    "crypto.defi.staking_ratio_history": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_staking_ratio_history"
    },
    "crypto.defi.staking_returns_history": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_staking_returns_history"
    },
    "crypto.defi.validators": {
        "model": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_model.get_validators",
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_validators",
    },
    "crypto.defi.gacc": {
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_account_growth"
    },
    "crypto.defi.sinfo": {
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_account_staking_info"
    },
    "crypto.defi.gov_proposals": {
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_gov_proposals"
    },
    "crypto.defi.sratio": {
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_staking_ratio_history"
    },
    "crypto.defi.sreturn": {
        "view": "openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.display_staking_returns_history"
    },
    "crypto.disc.cmc_top_n": {
        "model": "openbb_terminal.cryptocurrency.discovery.coinmarketcap_model.get_cmc_top_n"
    },
    "crypto.disc.cmctop": {
        "view": "openbb_terminal.cryptocurrency.discovery.coinmarketcap_view.display_cmc_top_coins"
    },
    "crypto.disc.search_results": {
        "model": "openbb_terminal.cryptocurrency.discovery.coinpaprika_model.get_search_results"
    },
    "crypto.disc.cpsearch": {
        "view": "openbb_terminal.cryptocurrency.discovery.coinpaprika_view.display_search_results"
    },
    "crypto.disc._make_request": {
        "model": "openbb_terminal.cryptocurrency.discovery.dappradar_model._make_request"
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
    "crypto.disc.mapping_matrix_for_exchange": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_mapping_matrix_for_exchange"
    },
    "crypto.disc.trending_coins": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.get_trending_coins"
    },
    "crypto.disc.read_file_data": {
        "model": "openbb_terminal.cryptocurrency.discovery.pycoingecko_model.read_file_data"
    },
    "crypto.disc.cggainers": {
        "view": "openbb_terminal.cryptocurrency.discovery.pycoingecko_view.display_gainers"
    },
    "crypto.disc.cglosers": {
        "view": "openbb_terminal.cryptocurrency.discovery.pycoingecko_view.display_losers"
    },
    "crypto.disc.trending": {
        "view": "openbb_terminal.cryptocurrency.discovery.pycoingecko_view.display_trending"
    },
    "crypto.dd._trading_pairs": {
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
    "crypto.dd.show_available_pairs_for_given_symbol": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.show_available_pairs_for_given_symbol"
    },
    "crypto.dd.balance": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.binance_view.display_balance"
    },
    "crypto.dd.book": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.binance_view.display_order_book"
    },
    "crypto.dd.exchanges": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.ccxt_model.get_exchanges"
    },
    "crypto.dd.candles": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_candles",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinbase_view.display_candles",
    },
    "crypto.dd.order_book": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_order_book"
    },
    "crypto.dd.product_stats": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_product_stats"
    },
    "crypto.dd.trades": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_trades",
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinbase_view.display_trades",
    },
    "crypto.dd.trading_pair_info": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinbase_model.get_trading_pair_info"
    },
    "crypto.dd.cbbook": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinbase_view.display_order_book"
    },
    "crypto.dd.stats": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinbase_view.display_stats"
    },
    "crypto.dd.open_interest_per_exchange": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinglass_model.get_open_interest_per_exchange"
    },
    "crypto.dd.oi": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinglass_view.display_open_interest"
    },
    "crypto.dd.plot_data": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinglass_view.plot_data"
    },
    "crypto.dd.basic_coin_info": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.basic_coin_info"
    },
    "crypto.dd.coin": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin"
    },
    "crypto.dd.coin_events_by_id": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_events_by_id"
    },
    "crypto.dd.coin_exchanges_by_id": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_exchanges_by_id"
    },
    "crypto.dd.coin_markets_by_id": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_markets_by_id"
    },
    "crypto.dd.coin_twitter_timeline": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_twitter_timeline"
    },
    "crypto.dd.ohlc_historical": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_ohlc_historical"
    },
    "crypto.dd.tickers_info_for_coin": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_tickers_info_for_coin"
    },
    "crypto.dd.validate_coin": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_model.validate_coin"
    },
    "crypto.dd.basic": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_basic"
    },
    "crypto.dd.events": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_events"
    },
    "crypto.dd.ex": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_exchanges"
    },
    "crypto.dd.mkt": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_markets"
    },
    "crypto.dd.ps": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_price_supply"
    },
    "crypto.dd.twitter": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.coinpaprika_view.display_twitter"
    },
    "crypto.dd.news": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.cryptopanic_view.display_news"
    },
    "crypto.headlines": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.finbrain_crypto_view.display_crypto_sentiment_analysis"
    },
    "crypto.dd.active_addresses": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_active_addresses"
    },
    "crypto.dd.close_price": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_close_price"
    },
    "crypto.dd.exchange_balances": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_exchange_balances"
    },
    "crypto.dd.exchange_net_position_change": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_exchange_net_position_change"
    },
    "crypto.dd.hashrate": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_hashrate"
    },
    "crypto.dd.non_zero_addresses": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.glassnode_model.get_non_zero_addresses"
    },
    "crypto.dd.active": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_active_addresses"
    },
    "crypto.dd.btcrb": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_btc_rainbow"
    },
    "crypto.dd.eb": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_exchange_balances"
    },
    "crypto.dd.change": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_exchange_net_position_change"
    },
    "crypto.dd.hr": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_hashrate"
    },
    "crypto.dd.nonzero": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.glassnode_view.display_non_zero_addresses"
    },
    "crypto.dd.format_addresses": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.format_addresses"
    },
    "crypto.dd.available_timeseries": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_available_timeseries"
    },
    "crypto.dd.fundraising": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_fundraising"
    },
    "crypto.dd.governance": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_governance"
    },
    "crypto.dd.investors": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_investors"
    },
    "crypto.dd.links": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_links",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_links",
    },
    "crypto.dd.marketcap_dominance": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_marketcap_dominance"
    },
    "crypto.dd.messari_timeseries": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_messari_timeseries"
    },
    "crypto.dd.project_product_info": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_project_product_info"
    },
    "crypto.dd.roadmap": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_roadmap"
    },
    "crypto.dd.team": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_team",
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_team",
    },
    "crypto.dd.tokenomics": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.messari_model.get_tokenomics"
    },
    "crypto.dd.fr": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_fundraising"
    },
    "crypto.dd.gov": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_governance"
    },
    "crypto.dd.inv": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_investors"
    },
    "crypto.dd.mcapdom": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_marketcap_dominance"
    },
    "crypto.dd.mt": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_messari_timeseries"
    },
    "crypto.dd.get_mt": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_messari_timeseries_list"
    },
    "crypto.dd.pi": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_project_info"
    },
    "crypto.dd.rm": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_roadmap"
    },
    "crypto.dd.tk": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.messari_view.display_tokenomics"
    },
    "crypto.dd.check_coin": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.check_coin"
    },
    "crypto.dd.coin_market_chart": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_coin_market_chart"
    },
    "crypto.dd.coin_potential_returns": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_coin_potential_returns",
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_coin_potential_returns",
    },
    "crypto.dd.coin_tokenomics": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_coin_tokenomics"
    },
    "crypto.dd.ohlc": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.get_ohlc"
    },
    "crypto.dd.ath": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_ath"
    },
    "crypto.dd.atl": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_atl"
    },
    "crypto.dd.bc": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_bc"
    },
    "crypto.dd.dev": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_dev"
    },
    "crypto.dd.info": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_info"
    },
    "crypto.dd.market": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_market"
    },
    "crypto.dd.score": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_score"
    },
    "crypto.dd.social": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_social"
    },
    "crypto.dd.web": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_view.display_web"
    },
    "crypto.dd.github_activity": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.santiment_model.get_github_activity"
    },
    "crypto.dd.slug": {
        "model": "openbb_terminal.cryptocurrency.due_diligence.santiment_model.get_slug"
    },
    "crypto.dd.gh": {
        "view": "openbb_terminal.cryptocurrency.due_diligence.santiment_view.display_github_activity"
    },
    "crypto.nft.nft_drops": {
        "model": "openbb_terminal.cryptocurrency.nft.nftcalendar_model.get_nft_drops"
    },
    "crypto.nft.nft_newest_drops": {
        "model": "openbb_terminal.cryptocurrency.nft.nftcalendar_model.get_nft_newest_drops"
    },
    "crypto.nft.nft_ongoing_drops": {
        "model": "openbb_terminal.cryptocurrency.nft.nftcalendar_model.get_nft_ongoing_drops"
    },
    "crypto.nft.nft_today_drops": {
        "model": "openbb_terminal.cryptocurrency.nft.nftcalendar_model.get_nft_today_drops"
    },
    "crypto.nft.nft_upcoming_drops": {
        "model": "openbb_terminal.cryptocurrency.nft.nftcalendar_model.get_nft_upcoming_drops"
    },
    "crypto.nft.newest": {
        "view": "openbb_terminal.cryptocurrency.nft.nftcalendar_view.display_nft_newest_drops"
    },
    "crypto.nft.ongoing": {
        "view": "openbb_terminal.cryptocurrency.nft.nftcalendar_view.display_nft_ongoing_drops"
    },
    "crypto.nft.today": {
        "view": "openbb_terminal.cryptocurrency.nft.nftcalendar_view.display_nft_today_drops"
    },
    "crypto.nft.upcoming": {
        "view": "openbb_terminal.cryptocurrency.nft.nftcalendar_view.display_nft_upcoming_drops"
    },
    "crypto.nft.collection_stats": {
        "model": "openbb_terminal.cryptocurrency.nft.opensea_model.get_collection_stats"
    },
    "crypto.nft.stats": {
        "view": "openbb_terminal.cryptocurrency.nft.opensea_view.display_collection_stats"
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
    "crypto.onchain.erc20_tokens": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_erc20_tokens"
    },
    "crypto.onchain.ethereum_unique_senders": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_ethereum_unique_senders"
    },
    "crypto.onchain.most_traded_pairs": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_most_traded_pairs"
    },
    "crypto.onchain.spread_for_crypto_pair": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_spread_for_crypto_pair"
    },
    "crypto.onchain.token_volume_on_dexes": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.get_token_volume_on_dexes"
    },
    "crypto.onchain.query_graph": {
        "model": "openbb_terminal.cryptocurrency.onchain.bitquery_model.query_graph"
    },
    "crypto.onchain.dvcp": {
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_daily_volume_for_given_pair"
    },
    "crypto.onchain.lt": {
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_dex_trades"
    },
    "crypto.onchain.tv": {
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_dex_volume_for_token"
    },
    "crypto.onchain.ueat": {
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_ethereum_unique_senders"
    },
    "crypto.onchain.ttcp": {
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_most_traded_pairs"
    },
    "crypto.onchain.baas": {
        "view": "openbb_terminal.cryptocurrency.onchain.bitquery_view.display_spread_for_crypto_pair"
    },
    "crypto.onchain._make_request": {
        "model": "openbb_terminal.cryptocurrency.onchain.blockchain_model._make_request"
    },
    "crypto.onchain.btc_circulating_supply": {
        "model": "openbb_terminal.cryptocurrency.onchain.blockchain_model.get_btc_circulating_supply",
        "view": "openbb_terminal.cryptocurrency.onchain.blockchain_view.display_btc_circulating_supply",
    },
    "crypto.onchain.btc_confirmed_transactions": {
        "model": "openbb_terminal.cryptocurrency.onchain.blockchain_model.get_btc_confirmed_transactions",
        "view": "openbb_terminal.cryptocurrency.onchain.blockchain_view.display_btc_confirmed_transactions",
    },
    "crypto.onchain.gwei_fees": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethgasstation_model.get_gwei_fees"
    },
    "crypto.onchain.gwei": {
        "view": "openbb_terminal.cryptocurrency.onchain.ethgasstation_view.display_gwei_fees"
    },
    "crypto.onchain.enrich_social_media": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.enrich_social_media"
    },
    "crypto.onchain.address_history": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_address_history"
    },
    "crypto.onchain.address_info": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_address_info"
    },
    "crypto.onchain.token_decimals": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_decimals"
    },
    "crypto.onchain.token_historical_price": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_historical_price"
    },
    "crypto.onchain.token_history": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_history"
    },
    "crypto.onchain.token_info": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_token_info"
    },
    "crypto.onchain.top_token_holders": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_top_token_holders"
    },
    "crypto.onchain.top_tokens": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_top_tokens"
    },
    "crypto.onchain.tx_info": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.get_tx_info"
    },
    "crypto.onchain.make_request": {
        "model": "openbb_terminal.cryptocurrency.onchain.whale_alert_model.make_request"
    },
    "crypto.onchain.split_cols_with_dot": {
        "model": "openbb_terminal.cryptocurrency.onchain.ethplorer_model.split_cols_with_dot"
    },
    "crypto.onchain.hist": {
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_address_history"
    },
    "crypto.onchain.balance": {
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_address_info"
    },
    "crypto.onchain.prices": {
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_token_historical_prices"
    },
    "crypto.onchain.th": {
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_token_history"
    },
    "crypto.onchain.info": {
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_token_info"
    },
    "crypto.onchain.holders": {
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_top_token_holders"
    },
    "crypto.onchain.top": {
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_top_tokens"
    },
    "crypto.onchain.tx": {
        "view": "openbb_terminal.cryptocurrency.onchain.ethplorer_view.display_tx_info"
    },
    "crypto.onchain.whales_transactions": {
        "model": "openbb_terminal.cryptocurrency.onchain.whale_alert_model.get_whales_transactions"
    },
    "crypto.onchain.whales": {
        "view": "openbb_terminal.cryptocurrency.onchain.whale_alert_view.display_whales_transactions"
    },
    "crypto.ov.altcoin_index": {
        "model": "openbb_terminal.cryptocurrency.overview.blockchaincenter_model.get_altcoin_index"
    },
    "crypto.ov.altindex": {
        "view": "openbb_terminal.cryptocurrency.overview.blockchaincenter_view.display_altcoin_index"
    },
    "crypto.ov.trading_pairs": {
        "model": "openbb_terminal.cryptocurrency.overview.coinbase_model.get_trading_pairs"
    },
    "crypto.ov.cbpairs": {
        "view": "openbb_terminal.cryptocurrency.overview.coinbase_view.display_trading_pairs"
    },
    "crypto.ov._get_coins_info_helper": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model._get_coins_info_helper"
    },
    "crypto.ov.all_contract_platforms": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_all_contract_platforms"
    },
    "crypto.ov.coins_info": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_coins_info"
    },
    "crypto.ov.coins_market_info": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_coins_market_info"
    },
    "crypto.ov.contract_platform": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_contract_platform"
    },
    "crypto.ov.exchanges_market": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_exchanges_market"
    },
    "crypto.ov.global_market": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_global_market"
    },
    "crypto.ov.list_of_coins": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_list_of_coins"
    },
    "crypto.ov.list_of_exchanges": {
        "model": "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_list_of_exchanges"
    },
    "crypto.ov.cpinfo": {
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_all_coins_info"
    },
    "crypto.ov.cpmarkets": {
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_all_coins_market_info"
    },
    "crypto.ov.cpexchanges": {
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_all_exchanges"
    },
    "crypto.ov.cpplatforms": {
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_all_platforms"
    },
    "crypto.ov.cpcontracts": {
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_contracts"
    },
    "crypto.ov.cpexmarkets": {
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_exchange_markets"
    },
    "crypto.ov.cpglobal": {
        "view": "openbb_terminal.cryptocurrency.overview.coinpaprika_view.display_global_market"
    },
    "crypto.ov._parse_post": {
        "model": "openbb_terminal.cryptocurrency.overview.cryptopanic_model._parse_post"
    },
    "crypto.ov.news": {
        "model": "openbb_terminal.cryptocurrency.overview.cryptopanic_model.get_news",
        "view": "openbb_terminal.cryptocurrency.overview.cryptopanic_view.display_news",
    },
    "crypto.ov.make_request": {
        "model": "openbb_terminal.cryptocurrency.overview.cryptopanic_model.make_request"
    },
    "crypto.ov.check_valid_coin": {
        "model": "openbb_terminal.cryptocurrency.overview.loanscan_model.check_valid_coin"
    },
    "crypto.ov.check_valid_platform": {
        "model": "openbb_terminal.cryptocurrency.overview.loanscan_model.check_valid_platform"
    },
    "crypto.ov.rates": {
        "model": "openbb_terminal.cryptocurrency.overview.loanscan_model.get_rates"
    },
    "crypto.ov.cr": {
        "view": "openbb_terminal.cryptocurrency.overview.loanscan_view.display_crypto_rates"
    },
    "crypto.ov.derivatives": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_derivatives"
    },
    "crypto.ov.exchange_rates": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_exchange_rates"
    },
    "crypto.ov.exchanges": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_exchanges",
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_exchanges",
    },
    "crypto.ov.finance_products": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_finance_products"
    },
    "crypto.ov.financial_platforms": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_financial_platforms"
    },
    "crypto.ov.global_defi_info": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_global_defi_info"
    },
    "crypto.ov.global_info": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_global_info"
    },
    "crypto.ov.global_markets_info": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_global_markets_info"
    },
    "crypto.ov.holdings_overview": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_holdings_overview"
    },
    "crypto.ov.indexes": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_indexes"
    },
    "crypto.ov.stable_coins": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_stable_coins"
    },
    "crypto.ov.top_crypto_categories": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.get_top_crypto_categories"
    },
    "crypto.ov.lambda_coin_formatter": {
        "model": "openbb_terminal.cryptocurrency.overview.pycoingecko_model.lambda_coin_formatter"
    },
    "crypto.ov.cgcategories": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_categories"
    },
    "crypto.ov.crypto_heatmap": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_crypto_heatmap"
    },
    "crypto.ov.cgderivatives": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_derivatives"
    },
    "crypto.ov.cgexrates": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_exchange_rates"
    },
    "crypto.ov.cgdefi": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_global_defi_info"
    },
    "crypto.ov.cgglobal": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_global_market_info"
    },
    "crypto.ov.cghold": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_holdings_overview"
    },
    "crypto.ov.cgindexes": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_indexes"
    },
    "crypto.ov.platforms": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_platforms"
    },
    "crypto.ov.cgproducts": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_products"
    },
    "crypto.ov.cgstables": {
        "view": "openbb_terminal.cryptocurrency.overview.pycoingecko_view.display_stablecoins"
    },
    "crypto.ov._make_request": {
        "model": "openbb_terminal.cryptocurrency.overview.rekt_model._make_request"
    },
    "crypto.ov._retry_session": {
        "model": "openbb_terminal.cryptocurrency.overview.rekt_model._retry_session"
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
    "crypto.ov.crypto_withdrawal_fees": {
        "model": "openbb_terminal.cryptocurrency.overview.withdrawalfees_model.get_crypto_withdrawal_fees"
    },
    "crypto.ov.overall_exchange_withdrawal_fees": {
        "model": "openbb_terminal.cryptocurrency.overview.withdrawalfees_model.get_overall_exchange_withdrawal_fees"
    },
    "crypto.ov.overall_withdrawal_fees": {
        "model": "openbb_terminal.cryptocurrency.overview.withdrawalfees_model.get_overall_withdrawal_fees"
    },
    "crypto.ov.wfpe": {
        "view": "openbb_terminal.cryptocurrency.overview.withdrawalfees_view.display_crypto_withdrawal_fees"
    },
    "crypto.ov.ewf": {
        "view": "openbb_terminal.cryptocurrency.overview.withdrawalfees_view.display_overall_exchange_withdrawal_fees"
    },
    "crypto.ov.wf": {
        "view": "openbb_terminal.cryptocurrency.overview.withdrawalfees_view.display_overall_withdrawal_fees"
    },
    "crypto.tools.calculate_apy": {
        "model": "openbb_terminal.cryptocurrency.tools.tools_model.calculate_apy"
    },
    "crypto.tools.calculate_il": {
        "model": "openbb_terminal.cryptocurrency.tools.tools_model.calculate_il"
    },
    "crypto.tools.apy": {
        "view": "openbb_terminal.cryptocurrency.tools.tools_view.display_apy"
    },
    "crypto.tools.il": {
        "view": "openbb_terminal.cryptocurrency.tools.tools_view.display_il"
    },
    "econometrics.clean": {
        "model": "openbb_terminal.econometrics.econometrics_model.clean"
    },
    "econometrics.load": {
        "model": "openbb_terminal.econometrics.econometrics_model.load"
    },
    "econometrics.coint": {
        "view": "openbb_terminal.econometrics.econometrics_view.display_cointegration_test"
    },
    "econometrics.granger": {
        "view": "openbb_terminal.econometrics.econometrics_view.display_granger"
    },
    "econometrics.norm": {
        "view": "openbb_terminal.econometrics.econometrics_view.display_norm"
    },
    "econometrics.plot": {
        "view": "openbb_terminal.econometrics.econometrics_view.display_plot"
    },
    "econometrics.root": {
        "view": "openbb_terminal.econometrics.econometrics_view.display_root"
    },
    "econometrics.options": {
        "view": "openbb_terminal.econometrics.econometrics_view.show_options"
    },
    "econometrics.compare": {
        "model": "openbb_terminal.econometrics.regression_model.get_comparison"
    },
    "econometrics.ols": {
        "model": "openbb_terminal.econometrics.regression_model.get_ols"
    },
    "econometrics.bgod": {
        "view": "openbb_terminal.econometrics.regression_view.display_bgod"
    },
    "econometrics.bpag": {
        "view": "openbb_terminal.econometrics.regression_view.display_bpag"
    },
    "econometrics.dwat": {
        "view": "openbb_terminal.econometrics.regression_view.display_dwat"
    },
    "econometrics.panel": {
        "view": "openbb_terminal.econometrics.regression_view.display_panel"
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
    "economy.get_macro_parameters": {
        "model": "openbb_terminal.economy.econdb_model.get_macro_parameters"
    },
    "economy.get_macro_countries": {
        "model": "openbb_terminal.economy.econdb_model.get_macro_countries"
    },
    "economy.treasury": {
        "model": "openbb_terminal.economy.econdb_model.get_treasuries",
        "view": "openbb_terminal.economy.econdb_view.show_treasuries",
    },
    "economy.maturities": {
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
    "economy.events": {
        "model": "openbb_terminal.economy.investingcom_model.get_economic_calendar"
    },
    "economy.ycrv": {
        "model": "openbb_terminal.economy.investingcom_model.get_yieldcurve",
        "view": "openbb_terminal.economy.investingcom_view.display_yieldcurve",
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
    "economy.search_index": {
        "model": "openbb_terminal.economy.yfinance_model.get_search_indices"
    },
    "etf.disc.etf_movers": {
        "model": "openbb_terminal.etf.discovery.wsj_model.etf_movers"
    },
    "etf.disc.mover": {"view": "openbb_terminal.etf.discovery.wsj_view.show_top_mover"},
    "etf.etf_by_category": {
        "view": "openbb_terminal.etf.financedatabase_view.display_etf_by_category"
    },
    "etf.ld": {
        "view": "openbb_terminal.etf.financedatabase_view.display_etf_by_description"
    },
    "etf.ln": {"view": "openbb_terminal.etf.financedatabase_view.display_etf_by_name"},
    "etf.scr.screen": {
        "model": "openbb_terminal.etf.screener.screener_model.etf_screener",
        "view": "openbb_terminal.etf.screener.screener_view.view_screener",
    },
    "etf.etf_by_name": {
        "view": "openbb_terminal.etf.stockanalysis_view.display_etf_by_name"
    },
    "etf.holdings": {"view": "openbb_terminal.etf.stockanalysis_view.view_holdings"},
    "etf.overview": {"view": "openbb_terminal.etf.stockanalysis_view.view_overview"},
    "etf.summary": {
        "view": "openbb_terminal.etf.yfinance_view.display_etf_description"
    },
    "etf.weights": {"view": "openbb_terminal.etf.yfinance_view.display_etf_weightings"},
    "forex.quote": {"view": "openbb_terminal.forex.av_view.display_quote"},
    "forex.oanda.fwd": {
        "view": "openbb_terminal.forex.fxempire_view.display_forward_rates"
    },
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
    "forex.oanda.add_plots": {
        "view": "openbb_terminal.forex.oanda.oanda_view.add_plots"
    },
    "forex.oanda.book_plot": {
        "view": "openbb_terminal.forex.oanda.oanda_view.book_plot"
    },
    "forex.oanda.calendar": {"view": "openbb_terminal.forex.oanda.oanda_view.calendar"},
    "forex.oanda.cancel": {
        "view": "openbb_terminal.forex.oanda.oanda_view.cancel_pending_order"
    },
    "forex.oanda.closetrade": {
        "view": "openbb_terminal.forex.oanda.oanda_view.close_trade"
    },
    "forex.oanda.order": {
        "view": "openbb_terminal.forex.oanda.oanda_view.create_order"
    },
    "forex.oanda.summary": {
        "view": "openbb_terminal.forex.oanda.oanda_view.get_account_summary"
    },
    "forex.oanda.price": {
        "view": "openbb_terminal.forex.oanda.oanda_view.get_fx_price"
    },
    "forex.oanda.positions": {
        "view": "openbb_terminal.forex.oanda.oanda_view.get_open_positions"
    },
    "forex.oanda.trades": {
        "view": "openbb_terminal.forex.oanda.oanda_view.get_open_trades"
    },
    "forex.oanda.orderbook": {
        "view": "openbb_terminal.forex.oanda.oanda_view.get_order_book"
    },
    "forex.oanda.pending": {
        "view": "openbb_terminal.forex.oanda.oanda_view.get_pending_orders"
    },
    "forex.oanda.positionbook": {
        "view": "openbb_terminal.forex.oanda.oanda_view.get_position_book"
    },
    "forex.oanda.listorder": {
        "view": "openbb_terminal.forex.oanda.oanda_view.list_orders"
    },
    "forex.oanda.candles": {
        "view": "openbb_terminal.forex.oanda.oanda_view.show_candles"
    },
    "funds.info": {
        "view": "openbb_terminal.mutual_funds.investpy_view.display_fund_info"
    },
    "funds.plot": {
        "view": "openbb_terminal.mutual_funds.investpy_view.display_historical"
    },
    "funds.overview": {
        "view": "openbb_terminal.mutual_funds.investpy_view.display_overview"
    },
    "funds.search": {
        "view": "openbb_terminal.mutual_funds.investpy_view.display_search"
    },
    "funds.equity": {
        "view": "openbb_terminal.mutual_funds.yfinance_view.display_equity"
    },
    "funds.sector": {
        "view": "openbb_terminal.mutual_funds.yfinance_view.display_sector"
    },
    "portfolio.bro.ally.ally_positions_to_df": {
        "model": "openbb_terminal.portfolio.brokers.ally.ally_model.ally_positions_to_df"
    },
    "portfolio.bro.ally.stock_quote": {
        "model": "openbb_terminal.portfolio.brokers.ally.ally_model.get_stock_quote"
    },
    "portfolio.bro.ally.top_movers": {
        "model": "openbb_terminal.portfolio.brokers.ally.ally_model.get_top_movers"
    },
    "portfolio.bro.ally.balances": {
        "view": "openbb_terminal.portfolio.brokers.ally.ally_view.display_balances"
    },
    "portfolio.bro.ally.history": {
        "view": "openbb_terminal.portfolio.brokers.ally.ally_view.display_history"
    },
    "portfolio.bro.ally.holdings": {
        "view": "openbb_terminal.portfolio.brokers.ally.ally_view.display_holdings"
    },
    "portfolio.bro.ally.quote": {
        "view": "openbb_terminal.portfolio.brokers.ally.ally_view.display_stock_quote"
    },
    "portfolio.bro.ally.movers": {
        "view": "openbb_terminal.portfolio.brokers.ally.ally_view.display_top_lists"
    },
    "portfolio.bro.coinbase.account_history": {
        "model": "openbb_terminal.portfolio.brokers.coinbase.coinbase_model.get_account_history"
    },
    "portfolio.bro.coinbase.accounts": {
        "model": "openbb_terminal.portfolio.brokers.coinbase.coinbase_model.get_accounts"
    },
    "portfolio.bro.coinbase.deposits": {
        "model": "openbb_terminal.portfolio.brokers.coinbase.coinbase_model.get_deposits"
    },
    "portfolio.bro.cb.account": {
        "view": "openbb_terminal.portfolio.brokers.coinbase.coinbase_view.display_account"
    },
    "portfolio.bro.cb.deposits": {
        "view": "openbb_terminal.portfolio.brokers.coinbase.coinbase_view.display_deposits"
    },
    "portfolio.bro.cb.history": {
        "view": "openbb_terminal.portfolio.brokers.coinbase.coinbase_view.display_history"
    },
    "portfolio.bro.cb.orders": {
        "view": "openbb_terminal.portfolio.brokers.coinbase.coinbase_view.display_orders"
    },
    "portfolio.bro.robinhood.historical": {
        "model": "openbb_terminal.portfolio.brokers.robinhood.robinhood_model.get_historical"
    },
    "portfolio.bro.robinhood.rh_positions_to_df": {
        "model": "openbb_terminal.portfolio.brokers.robinhood.robinhood_model.rh_positions_to_df"
    },
    "portfolio.bro.rh.historical": {
        "view": "openbb_terminal.portfolio.brokers.robinhood.robinhood_view.display_historical"
    },
    "portfolio.bro.rh.holdings": {
        "view": "openbb_terminal.portfolio.brokers.robinhood.robinhood_view.display_holdings"
    },
    "portfolio.pa.load_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_analysis.portfolio_model.load_portfolio"
    },
    "portfolio.pa.group": {
        "view": "openbb_terminal.portfolio.portfolio_analysis.portfolio_view.display_group_holdings"
    },
    "portfolio.pa.country": {
        "model": "openbb_terminal.portfolio.portfolio_analysis.yfinance_model.get_country"
    },
    "portfolio.po.excel_bl_views": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.excel_model.excel_bl_views"
    },
    "portfolio.po.load_allocation": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.excel_model.load_allocation"
    },
    "portfolio.po.load_bl_views": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.excel_model.load_bl_views"
    },
    "portfolio.po.load_configuration": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.excel_model.load_configuration"
    },
    "portfolio.po.black_litterman": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.black_litterman",
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_black_litterman",
    },
    "portfolio.po.generate_random_portfolios": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.generate_random_portfolios"
    },
    "portfolio.po.black_litterman_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_black_litterman_portfolio"
    },
    "portfolio.po.equal_weights": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_equal_weights"
    },
    "portfolio.po.hcp_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_hcp_portfolio"
    },
    "portfolio.po.max_decorrelation_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_max_decorrelation_portfolio"
    },
    "portfolio.po.max_diversification_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_max_diversification_portfolio"
    },
    "portfolio.po.mean_risk_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_mean_risk_portfolio"
    },
    "portfolio.po.property_weights": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_property_weights"
    },
    "portfolio.po.rel_risk_parity_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_rel_risk_parity_portfolio"
    },
    "portfolio.po.risk_parity_portfolio": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.optimizer_model.get_risk_parity_portfolio"
    },
    "portfolio.po.additional_plots": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.additional_plots"
    },
    "portfolio.po.d_period": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.d_period"
    },
    "portfolio.po.categories": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_categories"
    },
    "portfolio.po.categories_sa": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_categories_sa"
    },
    "portfolio.po.ef": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_ef"
    },
    "portfolio.po.equal": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_equal_weight"
    },
    "portfolio.po.hcp": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_hcp"
    },
    "portfolio.po.herc": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_herc"
    },
    "portfolio.po.hrp": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_hrp"
    },
    "portfolio.po.max_decorr": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_max_decorr"
    },
    "portfolio.po.max_div": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_max_div"
    },
    "portfolio.po.max_ret": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_max_ret"
    },
    "portfolio.po.max_sharpe": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_max_sharpe"
    },
    "portfolio.po.max_util": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_max_util"
    },
    "portfolio.po.mean_risk": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_mean_risk"
    },
    "portfolio.po.min_risk": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_min_risk"
    },
    "portfolio.po.nco": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_nco"
    },
    "portfolio.po.weighting": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_property_weighting"
    },
    "portfolio.po.rel_risk_parity": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_rel_risk_parity"
    },
    "portfolio.po.risk_parity": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_risk_parity"
    },
    "portfolio.po.weights": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_weights"
    },
    "portfolio.po.weights_sa": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.display_weights_sa"
    },
    "portfolio.po.my_autopct": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.my_autopct"
    },
    "portfolio.po.pie_chart_weights": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.pie_chart_weights"
    },
    "portfolio.po.portfolio_performance": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.optimizer_view.portfolio_performance"
    },
    "portfolio.po.parameters.load_file": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.parameters.params_view.load_file"
    },
    "portfolio.po.parameters.show_arguments": {
        "view": "openbb_terminal.portfolio.portfolio_optimization.parameters.params_view.show_arguments"
    },
    "portfolio.po.process_returns": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.yahoo_finance_model.process_returns"
    },
    "portfolio.po.process_stocks": {
        "model": "openbb_terminal.portfolio.portfolio_optimization.yahoo_finance_model.process_stocks"
    },
    "stocks.bt.ema_cross": {
        "model": "openbb_terminal.stocks.backtesting.bt_model.ema_cross_strategy",
        "view": "openbb_terminal.stocks.backtesting.bt_view.display_ema_cross",
    },
    "stocks.bt.ema": {
        "model": "openbb_terminal.stocks.backtesting.bt_model.ema_strategy",
        "view": "openbb_terminal.stocks.backtesting.bt_view.display_simple_ema",
    },
    "stocks.bt.rsi": {
        "model": "openbb_terminal.stocks.backtesting.bt_model.rsi_strategy",
        "view": "openbb_terminal.stocks.backtesting.bt_view.display_rsi_strategy",
    },
    "stocks.bt.whatif": {
        "view": "openbb_terminal.stocks.backtesting.bt_view.display_whatif_scenario"
    },
    "stocks.ba.cramer": {
        "model": "openbb_terminal.stocks.behavioural_analysis.cramer_model.get_cramer_daily"
    },
    "stocks.ba.cramer_ticker": {
        "model": "openbb_terminal.stocks.behavioural_analysis.cramer_model.get_cramer_ticker",
        "view": "openbb_terminal.stocks.behavioural_analysis.cramer_view.display_cramer_ticker",
    },
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
        "model": "openbb_terminal.stocks.comparison_analysis.marketwatch_model.get_income_comparison"
    },
    "stocks.ca.polygon_peers": {
        "model": "openbb_terminal.stocks.comparison_analysis.polygon_model.get_similar_companies"
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
    "stocks.disc.ford": {
        "model": "openbb_terminal.stocks.discovery.fidelity_model.get_orders"
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
    "stocks.options.calc": {
        "model": "openbb_terminal.stocks.options.calculator_model.pnl_calculator",
        "view": "openbb_terminal.stocks.options.calculator_view.view_calculator",
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
        "model": "openbb_terminal.stocks.options.screen.syncretism_model.get_screener_output"
    },
    "stocks.options.screen.view_available_presets": {
        "view": "openbb_terminal.stocks.options.screen.syncretism_view.view_available_presets"
    },
    "stocks.options.screen.view_screener_output": {
        "view": "openbb_terminal.stocks.options.screen.syncretism_view.view_screener_output"
    },
    "stocks.options.historical_options": {
        "model": "openbb_terminal.stocks.options.tradier_model.get_historical_options"
    },
    "stocks.options.chains": {
        "model": "openbb_terminal.stocks.options.tradier_model.get_option_chains",
        "view": "openbb_terminal.stocks.options.tradier_view.display_chains",
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
    "stocks.options.check_valid_option_chains_headers": {
        "view": "openbb_terminal.stocks.options.tradier_view.check_valid_option_chains_headers"
    },
    "stocks.options.expiry_dates": {
        "view": "openbb_terminal.stocks.options.tradier_view.display_expiry_dates"
    },
    "stocks.options.hist_tr": {
        "view": "openbb_terminal.stocks.options.tradier_view.display_historical"
    },
    "stocks.options.green": {
        "view": "openbb_terminal.stocks.options.tradier_view.lambda_green_highlight"
    },
    "stocks.options.red": {
        "view": "openbb_terminal.stocks.options.tradier_view.lambda_red_highlight"
    },
    "stocks.options.oi_tr": {
        "view": "openbb_terminal.stocks.options.tradier_view.plot_oi"
    },
    "stocks.options.vol_tr": {
        "view": "openbb_terminal.stocks.options.tradier_view.plot_vol"
    },
    "stocks.options.voi_tr": {
        "view": "openbb_terminal.stocks.options.tradier_view.plot_volume_open_interest"
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
    "stocks.options.oi_yf": {
        "view": "openbb_terminal.stocks.options.yfinance_view.plot_oi"
    },
    "stocks.options.plot": {
        "view": "openbb_terminal.stocks.options.yfinance_view.plot_plot"
    },
    "stocks.options.vol_yf": {
        "view": "openbb_terminal.stocks.options.yfinance_view.plot_vol"
    },
    "stocks.options.voi_yf": {
        "view": "openbb_terminal.stocks.options.yfinance_view.plot_volume_open_interest"
    },
    "stocks.options.binom": {
        "view": "openbb_terminal.stocks.options.yfinance_view.show_binom"
    },
    "stocks.options.greeks": {
        "view": "openbb_terminal.stocks.options.yfinance_view.show_greeks"
    },
    "stocks.options.parity": {
        "view": "openbb_terminal.stocks.options.yfinance_view.show_parity"
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
    "stocks.qa.capm": {
        "view": "openbb_terminal.stocks.quantitative_analysis.factors_view.capm_view"
    },
    "stocks.screener.screener_data": {
        "model": "openbb_terminal.stocks.screener.finviz_model.get_screener_data"
    },
    "stocks.screener.finviz_screener": {
        "view": "openbb_terminal.stocks.screener.finviz_view.screener"
    },
    "stocks.screener.historical": {
        "view": "openbb_terminal.stocks.screener.yahoofinance_view.historical"
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
    "stocks.sia.metric": {
        "view": "openbb_terminal.stocks.sector_industry_analysis.financedatabase_view.display_bars_financials"
    },
    "stocks.sia.financials": {
        "view": "openbb_terminal.stocks.sector_industry_analysis.stockanalysis_view.display_plots_financials"
    },
    "stocks.ta.summary": {
        "model": "openbb_terminal.stocks.technical_analysis.finbrain_model.get_technical_summary_report",
        "view": "openbb_terminal.stocks.technical_analysis.finbrain_view.technical_summary_report",
    },
    "stocks.ta.pattern": {
        "model": "openbb_terminal.stocks.technical_analysis.finnhub_model.get_pattern_recognition",
        "view": "openbb_terminal.stocks.technical_analysis.finnhub_view.plot_pattern_recognition",
    },
    "stocks.ta.finviz_image": {
        "model": "openbb_terminal.stocks.technical_analysis.finviz_model.get_finviz_image"
    },
    "stocks.ta.view": {
        "view": "openbb_terminal.stocks.technical_analysis.finviz_view.view"
    },
    "stocks.ta.recom": {
        "model": "openbb_terminal.stocks.technical_analysis.tradingview_model.get_tradingview_recommendation",
        "view": "openbb_terminal.stocks.technical_analysis.tradingview_view.print_recommendation",
    },
    "stocks.tradinghours.check_if_open": {
        "model": "openbb_terminal.stocks.tradinghours.bursa_model.check_if_open"
    },
    "stocks.tradinghours.bursa": {
        "model": "openbb_terminal.stocks.tradinghours.bursa_model.get_bursa"
    },
    "stocks.th.all": {
        "view": "openbb_terminal.stocks.tradinghours.bursa_view.display_all"
    },
    "stocks.th.closed": {
        "view": "openbb_terminal.stocks.tradinghours.bursa_view.display_closed"
    },
    "stocks.th.exchange": {
        "view": "openbb_terminal.stocks.tradinghours.bursa_view.display_exchange"
    },
    "stocks.th.open": {
        "view": "openbb_terminal.stocks.tradinghours.bursa_view.display_open"
    },
}
