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
        `news_view`: Plots news for a given term and source. [Source: Feedparser]\n
    """

    @property
    def qa(self):
        """OpenBB SDK Common Quantitative Analysis Submodule

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

        return model.CommonQuantitativeAnalysis()

    @property
    def ta(self):
        """OpenBB SDK Common Technical Analysis Submodule

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

        return model.CommonTechnicalAnalysis()
