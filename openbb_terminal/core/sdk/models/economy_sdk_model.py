# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class EconomyRoot(Category):
    """Economy Module

    Attributes:
        `available_indices`: Get available indices\n
        `bigmac`: Display Big Mac Index for given countries\n
        `bigmac_chart`: Display Big Mac Index for given countries\n
        `country_codes`: Get available country codes for Bigmac index\n
        `cpi`: Obtain CPI data from FRED. [Source: FRED]\n
        `cpi_chart`: Plot CPI data. [Source: FRED]\n
        `currencies`: Scrape data for global currencies\n
        `events`: Get economic calendar for countries between specified dates\n
        `fred`: Get Series data. [Source: FRED]\n
        `fred_chart`: Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]\n
        `fred_ids`: Get Series IDs. [Source: FRED]\n
        `fred_notes`: Get series notes. [Source: FRED]\n
        `future`: Get futures data. [Source: Finviz]\n
        `futures`: Get futures data.\n
        `get_groups`: Get group available\n
        `glbonds`: Scrape data for global bonds\n
        `index`: Get data on selected indices over time [Source: Yahoo Finance]\n
        `index_chart`: Load (and show) the selected indices over time [Source: Yahoo Finance]\n
        `indices`: Get the top US indices\n
        `macro`: This functions groups the data queried from the EconDB database [Source: EconDB]\n
        `macro_chart`: Show the received macro data about a company [Source: EconDB]\n
        `macro_countries`: This function returns the available countries and respective currencies.\n
        `macro_parameters`: This function returns the available macro parameters with detail.\n
        `overview`: Scrape data for market overview\n
        `perfmap`: Opens Finviz map website in a browser. [Source: Finviz]\n
        `performance`: Get group (sectors, industry or country) performance data. [Source: Finviz]\n
        `rtps`: Get real-time performance sector data\n
        `rtps_chart`: Display Real-Time Performance sector. [Source: AlphaVantage]\n
        `search_index`: Search indices by keyword. [Source: FinanceDatabase]\n
        `spectrum`: Display finviz spectrum in system viewer [Source: Finviz]\n
        `treasury`: Get U.S. Treasury rates [Source: EconDB]\n
        `treasury_chart`: Display U.S. Treasury rates [Source: EconDB]\n
        `treasury_maturities`: Get treasury maturity options [Source: EconDB]\n
        `usbonds`: Scrape data for us bonds\n
        `valuation`: Get group (sectors, industry or country) valuation data. [Source: Finviz]\n
    """

    _location_path = "economy"

    def __init__(self):
        super().__init__()
        self.available_indices = lib.economy_yfinance_model.get_available_indices
        self.bigmac = lib.economy_nasdaq_model.get_big_mac_indices
        self.bigmac_chart = lib.economy_nasdaq_view.display_big_mac_index
        self.country_codes = lib.economy_nasdaq_model.get_country_codes
        self.cpi = lib.economy_fred_model.get_cpi
        self.cpi_chart = lib.economy_fred_view.plot_cpi
        self.currencies = lib.economy_wsj_model.global_currencies
        self.events = lib.economy_nasdaq_model.get_economic_calendar
        self.fred = lib.economy_fred_model.get_aggregated_series_data
        self.fred_chart = lib.economy_fred_view.display_fred_series
        self.fred_ids = lib.economy_fred_model.get_series_ids
        self.fred_notes = lib.economy_fred_model.get_series_notes
        self.future = lib.economy_finviz_model.get_futures
        self.futures = lib.economy_sdk_helpers.futures
        self.get_groups = lib.economy_finviz_model.get_groups
        self.glbonds = lib.economy_wsj_model.global_bonds
        self.index = lib.economy_yfinance_model.get_indices
        self.index_chart = lib.economy_yfinance_view.show_indices
        self.indices = lib.economy_wsj_model.us_indices
        self.macro = lib.economy_econdb_model.get_aggregated_macro_data
        self.macro_chart = lib.economy_econdb_view.show_macro_data
        self.macro_countries = lib.economy_econdb_model.get_macro_countries
        self.macro_parameters = lib.economy_econdb_model.get_macro_parameters
        self.overview = lib.economy_wsj_model.market_overview
        self.perfmap = lib.economy_finviz_model.get_performance_map
        self.performance = lib.economy_finviz_model.get_performance_data
        self.rtps = lib.economy_alphavantage_model.get_sector_data
        self.rtps_chart = lib.economy_alphavantage_view.realtime_performance_sector
        self.search_index = lib.economy_yfinance_model.get_search_indices
        self.spectrum = lib.economy_finviz_view.display_spectrum
        self.treasury = lib.economy_econdb_model.get_treasuries
        self.treasury_chart = lib.economy_econdb_view.show_treasuries
        self.treasury_maturities = lib.economy_econdb_model.get_treasury_maturities
        self.usbonds = lib.economy_wsj_model.us_bonds
        self.valuation = lib.economy_finviz_model.get_valuation_data
