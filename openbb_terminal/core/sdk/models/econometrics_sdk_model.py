# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class EconometricsRoot(Category):
    """Econometrics Module

    Attributes:
        `bgod`: Calculate test statistics for autocorrelation\n
        `bgod_chart`: Show Breusch-Godfrey autocorrelation test\n
        `bols`: The between estimator is an alternative, usually less efficient estimator, can can be used to\n
        `bpag`: Calculate test statistics for heteroscedasticity\n
        `bpag_chart`: Show Breusch-Pagan heteroscedasticity test\n
        `clean`: Clean up NaNs from the dataset\n
        `coint`: Calculate cointegration tests between variable number of input series\n
        `coint_chart`: Estimates long-run and short-run cointegration relationship for series y and x and apply\n
        `comparison`: Compare regression results between Panel Data regressions.\n
        `dwat`: Calculate test statistics for Durbin Watson autocorrelation\n
        `dwat_chart`: Show Durbin-Watson autocorrelation tests\n
        `fdols`: First differencing is an alternative to using fixed effects when there might be correlation.\n
        `fe`: When effects are correlated with the regressors the RE and BE estimators are not consistent.\n
        `garch`: Calculates volatility forecasts based on GARCH.\n
        `garch_chart`: Plots the volatility forecasts based on GARCH\n
        `get_regression_data`: This function creates a DataFrame with the required regression data as\n
        `granger`: Calculate granger tests\n
        `granger_chart`: Show granger tests\n
        `load`: Load custom file into dataframe.\n
        `norm`: The distribution of returns and generate statistics on the relation to the normal curve.\n
        `norm_chart`: Determine the normality of a timeseries.\n
        `ols`: Performs an OLS regression on timeseries data. [Source: Statsmodels]\n
        `options`: Obtain columns-dataset combinations from loaded in datasets that can be used in other commands\n
        `options_chart`: Plot custom data\n
        `panel`: Based on the regression type, this function decides what regression to run.\n
        `panel_chart`: Based on the regression type, this function decides what regression to run.\n
        `pols`: PooledOLS is just plain OLS that understands that various panel data structures.\n
        `re`: The random effects model is virtually identical to the pooled OLS model except that is accounts for the\n
        `root`: Calculate test statistics for unit roots\n
        `root_chart`: Determine the normality of a timeseries.\n
        `vif`: Calculates VIF (variance inflation factor), which tests collinearity.\n
    """

    _location_path = "econometrics"

    def __init__(self):
        super().__init__()
        self.bgod = lib.econometrics_regression_model.get_bgod
        self.bgod_chart = lib.econometrics_regression_view.display_bgod
        self.bols = lib.econometrics_regression_model.get_bols
        self.bpag = lib.econometrics_regression_model.get_bpag
        self.bpag_chart = lib.econometrics_regression_view.display_bpag
        self.clean = lib.econometrics_model.clean
        self.coint = lib.econometrics_model.get_coint_df
        self.coint_chart = lib.econometrics_view.display_cointegration_test
        self.comparison = lib.econometrics_regression_model.get_comparison
        self.dwat = lib.econometrics_regression_model.get_dwat
        self.dwat_chart = lib.econometrics_regression_view.display_dwat
        self.fdols = lib.econometrics_regression_model.get_fdols
        self.fe = lib.econometrics_regression_model.get_fe
        self.garch = lib.econometrics_model.get_garch
        self.garch_chart = lib.econometrics_view.display_garch
        self.get_regression_data = lib.econometrics_regression_model.get_regression_data
        self.granger = lib.econometrics_model.get_granger_causality
        self.granger_chart = lib.econometrics_view.display_granger
        self.load = lib.common_model.load
        self.norm = lib.econometrics_model.get_normality
        self.norm_chart = lib.econometrics_view.display_norm
        self.ols = lib.econometrics_regression_model.get_ols
        self.options = lib.econometrics_model.get_options
        self.options_chart = lib.econometrics_view.show_options
        self.panel = lib.econometrics_regression_model.get_regressions_results
        self.panel_chart = lib.econometrics_regression_view.display_panel
        self.pols = lib.econometrics_regression_model.get_pols
        self.re = lib.econometrics_regression_model.get_re
        self.root = lib.econometrics_model.get_root
        self.root_chart = lib.econometrics_view.display_root
        self.vif = lib.econometrics_model.get_vif
