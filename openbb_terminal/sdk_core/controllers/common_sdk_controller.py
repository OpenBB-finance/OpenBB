# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.models import common_sdk_model as model


class CommonController(model.CommonRoot):
    """OpenBB SDK Common Module.

    Submodules:
        `qa`: Quantitative Analysis Module
        `ta`: Technical Analysis Module

    Attributes:
        `news`: Get news for a given term and source. [Source: Feedparser]\n
        `news_view`: Display news for a given term and source. [Source: Feedparser]\n
    """

    @property
    def qa(self):
        """OpenBB SDK Common Quantitative Analysis Submodule

        Submodules:
            `qa`: Quantitative Analysis Module

        Attributes:
            `bw`: Show box and whisker plots\n
            `calculate_adjusted_var`: Calculates VaR, which is adjusted for skew and kurtosis (Cornish-Fischer-Expansion)\n
            `decompose`: Perform seasonal decomposition\n
            `es`: Gets Expected Shortfall for specified stock dataframe.\n
            `es_view`: Displays expected shortfall.\n
            `kurtosis`: Kurtosis Indicator\n
            `kurtosis_view`: View rolling kurtosis\n
            `normality`: Look at the distribution of returns and generate statistics on the relation to the normal curve.\n
            `normality_view`: View normality statistics\n
            `omega`: Get the omega series\n
            `omega_view`: Displays the omega ratio\n
            `quantile`: Overlay Median & Quantile\n
            `quantile_view`: View rolling quantile\n
            `rolling`: Return rolling mean and standard deviation\n
            `rolling_view`: View mean std deviation\n
            `sharpe`: Calculates the sharpe ratio\n
            `sharpe_view`: Calculates the sharpe ratio\n
            `skew`: Skewness Indicator\n
            `skew_view`: View rolling skew\n
            `sortino`: Calculates the sortino ratio\n
            `sortino_view`: Displays the sortino ratio\n
            `spread`: Standard Deviation and Variance\n
            `spread_view`: View rolling spread\n
            `summary`: Print summary statistics\n
            `summary_view`: Show summary statistics\n
            `unitroot`: Calculate test statistics for unit roots\n
            `unitroot_view`: Show unit root test calculations\n
            `var`: Gets value at risk for specified stock dataframe.\n
            `var_view`: Displays VaR of dataframe.\n
        """

        return model.CommonQuantitativeAnalysis()

    @property
    def ta(self):
        """OpenBB SDK Common Technical Analysis Submodule

        Submodules:
            `ta`: Technical Analysis Module

        Attributes:
            `ad`: Calculate AD technical indicator\n
            `ad_view`: Plot AD technical indicator\n
            `adosc`: Calculate AD oscillator technical indicator\n
            `adosc_view`: Display AD Osc Indicator\n
            `adx`: ADX technical indicator\n
            `adx_view`: Plot ADX indicator\n
            `aroon`: Aroon technical indicator\n
            `aroon_view`: Plot Aroon indicator\n
            `atr`: Average True Range\n
            `atr_view`: Show ATR\n
            `bbands`: Calculate Bollinger Bands\n
            `bbands_view`: Show bollinger bands\n
            `donchian`: Calculate Donchian Channels\n
            `donchian_view`: Show donchian channels\n
            `ema`: Gets exponential moving average (EMA) for stock\n
            `fib`: Calculate Fibonacci levels\n
            `fib_view`: Calculate fibonacci retracement levels\n
            `fisher`: Fisher Transform\n
            `hma`: Gets hull moving average (HMA) for stock\n
            `kc`: Keltner Channels\n
            `kc_view`: View Keltner Channels Indicator\n
            `ma`: Plots MA technical indicator\n
            `macd`: Moving average convergence divergence\n
            `macd_view`: Plot MACD signal\n
            `obv`: On Balance Volume\n
            `obv_view`: Plot OBV technical indicator\n
            `rsi`: Relative strength index\n
            `rsi_view`: Display RSI Indicator\n
            `sma`: Gets simple moving average (EMA) for stock\n
            `stoch`: Stochastic oscillator\n
            `stoch_view`: Plot stochastic oscillator signal\n
            `vwap`: Gets volume weighted average price (VWAP)\n
            `vwap_view`: Plots VWMA technical indicator\n
            `wma`: Gets weighted moving average (WMA) for stock\n
            `zlma`: Gets zero-lagged exponential moving average (ZLEMA) for stock\n
        """

        return model.CommonTechnicalAnalysis()
