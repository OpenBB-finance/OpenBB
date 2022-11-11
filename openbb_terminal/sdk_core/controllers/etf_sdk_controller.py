# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.models import etf_sdk_model as model


class EtfController(model.EtfRoot):
    """OpenBB SDK Etf Module.

    Submodules:
        `disc`: Discovery Module
        `scr`: Scr Module

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

    @property
    def disc(self):
        """OpenBB SDK Etf Discovery Submodule

        Submodules:
            `disc`: Discovery Module

        Attributes:
            `mover`: Scrape data for top etf movers.\n
            `mover_view`: Show top ETF movers from wsj.com\n
        """

        return model.EtfDiscovery()

    @property
    def scr(self):
        """OpenBB SDK Etf Scr Submodule

        Submodules:
            `scr`: Scr Module

        Attributes:
            `screen`: Screens the etfs pulled from my repo (https://github.com/jmaslek/etf_scraper),\n
            `view`: Display screener output\n
        """

        return model.EtfScr()
