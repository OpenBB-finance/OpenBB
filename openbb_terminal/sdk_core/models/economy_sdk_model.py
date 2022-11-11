# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class EconomyRoot(Category):
    """OpenBB SDK Economy Module

    Attributes:
        `available_indices`: Get available indices\n
        `bigmac`: Display Big Mac Index for given countries\n
        `bigmac_view`: Display Big Mac Index for given countries\n
        `country_codes`: Get available country codes for Bigmac index\n
        `cpi`: Get Consumer Price Index from Alpha Vantage\n
        `cpi_view`: Display US consumer price index (CPI) from AlphaVantage\n
        `currencies`: Scrape data for global currencies\n
        `events`: Get economic calendar [Source: Investing.com]\n
        `fred_notes`: Get series notes. [Source: FRED]\n
        `fred_series`: Get Series data. [Source: FRED]\n
        `fred_series_view`: Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]\n
        `fred_yeild_curve`: Gets yield curve data from FRED\n
        `fred_yeild_curve_view`: Display yield curve based on US Treasury rates for a specified date.\n
        `friend_ids`: Get Series IDs. [Source: FRED]\n
        `future`: Get futures data. [Source: Finviz]\n
        `futures`: Scrape data for top commodities\n
        `gdp`: Get annual or quarterly Real GDP for US\n
        `gdp_view`: Display US GDP from AlphaVantage\n
        `gdpc`: Real GDP per Capita for United States\n
        `gdpc_view`: Display US GDP per Capita from AlphaVantage\n
        `get_events_countries`: Get available countries for events command.\n
        `get_ycrv_countries`: Get available countries for ycrv command.\n
        `glbonds`: Scrape data for global bonds\n
        `index`: Get data on selected indices over time [Source: Yahoo Finance]\n
        `index_view`: Load (and show) the selected indices over time [Source: Yahoo Finance]\n
        `indices`: Get the top US indices\n
        `inf`: Get historical Inflation for United States from AlphaVantage\n
        `inf_view`: Display US Inflation from AlphaVantage\n
        `macro`: This functions groups the data queried from the EconDB database [Source: EconDB]\n
        `macro_view`: Show the received macro data about a company [Source: EconDB]\n
        `macro_countries`: This function returns the available countries and respective currencies.\n
        `macro_parameters`: This function returns the available macro parameters with detail.\n
        `overview`: Scrape data for market overview\n
        `performance`: Get group (sectors, industry or country) performance data. [Source: Finviz]\n
        `performance_view`: View group (sectors, industry or country) performance data. [Source: Finviz]\n
        `prefmap`: Opens Finviz map website in a browser. [Source: Finviz]\n
        `rtps`: Get real-time performance sector data\n
        `rtps_view`: Display Real-Time Performance sector. [Source: AlphaVantage]\n
        `search_index`: Search indices by keyword. [Source: FinanceDatabase]\n
        `spectrum`: Get group (sectors, industry or country) valuation/performance data. [Source: Finviz]\n
        `spectrum_view`: Display finviz spectrum in system viewer [Source: Finviz]\n
        `spread`: Get spread matrix. [Source: Investing.com]\n
        `spread_view`: Display spread matrix. [Source: Investing.com]\n
        `treasury`: Get U.S. Treasury rates [Source: EconDB]\n
        `treasury_view`: Display U.S. Treasury rates [Source: EconDB]\n
        `treasury_maturities`: Get treasury maturity options [Source: EconDB]\n
        `tyld`: Get historical yield for a given maturity\n
        `tyld_view`: Display historical treasury yield for given maturity\n
        `unemp`: Get historical unemployment for United States\n
        `unemp_view`: Display US unemployment AlphaVantage\n
        `usbonds`: Scrape data for us bonds\n
        `valuation`: Get group (sectors, industry or country) valuation data. [Source: Finviz]\n
        `ycrv`: Get yield curve for specified country. [Source: Investing.com]\n
        `ycrv_view`: Display yield curve for specified country. [Source: Investing.com]\n
    """

    def __init__(self):
        super().__init__()
        self.available_indices = lib.economy_yfinance_model.get_available_indices
        self.bigmac = lib.economy_nasdaq_model.get_big_mac_indices
        self.bigmac_view = lib.economy_nasdaq_view.display_big_mac_index
        self.country_codes = lib.economy_nasdaq_model.get_country_codes
        self.cpi = lib.economy_alphavantage_model.get_cpi
        self.cpi_view = lib.economy_alphavantage_view.display_cpi
        self.currencies = lib.economy_wsj_model.global_currencies
        self.events = lib.economy_investingcom_model.get_economic_calendar
        self.fred_notes = lib.economy_fred_model.get_series_notes
        self.fred_series = lib.economy_fred_model.get_aggregated_series_data
        self.fred_series_view = lib.economy_fred_view.display_fred_series
        self.fred_yeild_curve = lib.economy_fred_model.get_yield_curve
        self.fred_yeild_curve_view = lib.economy_fred_view.display_yield_curve
        self.friend_ids = lib.economy_fred_model.get_series_ids
        self.future = lib.economy_finviz_model.get_futures
        self.futures = lib.economy_wsj_model.top_commodities
        self.gdp = lib.economy_alphavantage_model.get_real_gdp
        self.gdp_view = lib.economy_alphavantage_view.display_real_gdp
        self.gdpc = lib.economy_alphavantage_model.get_gdp_capita
        self.gdpc_view = lib.economy_alphavantage_view.display_gdp_capita
        self.get_events_countries = lib.economy_investingcom_model.get_events_countries
        self.get_ycrv_countries = lib.economy_investingcom_model.get_ycrv_countries
        self.glbonds = lib.economy_wsj_model.global_bonds
        self.index = lib.economy_yfinance_model.get_indices
        self.index_view = lib.economy_yfinance_view.show_indices
        self.indices = lib.economy_wsj_model.us_indices
        self.inf = lib.economy_alphavantage_model.get_inflation
        self.inf_view = lib.economy_alphavantage_view.display_inflation
        self.macro = lib.economy_econdb_model.get_aggregated_macro_data
        self.macro_view = lib.economy_econdb_view.show_macro_data
        self.macro_countries = lib.economy_econdb_model.get_macro_countries
        self.macro_parameters = lib.economy_econdb_model.get_macro_parameters
        self.overview = lib.economy_wsj_model.market_overview
        self.performance = lib.economy_finviz_model.get_performance_data
        self.performance_view = lib.economy_finviz_view.display_performance
        self.prefmap = lib.economy_finviz_model.get_performance_map
        self.rtps = lib.economy_alphavantage_model.get_sector_data
        self.rtps_view = lib.economy_alphavantage_view.realtime_performance_sector
        self.search_index = lib.economy_yfinance_model.get_search_indices
        self.spectrum = lib.economy_finviz_model.get_spectrum_data
        self.spectrum_view = lib.economy_finviz_view.display_spectrum
        self.spread = lib.economy_investingcom_model.get_spread_matrix
        self.spread_view = lib.economy_investingcom_view.display_spread_matrix
        self.treasury = lib.economy_econdb_model.get_treasuries
        self.treasury_view = lib.economy_econdb_view.show_treasuries
        self.treasury_maturities = lib.economy_econdb_model.get_treasury_maturities
        self.tyld = lib.economy_alphavantage_model.get_treasury_yield
        self.tyld_view = lib.economy_alphavantage_view.display_treasury_yield
        self.unemp = lib.economy_alphavantage_model.get_unemployment
        self.unemp_view = lib.economy_alphavantage_view.display_unemployment
        self.usbonds = lib.economy_wsj_model.us_bonds
        self.valuation = lib.economy_finviz_model.get_valuation_data
        self.ycrv = lib.economy_investingcom_model.get_yieldcurve
        self.ycrv_view = lib.economy_investingcom_view.display_yieldcurve
