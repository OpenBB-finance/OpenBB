# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class EtfRoot(Category):
    """OpenBB SDK Etf Module

    Attributes:
        `by_category`: Return a selection of ETFs based on category filtered by total assets.\n
        `by_category_view`: Display a selection of ETFs based on a category filtered by total assets.\n
        `by_name`: Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]\n
        `by_name_view`: Display ETFs matching search string. [Source: StockAnalysis]\n
        `candle`: Show candle plot of loaded ticker.\n
        `holdings`: Get ETF holdings\n
        `ld`: Return a selection of ETFs based on description filtered by total assets.\n
        `ld_view`: Display a selection of ETFs based on description filtered by total assets.\n
        `ln`: Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]\n
        `ln_view`: Display a selection of ETFs based on name filtered by total assets. [Source: Finance Database]\n
        `load`: Load a symbol to perform analysis using the string above as a template.\n
        `news`: Get news for a given term. [Source: NewsAPI]\n
        `news_view`: Display news for a given term. [Source: NewsAPI]\n
        `overview`: Get overview data for selected etf\n
        `overview_view`: Print etf overview information\n
        `summary`: Return summary description of ETF. [Source: Yahoo Finance]\n
        `summary_view`: Display ETF description summary. [Source: Yahoo Finance]\n
        `symbols`: Gets all etf names and symbols\n
        `weights`: Return sector weightings allocation of ETF. [Source: Yahoo Finance]\n
        `weights_view`: Display sector weightings allocation of ETF. [Source: Yahoo Finance]\n
    """

    def __init__(self):
        super().__init__()
        self.by_category = lib.etf_financedatabase_model.get_etfs_by_category
        self.by_category_view = lib.etf_financedatabase_view.display_etf_by_category
        self.by_name = lib.etf_stockanalysis_model.get_etfs_by_name
        self.by_name_view = lib.etf_stockanalysis_view.display_etf_by_name
        self.candle = lib.stocks_helper.display_candle
        self.holdings = lib.etf_stockanalysis_model.get_etf_holdings
        self.holdings_view = lib.etf_stockanalysis_view.view_holdings
        self.ld = lib.etf_financedatabase_model.get_etfs_by_description
        self.ld_view = lib.etf_financedatabase_view.display_etf_by_description
        self.ln = lib.etf_financedatabase_model.get_etfs_by_name
        self.ln_view = lib.etf_financedatabase_view.display_etf_by_name
        self.load = lib.stocks_helper.load
        self.news = lib.common_newsapi_model.get_news
        self.news_view = lib.common_newsapi_view.display_news
        self.overview = lib.etf_stockanalysis_model.get_etf_overview
        self.overview_view = lib.etf_stockanalysis_view.view_overview
        self.summary = lib.etf_yfinance_model.get_etf_summary_description
        self.summary_view = lib.etf_yfinance_view.display_etf_description
        self.symbols = lib.etf_stockanalysis_model.get_all_names_symbols
        self.weights = lib.etf_yfinance_model.get_etf_sector_weightings
        self.weights_view = lib.etf_yfinance_view.display_etf_weightings


class EtfDiscovery(Category):
    """OpenBB SDK Discovery Module.

    Attributes:
        `mover`: Scrape data for top etf movers.\n
        `mover_view`: Show top ETF movers from wsj.com\n
    """

    def __init__(self):
        super().__init__()
        self.mover = lib.etf_disc_wsj_model.etf_movers
        self.mover_view = lib.etf_disc_wsj_view.show_top_mover


class EtfScr(Category):
    """OpenBB SDK Scr Module.

    Attributes:
        `screen`: Screens the etfs pulled from my repo (https://github.com/jmaslek/etf_scraper),\n
        `view`: Display screener output\n
    """

    def __init__(self):
        super().__init__()
        self.screen = lib.etf_scr_model.etf_screener
        self.view = lib.etf_scr_view.view_screener
