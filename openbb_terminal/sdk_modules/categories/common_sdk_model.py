"""OpenBB Terminal SDK Common module."""
import logging

import openbb_terminal.sdk_init as lib
from openbb_terminal.sdk_modules.sdk_helpers import Category

logger = logging.getLogger(__name__)


class CommonQuantitativeAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.bw = lib.common_qa_view.display_bw
        self.calculate_adjusted_var = lib.common_qa_model.calculate_adjusted_var
        self.es = lib.common_qa_model.get_es
        self.es_view = lib.common_qa_view.display_es
        self.normality = lib.common_qa_model.get_normality
        self.normality_view = lib.common_qa_view.display_normality
        self.omega = lib.common_qa_model.get_omega
        self.omega_view = lib.common_qa_view.display_omega
        self.decompose = lib.common_qa_model.get_seasonal_decomposition
        self.sharpe = lib.common_qa_model.get_sharpe
        self.sharpe_view = lib.common_qa_view.display_sharpe
        self.sortino = lib.common_qa_model.get_sortino
        self.sortino_view = lib.common_qa_view.display_sortino
        self.summary = lib.common_qa_model.get_summary
        self.summary_view = lib.common_qa_view.display_summary
        self.unitroot = lib.common_qa_model.get_unitroot
        self.unitroot_view = lib.common_qa_view.display_unitroot
        self.var = lib.common_qa_model.get_var
        self.var_view = lib.common_qa_view.display_var
        self.kurtosis = lib.common_qa_rolling_model.get_kurtosis
        self.kurtosis_view = lib.common_qa_rolling_view.display_kurtosis
        self.quantile = lib.common_qa_rolling_model.get_quantile
        self.quantile_view = lib.common_qa_rolling_view.display_quantile
        self.rolling = lib.common_qa_rolling_model.get_rolling_avg
        self.rolling_view = lib.common_qa_rolling_view.display_mean_std
        self.skew = lib.common_qa_rolling_model.get_skew
        self.skew_view = lib.common_qa_rolling_view.display_skew
        self.spread = lib.common_qa_rolling_model.get_spread
        self.spread_view = lib.common_qa_rolling_view.display_spread


class CommonTechnicalAnalysis(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.ad = lib.common_ta_volume_model.ad
        self.ad_view = lib.common_ta_volume_view.display_ad
        self.adosc = lib.common_ta_volume_model.adosc
        self.adosc_view = lib.common_ta_volume_view.display_adosc
        self.aroon = lib.common_ta_trend_indicators_model.aroon
        self.aroon_view = lib.common_ta_trend_indicators_view.display_aroon
        self.adx = lib.common_ta_trend_indicators_model.adx
        self.adx_view = lib.common_ta_trend_indicators_view.display_adx
        self.atr = lib.common_ta_volatility_model.atr
        self.atr_view = lib.common_ta_volatility_view.display_atr
        self.bbands = lib.common_ta_volatility_model.bbands
        self.bbands_view = lib.common_ta_volatility_view.display_bbands
        self.donchian = lib.common_ta_volatility_model.donchian
        self.donchian_view = lib.common_ta_volatility_view.display_donchian
        self.ema = lib.common_ta_overlap_model.ema
        self.fib = lib.common_ta_custom_indicators_model.calculate_fib_levels
        self.fib_view = lib.common_ta_custom_indicators_view.fibonacci_retracement
        self.fisher = lib.common_ta_momentum_model.fisher
        self.hma = lib.common_ta_overlap_model.hma
        self.kc = lib.common_ta_volatility_model.kc
        self.kc_view = lib.common_ta_volatility_view.view_kc
        self.ma = lib.common_ta_overlap_view.view_ma
        self.macd = lib.common_ta_momentum_model.macd
        self.macd_view = lib.common_ta_momentum_view.display_macd
        self.obv = lib.common_ta_volume_model.obv
        self.obv_view = lib.common_ta_volume_view.display_obv
        self.rsi = lib.common_ta_momentum_model.rsi
        self.rsi_view = lib.common_ta_momentum_view.display_rsi
        self.sma = lib.common_ta_overlap_model.sma
        self.stoch = lib.common_ta_momentum_model.stoch
        self.stoch_view = lib.common_ta_momentum_view.display_stoch
        self.vwap = lib.common_ta_overlap_model.vwap
        self.vwap_view = lib.common_ta_overlap_view.view_vwap
        self.wma = lib.common_ta_overlap_model.wma
        self.zlma = lib.common_ta_overlap_model.zlma


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
