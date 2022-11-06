"""OpenBB Terminal SDK Econometrics/Economy Modules."""
import logging

import openbb_terminal.sdk_init as lib
from openbb_terminal.sdk_modules.sdk_helpers import Category

logger = logging.getLogger(__name__)


class Econometrics(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.clean = lib.econometrics_model.clean
        self.coint = (
            lib.econometrics_model.get_engle_granger_two_step_cointegration_test
        )
        self.coint_view = lib.econometrics_view.display_cointegration_test
        self.granger = lib.econometrics_model.get_granger_causality
        self.granger_view = lib.econometrics_view.display_granger
        self.norm = lib.econometrics_model.get_normality
        self.norm_view = lib.econometrics_view.display_norm
        self.options = lib.econometrics_model.get_options
        self.options_view = lib.econometrics_view.show_options
        self.root = lib.econometrics_model.get_root
        self.root_view = lib.econometrics_view.display_root
        self.load = lib.common_model.load
        self.bgod = lib.econometrics_regression_model.get_bgod
        self.bgod_view = lib.econometrics_regression_view.display_bgod
        self.bols = lib.econometrics_regression_model.get_bols
        self.bpag = lib.econometrics_regression_model.get_bpag
        self.bpag_view = lib.econometrics_regression_view.display_bpag
        self.comparison = lib.econometrics_regression_model.get_comparison
        self.dwat = lib.econometrics_regression_model.get_dwat
        self.dwat_view = lib.econometrics_regression_view.display_dwat
        self.fdols = lib.econometrics_regression_model.get_fdols
        self.fe = lib.econometrics_regression_model.get_fe
        self.ols = lib.econometrics_regression_model.get_ols
        self.pols = lib.econometrics_regression_model.get_pols
        self.re = lib.econometrics_regression_model.get_re
        self.get_regression_data = lib.econometrics_regression_model.get_regression_data
        self.panel = lib.econometrics_regression_model.get_regressions_results
        self.panel_view = lib.econometrics_regression_view.display_panel


class Economy(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.cpi = lib.economy_alphavantage_model.get_cpi
        self.cpi_view = lib.economy_alphavantage_view.display_cpi
        self.gdpc = lib.economy_alphavantage_model.get_gdp_capita
        self.gdpc_view = lib.economy_alphavantage_view.display_gdp_capita
        self.inf = lib.economy_alphavantage_model.get_inflation
        self.inf_view = lib.economy_alphavantage_view.display_inflation
        self.gdp = lib.economy_alphavantage_model.get_real_gdp
        self.gdp_view = lib.economy_alphavantage_view.display_real_gdp
        self.rtps = lib.economy_alphavantage_model.get_sector_data
        self.rtps_view = lib.economy_alphavantage_view.realtime_performance_sector
        self.tyld = lib.economy_alphavantage_model.get_treasury_yield
        self.tyld_view = lib.economy_alphavantage_view.display_treasury_yield
        self.unemp = lib.economy_alphavantage_model.get_unemployment
        self.unemp_view = lib.economy_alphavantage_view.display_unemployment
        self.macro = lib.economy_econdb_model.get_aggregated_macro_data
        self.macro_view = lib.economy_econdb_view.show_macro_data
        self.macro_parameters = lib.economy_econdb_model.get_macro_parameters
        self.macro_countries = lib.economy_econdb_model.get_macro_countries
        self.treasury = lib.economy_econdb_model.get_treasuries
        self.treasury_view = lib.economy_econdb_view.show_treasuries
        self.treasury_maturities = lib.economy_econdb_model.get_treasury_maturities
        self.future = lib.economy_finviz_model.get_futures
        self.spectrum = lib.economy_finviz_model.get_spectrum_data
        self.spectrum_view = lib.economy_finviz_view.display_spectrum
        self.valuation = lib.economy_finviz_model.get_valuation_data
        self.performance = lib.economy_finviz_model.get_performance_data
        self.performance_view = lib.economy_finviz_view.display_performance
        self.prefmap = lib.economy_finviz_model.get_performance_map
        self.fred_series = lib.economy_fred_model.get_aggregated_series_data
        self.fred_series_view = lib.economy_fred_view.display_fred_series
        self.friend_ids = lib.economy_fred_model.get_series_ids
        self.fred_notes = lib.economy_fred_model.get_series_notes
        self.fred_yeild_curve = lib.economy_fred_model.get_yield_curve
        self.fred_yeild_curve_view = lib.economy_fred_view.display_yield_curve
        self.get_events_countries = lib.economy_investingcom_model.get_events_countries
        self.events = lib.economy_investingcom_model.get_economic_calendar
        self.get_ycrv_countries = lib.economy_investingcom_model.get_ycrv_countries
        self.ycrv = lib.economy_investingcom_model.get_yieldcurve
        self.ycrv_view = lib.economy_investingcom_view.display_yieldcurve
        self.spread = lib.economy_investingcom_model.get_spread_matrix
        self.spread_view = lib.economy_investingcom_view.display_spread_matrix
        self.country_codes = lib.economy_nasdaq_model.get_country_codes
        self.bigmac = lib.economy_nasdaq_model.get_big_mac_indices
        self.bigmac_view = lib.economy_nasdaq_view.display_big_mac_index
        self.glbonds = lib.economy_wsj_model.global_bonds
        self.currencies = lib.economy_wsj_model.global_currencies
        self.overview = lib.economy_wsj_model.market_overview
        self.futures = lib.economy_wsj_model.top_commodities
        self.usbonds = lib.economy_wsj_model.us_bonds
        self.indices = lib.economy_wsj_model.us_indices
        self.index = lib.economy_yfinance_model.get_indices
        self.index_view = lib.economy_yfinance_view.show_indices
        self.available_indices = lib.economy_yfinance_model.get_available_indices
        self.search_index = lib.economy_yfinance_model.get_search_indices
