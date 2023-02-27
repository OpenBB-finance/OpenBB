# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class EtfRoot(Category):
    """Etf Module

    Attributes:
        `candle`: Show candle plot of loaded ticker.\n
        `compare`: Compare selected ETFs\n
        `etf_by_category`: Return a selection of ETFs based on category filtered by total assets.\n
        `etf_by_name`: Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]\n
        `holdings`: Get ETF holdings\n
        `ld`: Return a selection of ETFs based on description filtered by total assets.\n
        `ln`: Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]\n
        `load`: Load a symbol to perform analysis using the string above as a template.\n
        `news`: Get news for a given term. [Source: NewsAPI]\n
        `news_chart`: Prints table showing news for a given term. [Source: NewsAPI]\n
        `overview`: Get overview data for selected etf\n
        `symbols`: Gets all etf names and symbols\n
        `weights`: Return sector weightings allocation of ETF. [Source: FinancialModelingPrep]\n
    """

    _location_path = "etf"

    def __init__(self):
        super().__init__()
        self.candle = lib.stocks_helper.display_candle
        self.compare = lib.etf_stockanalysis_model.compare_etfs
        self.etf_by_category = lib.etf_financedatabase_model.get_etfs_by_category
        self.etf_by_name = lib.etf_stockanalysis_model.get_etfs_by_name
        self.holdings = lib.etf_stockanalysis_model.get_etf_holdings
        self.ld = lib.etf_financedatabase_model.get_etfs_by_description
        self.ln = lib.etf_financedatabase_model.get_etfs_by_name
        self.load = lib.stocks_helper.load
        self.news = lib.common_newsapi_model.get_news
        self.news_chart = lib.common_newsapi_view.display_news
        self.overview = lib.etf_stockanalysis_model.get_etf_overview
        self.symbols = lib.etf_stockanalysis_model.get_all_names_symbols
        self.weights = lib.etf_fmp_model.get_etf_sector_weightings


class EtfDiscovery(Category):
    """Discovery Module.

    Attributes:
        `mover`: Scrape data for top etf movers.\n
    """

    _location_path = "etf.disc"

    def __init__(self):
        super().__init__()
        self.mover = lib.etf_disc_wsj_model.etf_movers
