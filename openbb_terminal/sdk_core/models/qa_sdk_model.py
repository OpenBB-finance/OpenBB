# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class QaRoot(Category):
    """OpenBB SDK Quantitative Analysis Module

    Attributes:
        `bw`: Plots box and whisker plots\n
        `calculate_adjusted_var`: Calculates VaR, which is adjusted for skew and kurtosis (Cornish-Fischer-Expansion)\n
        `decompose`: Perform seasonal decomposition\n
        `es`: Gets Expected Shortfall for specified stock dataframe.\n
        `es_print`: Prints table showing expected shortfall.\n
        `kurtosis`: Kurtosis Indicator\n
        `kurtosis_chart`: Plots rolling kurtosis\n
        `normality`: Look at the distribution of returns and generate statistics on the relation to the normal curve.\n
        `normality_print`: Prints table showing normality statistics\n
        `omega`: Get the omega series\n
        `omega_chart`: Plots the omega ratio\n
        `quantile`: Overlay Median & Quantile\n
        `quantile_chart`: Plots rolling quantile\n
        `rolling`: Return rolling mean and standard deviation\n
        `rolling_chart`: Plots mean std deviation\n
        `sharpe`: Calculates the sharpe ratio\n
        `sharpe_chart`: Plots Calculated the sharpe ratio\n
        `skew`: Skewness Indicator\n
        `skew_chart`: Plots rolling skew\n
        `sortino`: Calculates the sortino ratio\n
        `sortino_chart`: Plots the sortino ratio\n
        `spread`: Standard Deviation and Variance\n
        `spread_chart`: Plots rolling spread\n
        `summary`: Print summary statistics\n
        `summary_print`: Prints table showing summary statistics\n
        `unitroot`: Calculate test statistics for unit roots\n
        `unitroot_print`: Prints table showing unit root test calculations\n
        `var`: Gets value at risk for specified stock dataframe.\n
        `var_print`: Prints table showing VaR of dataframe.\n
    """

    def __init__(self):
        super().__init__()
        self.bw = lib.common_qa_view.display_bw
        self.calculate_adjusted_var = lib.common_qa_model.calculate_adjusted_var
        self.decompose = lib.common_qa_model.get_seasonal_decomposition
        self.es = lib.common_qa_model.get_es
        self.es_print = lib.common_qa_view.display_es
        self.kurtosis = lib.common_qa_rolling_model.get_kurtosis
        self.kurtosis_chart = lib.common_qa_rolling_view.display_kurtosis
        self.normality = lib.common_qa_model.get_normality
        self.normality_print = lib.common_qa_view.display_normality
        self.omega = lib.common_qa_model.get_omega
        self.omega_chart = lib.common_qa_view.display_omega
        self.quantile = lib.common_qa_rolling_model.get_quantile
        self.quantile_chart = lib.common_qa_rolling_view.display_quantile
        self.rolling = lib.common_qa_rolling_model.get_rolling_avg
        self.rolling_chart = lib.common_qa_rolling_view.display_mean_std
        self.sharpe = lib.common_qa_model.get_sharpe
        self.sharpe_chart = lib.common_qa_view.display_sharpe
        self.skew = lib.common_qa_rolling_model.get_skew
        self.skew_chart = lib.common_qa_rolling_view.display_skew
        self.sortino = lib.common_qa_model.get_sortino
        self.sortino_chart = lib.common_qa_view.display_sortino
        self.spread = lib.common_qa_rolling_model.get_spread
        self.spread_chart = lib.common_qa_rolling_view.display_spread
        self.summary = lib.common_qa_model.get_summary
        self.summary_print = lib.common_qa_view.display_summary
        self.unitroot = lib.common_qa_model.get_unitroot
        self.unitroot_print = lib.common_qa_view.display_unitroot
        self.var = lib.common_qa_model.get_var
        self.var_print = lib.common_qa_view.display_var
