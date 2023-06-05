# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class TaRoot(Category):
    """Technical Analysis Module

    Attributes:
        `ad`: Calculate AD technical indicator\n
        `ad_chart`: Plots AD technical indicator\n
        `adosc`: Calculate AD oscillator technical indicator\n
        `adosc_chart`: Plots AD Osc Indicator\n
        `adx`: ADX technical indicator\n
        `adx_chart`: Plots ADX indicator\n
        `aroon`: Aroon technical indicator\n
        `aroon_chart`: Plots Aroon indicator\n
        `atr`: Average True Range\n
        `atr_chart`: Plots ATR\n
        `bbands`: Calculate Bollinger Bands\n
        `bbands_chart`: Plots bollinger bands\n
        `cci`: Commodity channel index\n
        `cci_chart`: Plots CCI Indicator\n
        `cg`: Center of gravity\n
        `cg_chart`: Plots center of gravity Indicator\n
        `clenow`: Gets the Clenow Volatility Adjusted Momentum.  this is defined as the regression coefficient on log prices\n
        `clenow_chart`: Prints table and plots clenow momentum\n
        `cones`: Returns a DataFrame of realized volatility quantiles.\n
        `cones_chart`: Plots the realized volatility quantiles for the loaded ticker.\n
        `demark`: Get the integer value for demark sequential indicator\n
        `demark_chart`: Plot demark sequential indicator\n
        `donchian`: Calculate Donchian Channels\n
        `donchian_chart`: Plots donchian channels\n
        `ema`: Gets exponential moving average (EMA) for stock\n
        `fib`: Calculate Fibonacci levels\n
        `fib_chart`: Plots Calculated fibonacci retracement levels\n
        `fisher`: Fisher Transform\n
        `fisher_chart`: Plots Fisher Indicator\n
        `hma`: Gets hull moving average (HMA) for stock\n
        `kc`: Keltner Channels\n
        `kc_chart`: Plots Keltner Channels Indicator\n
        `ma`: Plots MA technical indicator\n
        `ma_chart`: Plots MA technical indicator\n
        `macd`: Moving average convergence divergence\n
        `macd_chart`: Plots MACD signal\n
        `obv`: On Balance Volume\n
        `obv_chart`: Plots OBV technical indicator\n
        `rsi`: Relative strength index\n
        `rsi_chart`: Plots RSI Indicator\n
        `rvol_garman_klass`: Garman-Klass volatility extends Parkinson volatility by taking into account the opening and closing price.\n
        `rvol_hodges_tompkins`: Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.\n
        `rvol_parkinson`: Parkinson volatility uses the high and low price of the day rather than just close to close prices.\n
        `rvol_rogers_satchell`: Rogers-Satchell is an estimator for measuring the volatility with an average return not equal to zero.\n
        `rvol_std`: Standard deviation measures how widely returns are dispersed from the average return.\n
        `rvol_yang_zhang`: Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).\n
        `sma`: Gets simple moving average (SMA) for stock\n
        `standard_deviation`: Standard deviation measures how widely returns are dispersed from the average return.\n
        `stoch`: Stochastic oscillator\n
        `stoch_chart`: Plots stochastic oscillator signal\n
        `vwap`: Gets volume weighted average price (VWAP)\n
        `vwap_chart`: Plots VWMA technical indicator\n
        `wma`: Gets weighted moving average (WMA) for stock\n
        `zlma`: Gets zero-lagged exponential moving average (ZLEMA) for stock\n
    """

    _location_path = "ta"

    def __init__(self):
        super().__init__()
        self.ad = lib.common_ta_volume_model.ad
        self.ad_chart = lib.common_ta_volume_view.display_ad
        self.adosc = lib.common_ta_volume_model.adosc
        self.adosc_chart = lib.common_ta_volume_view.display_adosc
        self.adx = lib.common_ta_trend_indicators_model.adx
        self.adx_chart = lib.common_ta_trend_indicators_view.display_adx
        self.aroon = lib.common_ta_trend_indicators_model.aroon
        self.aroon_chart = lib.common_ta_trend_indicators_view.display_aroon
        self.atr = lib.common_ta_volatility_model.atr
        self.atr_chart = lib.common_ta_volatility_view.display_atr
        self.bbands = lib.common_ta_volatility_model.bbands
        self.bbands_chart = lib.common_ta_volatility_view.display_bbands
        self.cci = lib.common_ta_momentum_model.cci
        self.cci_chart = lib.common_ta_momentum_view.display_cci
        self.cg = lib.common_ta_momentum_model.cg
        self.cg_chart = lib.common_ta_momentum_view.display_cg
        self.clenow = lib.common_ta_momentum_model.clenow_momentum
        self.clenow_chart = lib.common_ta_momentum_view.display_clenow_momentum
        self.cones = lib.common_ta_volatility_model.cones
        self.cones_chart = lib.common_ta_volatility_view.display_cones
        self.demark = lib.common_ta_momentum_model.demark_seq
        self.demark_chart = lib.common_ta_momentum_view.display_demark
        self.donchian = lib.common_ta_volatility_model.donchian
        self.donchian_chart = lib.common_ta_volatility_view.display_donchian
        self.ema = lib.common_ta_overlap_model.ema
        self.fib = lib.common_ta_custom_indicators_model.calculate_fib_levels
        self.fib_chart = lib.common_ta_custom_indicators_view.fibonacci_retracement
        self.fisher = lib.common_ta_momentum_model.fisher
        self.fisher_chart = lib.common_ta_momentum_view.display_fisher
        self.hma = lib.common_ta_overlap_model.hma
        self.kc = lib.common_ta_volatility_model.kc
        self.kc_chart = lib.common_ta_volatility_view.view_kc
        self.ma = lib.common_ta_overlap_view.view_ma
        self.ma_chart = lib.common_ta_overlap_view.view_ma
        self.macd = lib.common_ta_momentum_model.macd
        self.macd_chart = lib.common_ta_momentum_view.display_macd
        self.obv = lib.common_ta_volume_model.obv
        self.obv_chart = lib.common_ta_volume_view.display_obv
        self.rsi = lib.common_ta_momentum_model.rsi
        self.rsi_chart = lib.common_ta_momentum_view.display_rsi
        self.rvol_garman_klass = lib.common_ta_volatility_model.garman_klass
        self.rvol_hodges_tompkins = lib.common_ta_volatility_model.hodges_tompkins
        self.rvol_parkinson = lib.common_ta_volatility_model.parkinson
        self.rvol_rogers_satchell = lib.common_ta_volatility_model.rogers_satchell
        self.rvol_std = lib.common_ta_volatility_model.standard_deviation
        self.rvol_yang_zhang = lib.common_ta_volatility_model.yang_zhang
        self.sma = lib.common_ta_overlap_model.sma
        self.standard_deviation = lib.common_ta_volatility_model.standard_deviation
        self.stoch = lib.common_ta_momentum_model.stoch
        self.stoch_chart = lib.common_ta_momentum_view.display_stoch
        self.vwap = lib.common_ta_overlap_model.vwap
        self.vwap_chart = lib.common_ta_overlap_view.view_vwap
        self.wma = lib.common_ta_overlap_model.wma
        self.zlma = lib.common_ta_overlap_model.zlma
