"""OpenBB Terminal SDK ETF Module."""
import logging

import openbb_terminal.sdk_init as lib
from openbb_terminal.sdk_modules.sdk_helpers import Category, clean_attr_desc

logger = logging.getLogger(__name__)


class ETFDiscovery(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.mover = lib.etf_discovery_wsj_model.etf_movers
        self.mover_view = lib.etf_discovery_wsj_view.show_top_mover


class ETFScreen(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.screen = lib.etf_screener_model.etf_screener
        self.view = lib.etf_screener_view.view_screener


class ETFRoot(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.by_category = lib.etf_financedatabase_model.get_etfs_by_category
        self.by_category_view = lib.etf_financedatabase_view.display_etf_by_category
        self.ld = lib.etf_financedatabase_model.get_etfs_by_description
        self.ld_view = lib.etf_financedatabase_view.display_etf_by_description
        self.ln = lib.etf_financedatabase_model.get_etfs_by_name
        self.ln_view = lib.etf_financedatabase_view.display_etf_by_name
        self.holdings = lib.etf_stockanalysis_model.get_etf_holdings
        self.holdings_view = lib.etf_stockanalysis_view.view_holdings
        self.symbols = lib.etf_stockanalysis_model.get_all_names_symbols
        self.overview = lib.etf_stockanalysis_model.get_etf_overview
        self.overview_view = lib.etf_stockanalysis_view.view_overview
        self.by_name = lib.etf_stockanalysis_model.get_etfs_by_name
        self.by_name_view = lib.etf_stockanalysis_view.display_etf_by_name
        self.weights = lib.etf_yfinance_model.get_etf_sector_weightings
        self.weights_view = lib.etf_yfinance_view.display_etf_weightings
        self.summary = lib.etf_yfinance_model.get_etf_summary_description
        self.summary_view = lib.etf_yfinance_view.display_etf_description
        self.news = lib.common_newsapi_model.get_news
        self.news_view = lib.common_newsapi_view.display_news
        self.load = lib.stocks_helper.load
        self.candle = lib.stocks_helper.display_candle


class ETF(ETFRoot):
    """OpenBB SDK ETF Module"""

    @property
    def disc(self):
        """ETF Discovery Module

        Attributes:
            `mover`: Scrape data for top etf movers.\n
            `mover_view`: Show top ETF movers from wsj.com\n
        """
        return ETFDiscovery()

    @property
    def scr(self):
        """ETF Screener Module

        Attributes:
            `screen`: Get ETFs based of screener preset.\n
            `view`: Display screener output\n
        """
        return ETFScreen()

    def __repr__(self):
        attrs = [
            (f"    {k}: {clean_attr_desc(v)}\n")
            for k, v in self.__dict__.items()
            if v.__doc__ and not k.startswith("_")
        ]
        return (
            f"{self.__class__.__name__}(\n"
            f"disc={self.disc!r},\n"
            f"scr={self.scr!r},\n"
            f"{''.join(attrs)})"
        )
