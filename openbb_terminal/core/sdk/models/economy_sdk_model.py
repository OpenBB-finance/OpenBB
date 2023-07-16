# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class EconomyRoot(Category):
    """Economy Module

    Attributes:
        `available_indices`: Get available indices\n
        `balance`: General government deficit is defined as the balance of income and expenditure of government,\n
        `balance_chart`: General government balance is defined as the balance of income and expenditure of government,\n
        `bigmac`: Display Big Mac Index for given countries\n
        `bigmac_chart`: Display Big Mac Index for given countries\n
        `ccpi`: Inflation measured by consumer price index (CPI) is defined as the change in the prices\n
        `ccpi_chart`: Inflation measured by consumer price index (CPI) is defined as the change in the prices\n
        `country_codes`: Get available country codes for Bigmac index\n
        `cpi`: Obtain CPI data from FRED. [Source: FRED]\n
        `cpi_chart`: Inflation measured by consumer price index (CPI) is defined as the change in\n
        `currencies`: Scrape data for global currencies\n
        `debt`: General government debt-to-GDP ratio measures the gross debt of the general\n
        `debt_chart`: General government debt-to-GDP ratio measures the gross debt of the general\n
        `events`: Get economic calendar for countries between specified dates\n
        `fgdp`: Real gross domestic product (GDP) is GDP given in constant prices and\n
        `fgdp_chart`: Real gross domestic product (GDP) is GDP given in constant prices and\n
        `fred`: Get Series data. [Source: FRED]\n
        `fred_chart`: Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]\n
        `fred_notes`: Get series notes. [Source: FRED]\n
        `future`: Get futures data. [Source: Finviz]\n
        `futures`: Get futures data.\n
        `gdp`: Gross domestic product (GDP) is the standard measure of the value added created\n
        `gdp_chart`: Gross domestic product (GDP) is the standard measure of the value added created\n
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
        `revenue`: Governments collect revenues mainly for two purposes: to finance the goods\n
        `revenue_chart`: Governments collect revenues mainly for two purposes: to finance the goods\n
        `rgdp`: Gross domestic product (GDP) is the standard measure of the value added\n
        `rgdp_chart`: Gross domestic product (GDP) is the standard measure of the value added\n
        `search_index`: Search indices by keyword. [Source: FinanceDatabase]\n
        `spending`: General government spending provides an indication of the size\n
        `spending_chart`: General government spending provides an indication of the size\n
        `treasury`: Get treasury rates from Federal Reserve\n
        `treasury_chart`: Display U.S. Treasury rates [Source: EconDB]\n
        `trust`: Trust in government refers to the share of people who report having confidence in\n
        `trust_chart`: Trust in government refers to the share of people who report having confidence in\n
        `usbonds`: Scrape data for us bonds\n
        `usdli`: The USD Liquidity Index is defined as: [WALCL - WLRRAL - WDTGAL]. It is expressed in billions of USD.\n
        `usdli_chart`: Display US Dollar Liquidity\n
        `valuation`: Get group (sectors, industry or country) valuation data. [Source: Finviz]\n
    """

    _location_path = "economy"

    def __init__(self):
        super().__init__()
        self.available_indices = lib.economy_yfinance_model.get_available_indices
        self.balance = lib.economy_oecd_model.get_balance
        self.balance_chart = lib.economy_oecd_view.plot_balance
        self.bigmac = lib.economy_nasdaq_model.get_big_mac_indices
        self.bigmac_chart = lib.economy_nasdaq_view.display_big_mac_index
        self.ccpi = lib.economy_oecd_model.get_cpi
        self.ccpi_chart = lib.economy_oecd_view.plot_cpi
        self.country_codes = lib.economy_nasdaq_model.get_country_codes
        self.cpi = lib.economy_fred_model.get_cpi
        self.cpi_chart = lib.economy_fred_view.plot_cpi
        self.currencies = lib.economy_wsj_model.global_currencies
        self.debt = lib.economy_oecd_model.get_debt
        self.debt_chart = lib.economy_oecd_view.plot_debt
        self.events = lib.economy_nasdaq_model.get_economic_calendar
        self.fgdp = lib.economy_oecd_model.get_gdp_forecast
        self.fgdp_chart = lib.economy_oecd_view.plot_gdp_forecast
        self.fred = lib.economy_fred_model.get_aggregated_series_data
        self.fred_chart = lib.economy_fred_view.display_fred_series
        self.fred_notes = lib.economy_fred_model.get_series_notes
        self.future = lib.economy_finviz_model.get_futures
        self.futures = lib.economy_sdk_helpers.futures
        self.gdp = lib.economy_oecd_model.get_gdp
        self.gdp_chart = lib.economy_oecd_view.plot_gdp
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
        self.revenue = lib.economy_oecd_model.get_revenue
        self.revenue_chart = lib.economy_oecd_view.plot_revenue
        self.rgdp = lib.economy_oecd_model.get_real_gdp
        self.rgdp_chart = lib.economy_oecd_view.plot_real_gdp
        self.search_index = lib.economy_yfinance_model.get_search_indices
        self.spending = lib.economy_oecd_model.get_spending
        self.spending_chart = lib.economy_oecd_view.plot_spending
        self.treasury = lib.economy_fedreserve_model.get_treasury_rates
        self.treasury_chart = lib.economy_fedreserve_view.show_treasuries
        self.trust = lib.economy_oecd_model.get_trust
        self.trust_chart = lib.economy_oecd_view.plot_trust
        self.usbonds = lib.economy_wsj_model.us_bonds
        self.usdli = lib.economy_fred_model.get_usd_liquidity
        self.usdli_chart = lib.economy_fred_view.display_usd_liquidity
        self.valuation = lib.economy_finviz_model.get_valuation_data
