# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.models import etf_sdk_model as model


class EtfController(model.EtfRoot):
    """Etf Module.

    Submodules:
        `disc`: Discovery Module

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

    @property
    def disc(self):
        """Etf Discovery Submodule

        Attributes:
            `mover`: Scrape data for top etf movers.\n
        """

        return model.EtfDiscovery()
