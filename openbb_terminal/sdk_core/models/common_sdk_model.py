# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class CommonRoot(Category):
    """OpenBB SDK Common Module

    Attributes:
        `news`: Get news for a given term and source. [Source: Feedparser]\n
        `news_view`: Plots news for a given term and source. [Source: Feedparser]\n
    """

    def __init__(self):
        super().__init__()
        self.news = lib.common_feedparser_model.get_news
        self.news_view = lib.common_feedparser_view.display_news


class CommonQuantitativeAnalysis(Category):
    """OpenBB SDK Quantitative Analysis Module.

    Attributes:
        `bw`: Plots box and whisker plots\n
        `calculate_adjusted_var`: Calculates VaR, which is adjusted for skew and kurtosis (Cornish-Fischer-Expansion)\n
        `decompose`: Perform seasonal decomposition\n
        `es`: Gets Expected Shortfall for specified stock dataframe.\n
        `es_view`: Prints table showing expected shortfall.\n
        `kurtosis`: Kurtosis Indicator\n
        `kurtosis_view`: Plots rolling kurtosis\n
        `normality`: Look at the distribution of returns and generate statistics on the relation to the normal curve.\n
        `normality_view`: Prints table showing normality statistics\n
        `omega`: Get the omega series\n
        `omega_view`: Plots the omega ratio\n
        `quantile`: Overlay Median & Quantile\n
        `quantile_view`: Plots rolling quantile\n
        `rolling`: Return rolling mean and standard deviation\n
        `rolling_view`: Plots mean std deviation\n
        `sharpe`: Calculates the sharpe ratio\n
        `sharpe_view`: Plots Calculated the sharpe ratio\n
        `skew`: Skewness Indicator\n
        `skew_view`: Plots rolling skew\n
        `sortino`: Calculates the sortino ratio\n
        `sortino_view`: Plots the sortino ratio\n
        `spread`: Standard Deviation and Variance\n
        `spread_view`: Plots rolling spread\n
        `summary`: Print summary statistics\n
        `summary_view`: Prints table showing summary statistics\n
        `unitroot`: Calculate test statistics for unit roots\n
        `unitroot_view`: Prints table showing unit root test calculations\n
        `var`: Gets value at risk for specified stock dataframe.\n
        `var_view`: Prints table showing VaR of dataframe.\n
    """

    def __init__(self):
        super().__init__()
        self.bw = lib.common_qa_view.display_bw
        self.calculate_adjusted_var = lib.common_qa_model.calculate_adjusted_var
        self.decompose = lib.common_qa_model.get_seasonal_decomposition
        self.es = lib.common_qa_model.get_es
        self.es_view = lib.common_qa_view.display_es
        self.kurtosis = lib.common_qa_rolling_model.get_kurtosis
        self.kurtosis_view = lib.common_qa_rolling_view.display_kurtosis
        self.normality = lib.common_qa_model.get_normality
        self.normality_view = lib.common_qa_view.display_normality
        self.omega = lib.common_qa_model.get_omega
        self.omega_view = lib.common_qa_view.display_omega
        self.quantile = lib.common_qa_rolling_model.get_quantile
        self.quantile_view = lib.common_qa_rolling_view.display_quantile
        self.rolling = lib.common_qa_rolling_model.get_rolling_avg
        self.rolling_view = lib.common_qa_rolling_view.display_mean_std
        self.sharpe = lib.common_qa_model.get_sharpe
        self.sharpe_view = lib.common_qa_view.display_sharpe
        self.skew = lib.common_qa_rolling_model.get_skew
        self.skew_view = lib.common_qa_rolling_view.display_skew
        self.sortino = lib.common_qa_model.get_sortino
        self.sortino_view = lib.common_qa_view.display_sortino
        self.spread = lib.common_qa_rolling_model.get_spread
        self.spread_view = lib.common_qa_rolling_view.display_spread
        self.summary = lib.common_qa_model.get_summary
        self.summary_view = lib.common_qa_view.display_summary
        self.unitroot = lib.common_qa_model.get_unitroot
        self.unitroot_view = lib.common_qa_view.display_unitroot
        self.var = lib.common_qa_model.get_var
        self.var_view = lib.common_qa_view.display_var


class CommonTechnicalAnalysis(Category):
    """OpenBB SDK Technical Analysis Module.

    Attributes:
        `ad`: Calculate AD technical indicator\n
        `ad_view`: Plots AD technical indicator\n
        `adosc`: Calculate AD oscillator technical indicator\n
        `adosc_view`: Plots AD Osc Indicator\n
        `adx`: ADX technical indicator\n
        `adx_view`: Plots ADX indicator\n
        `aroon`: Aroon technical indicator\n
        `aroon_view`: Plots Aroon indicator\n
        `atr`: Average True Range\n
        `atr_view`: Plots ATR\n
        `bbands`: Calculate Bollinger Bands\n
        `bbands_view`: Plots bollinger bands\n
        `donchian`: Calculate Donchian Channels\n
        `donchian_view`: Plots donchian channels\n
        `ema`: Gets exponential moving average (EMA) for stock\n
        `fib`: Calculate Fibonacci levels\n
        `fib_view`: Plots Calculated fibonacci retracement levels\n
        `fisher`: Fisher Transform\n
        `hma`: Gets hull moving average (HMA) for stock\n
        `kc`: Keltner Channels\n
        `kc_view`: Plots Keltner Channels Indicator\n
        `ma`: Plots MA technical indicator\n
        `macd`: Moving average convergence divergence\n
        `macd_view`: Plots MACD signal\n
        `obv`: On Balance Volume\n
        `obv_view`: Plots OBV technical indicator\n
        `rsi`: Relative strength index\n
        `rsi_view`: Plots RSI Indicator\n
        `sma`: Gets simple moving average (EMA) for stock\n
        `stoch`: Stochastic oscillator\n
        `stoch_view`: Plots stochastic oscillator signal\n
        `vwap`: Gets volume weighted average price (VWAP)\n
        `vwap_view`: Plots VWMA technical indicator\n
        `wma`: Gets weighted moving average (WMA) for stock\n
        `zlma`: Gets zero-lagged exponential moving average (ZLEMA) for stock\n
    """

    def __init__(self):
        super().__init__()
        self.ad = lib.common_ta_volume_model.ad
        self.ad_view = lib.common_ta_volume_view.display_ad
        self.adosc = lib.common_ta_volume_model.adosc
        self.adosc_view = lib.common_ta_volume_view.display_adosc
        self.adx = lib.common_ta_trend_indicators_model.adx
        self.adx_view = lib.common_ta_trend_indicators_view.display_adx
        self.aroon = lib.common_ta_trend_indicators_model.aroon
        self.aroon_view = lib.common_ta_trend_indicators_view.display_aroon
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
