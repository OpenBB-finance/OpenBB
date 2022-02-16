from __future__ import annotations

import disnake
from disnake.ext import commands

from bots.helpers import ShowView, presets_custom_autocomp, signals_autocomp
from bots.stocks.screener.financial import financial_command
from bots.stocks.screener.historical import historical_command
from bots.stocks.screener.overview import overview_command
from bots.stocks.screener.ownership import ownership_command
from bots.stocks.screener.performance import performance_command
from bots.stocks.screener.presets_custom import presets_custom_command
from bots.stocks.screener.presets_default import presets_default_command
from bots.stocks.screener.technical import technical_command
from bots.stocks.screener.valuation import valuation_command

sort = {
    "overview": [
        "Ticker",
        "Company",
        "Sector",
        "Industry",
        "Country",
        "Market Cap",
        "P/E",
        "Price",
        "Change",
        "Volume",
    ],
    "valuation": [
        "Ticker",
        "Market Cap",
        "P/E",
        "Fwd P/E",
        "PEG",
        "P/S",
        "P/B",
        "P/C",
        "P/FCF",
        "EPS this Y",
        "EPS next Y",
        "EPS past 5Y",
        "EPS next 5Y",
        "Sales past 5Y",
        "Price",
        "Change",
        "Volume",
    ],
    "financial": [
        "Ticker",
        "Market Cap",
        "Dividend",
        "ROA",
        "ROE",
        "ROI",
        "Curr R",
        "Quick R",
        "LTDebt/Eq",
        "Debt/Eq",
        "Gross M",
        "Oper M",
        "Profit M",
        "Earnings",
        "Price",
        "Change",
        "Volume",
    ],
    "ownership": [
        "Ticker",
        "Market Cap",
        "Outstanding",
        "Float",
        "Insider Own",
        "Insider Trans",
        "Inst Own",
        "Inst Trans",
        "Float Short",
        "Short Ratio",
        "Avg Volume",
        "Price",
        "Change",
        "Volume",
    ],
    "performance": [
        "Ticker",
        "Perf Week",
        "Perf Month",
        "Perf Quart",
        "Perf Half",
        "Perf Year",
        "Perf YTD",
        "Volatility W",
        "Volatility M",
        "Recom",
        "Avg Volume",
        "Rel Volume",
        "Price",
        "Change",
        "Volume",
    ],
    "technical": [
        "Ticker",
        "Beta",
        "ATR",
        "SMA20",
        "SMA50",
        "SMA200",
        "52W High",
        "52W Low",
        "RSI",
        "Price",
        "Change",
        "from Open",
        "Gap",
        "Volume",
    ],
}
# pylint: disable=R0912


class ScreenerCommands(commands.Cog):
    """Screener menu"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="scr-presets_default")
    async def presets_default(self, inter: disnake.AppCmdInter):
        """Displays every available preset"""
        await ShowView().discord(presets_default_command, inter, "scr-presets_default")

    @commands.slash_command(name="scr-presets_custom")
    async def presets_custom(self, inter: disnake.AppCmdInter):
        """Displays every available preset"""
        await ShowView().discord(presets_custom_command, inter, "scr-presets_custom")

    @commands.slash_command(name="scr-historical")
    async def historical(
        self,
        inter: disnake.AppCmdInter,
        signal: str = commands.Param(autocomplete=signals_autocomp),
        start="",
    ):
        """Displays trades made by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        signal: Signal. Default: most_volatile
        start: Starting date in YYYY-MM-DD format
        """
        await ShowView().discord(
            historical_command, inter, "scr-historical", signal, start
        )

    @commands.slash_command(name="scr-overview")
    async def overview(
        self,
        inter: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["overview"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays stocks with overview data such as Sector and Industry [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ShowView().discord(
            overview_command, inter, "scr-overview", preset, sort, limit, ascend
        )

    @commands.slash_command(name="scr-valuation")
    async def valuation(
        self,
        inter: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["valuation"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays results from chosen preset focusing on valuation metrics [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ShowView().discord(
            valuation_command, inter, "scr-valuation", preset, sort, limit, ascend
        )

    @commands.slash_command(name="scr-financial")
    async def financial(
        self,
        inter: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["financial"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays returned results from preset by financial metrics [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ShowView().discord(
            financial_command, inter, "scr-financial", preset, sort, limit, ascend
        )

    @commands.slash_command(name="scr-ownership")
    async def ownership(
        self,
        inter: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["ownership"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays stocks based on own share float and ownership data [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ShowView().discord(
            ownership_command, inter, "scr-ownership", preset, sort, limit, ascend
        )

    @commands.slash_command(name="scr-performance")
    async def performance(
        self,
        inter: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["performance"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays stocks and sort by performance categories [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ShowView().discord(
            performance_command, inter, "scr-performance", preset, sort, limit, ascend
        )

    @commands.slash_command(name="scr-technical")
    async def technical(
        self,
        inter: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["technical"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays stocks according to chosen preset, sorting by technical factors [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ShowView().discord(
            technical_command, inter, "scr-technical", preset, sort, limit, ascend
        )


def setup(bot: commands.Bot):
    bot.add_cog(ScreenerCommands(bot))
