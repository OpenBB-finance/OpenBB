"""Research Controller Module"""
__docformat__ = "numpy"

import logging
import webbrowser
from datetime import datetime
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class ResearchController(BaseController):
    """Research Controller class"""

    CHOICES_COMMANDS = [
        "barchart",
        "businessinsider",
        "bullrun",
        "fidelity",
        "fintel",
        "finviz",
        "fmp",
        "fool",
        "grufity",
        "macroaxis",
        "macrotrends",
        "marketchameleon",
        "marketwatch",
        "newsfilter",
        "stockanalysis",
        "stockrow",
        "tradingview",
        "yahoo",
        "zacks",
    ]
    PATH = "/stocks/res/"

    def __init__(
        self,
        ticker: str,
        start: datetime,
        interval: str,
        queue: Optional[List[str]] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker
        self.start = start
        self.interval = interval

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/res/", 50)
        mt.add_param("_ticker", self.ticker.upper())
        mt.add_raw("\n")
        mt.add_cmd("barchart")
        mt.add_cmd("businessinsider")
        mt.add_cmd("bullrun")
        mt.add_cmd("fidelity")
        mt.add_cmd("fintel")
        mt.add_cmd("finviz")
        mt.add_cmd("fmp")
        mt.add_cmd("fool")
        mt.add_cmd("grufity")
        mt.add_cmd("macroaxis")
        mt.add_cmd("macrotrends")
        mt.add_cmd("marketchameleon")
        mt.add_cmd("marketwatch")
        mt.add_cmd("newsfilter")
        mt.add_cmd("stockanalysis")
        mt.add_cmd("stockrow")
        mt.add_cmd("tradingview")
        mt.add_cmd("yahoo")
        mt.add_cmd("zacks")
        console.print(text=mt.menu_text, menu="Stocks - Research")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "res"]
        return []

    @log_start_end(log=logger)
    def call_macroaxis(self, _):
        """Process macroaxis command"""
        webbrowser.open(f"https://www.macroaxis.com/invest/market/{self.ticker}")

    @log_start_end(log=logger)
    def call_yahoo(self, _):
        """Process yahoo command"""
        webbrowser.open(f"https://finance.yahoo.com/quote/{self.ticker}")

    @log_start_end(log=logger)
    def call_finviz(self, _):
        """Process finviz command"""
        webbrowser.open(f"https://finviz.com/quote.ashx?t={self.ticker}")

    @log_start_end(log=logger)
    def call_bullrun(self, _):
        """Process bullrun command"""
        webbrowser.open(f"https://bullrun.com.br/acoes/{self.ticker}")

    @log_start_end(log=logger)
    def call_marketwatch(self, _):
        """Process marketwatch command"""
        webbrowser.open(f"https://www.marketwatch.com/investing/stock/{self.ticker}")

    @log_start_end(log=logger)
    def call_fool(self, _):
        """Process fool command"""
        webbrowser.open(f"https://www.fool.com/quote/{self.ticker}")

    @log_start_end(log=logger)
    def call_businessinsider(self, _):
        """Process businessinsider command"""
        webbrowser.open(
            f"https://markets.businessinsider.com/stocks/{self.ticker}-stock/"
        )

    @log_start_end(log=logger)
    def call_fmp(self, _):
        """Process fmp command"""
        webbrowser.open(
            f"https://financialmodelingprep.com/financial-summary/{self.ticker}"
        )

    @log_start_end(log=logger)
    def call_fidelity(self, _):
        """Process fidelity command"""
        webbrowser.open(
            f"https://eresearch.fidelity.com/eresearch/goto/evaluate/snapshot.jhtml?symbols={self.ticker}"
        )

    @log_start_end(log=logger)
    def call_tradingview(self, _):
        """Process tradingview command"""
        webbrowser.open(f"https://www.tradingview.com/symbols/{self.ticker}")

    @log_start_end(log=logger)
    def call_marketchameleon(self, _):
        """Process marketchameleon command"""
        webbrowser.open(f"https://marketchameleon.com/Overview/{self.ticker}")

    @log_start_end(log=logger)
    def call_stockrow(self, _):
        """Process stockrow command"""
        webbrowser.open(f"https://stockrow.com/{self.ticker}")

    @log_start_end(log=logger)
    def call_barchart(self, _):
        """Process barchart command"""
        webbrowser.open(
            f"https://www.barchart.com/stocks/quotes/{self.ticker}/overview"
        )

    @log_start_end(log=logger)
    def call_grufity(self, _):
        """Process grufity command"""
        webbrowser.open(f"https://grufity.com/stock/{self.ticker}")

    @log_start_end(log=logger)
    def call_fintel(self, _):
        """Process fintel command"""
        webbrowser.open(f"https://fintel.io/s/us/{self.ticker}")

    @log_start_end(log=logger)
    def call_zacks(self, _):
        """Process zacks command"""
        webbrowser.open(f"https://www.zacks.com/stock/quote/{self.ticker}")

    @log_start_end(log=logger)
    def call_macrotrends(self, _):
        """Process macrotrends command"""
        webbrowser.open(
            f"https://www.macrotrends.net/stocks/charts/{self.ticker}/{self.ticker}/market-cap"
        )

    @log_start_end(log=logger)
    def call_newsfilter(self, _):
        """Process newsfilter command"""
        webbrowser.open(f"https://newsfilter.io/search?query={self.ticker}")

    @log_start_end(log=logger)
    def call_stockanalysis(self, _):
        """Process stockanalysis command"""
        webbrowser.open(f"https://stockanalysis.com/stocks/{self.ticker}/")
