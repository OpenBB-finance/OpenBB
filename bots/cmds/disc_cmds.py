from __future__ import annotations

import disnake
from disnake.ext import commands

from bots.economy.heatmaps import heatmaps_command
from bots.helpers import ShowView, ticker_autocomp
from bots.stocks.disc.active import active_command
from bots.stocks.disc.ford import ford_command
from bots.stocks.disc.topgainers import gainers_command
from bots.stocks.disc.toplosers import losers_command
from bots.stocks.disc.ugs import ugs_command
from bots.stocks.disc.upcoming import earnings_command
from bots.stocks.insider.lins import lins_command


class DiscoverCommands(commands.Cog):
    """Discover menu."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="disc")
    async def discovery(self, inter):
        pass

    @commands.slash_command(name="heatmap")
    async def heatmap(
        inter: disnake.AppCmdInter,
        maps: str = commands.Param(
            choices={
                "S&P 500 Map",
                "Stock Market Map",
                "World Map",
                "ETF Map - Exchange Traded Funds Map",
            },
        ),
        timeline: str = commands.Param(
            choices={
                "1 Day Performance": "",
                "1 Week Performance": "w1",
                "1 Month Performance": "w4",
                "3 Month Performance": "w13",
                "6 Month Performance": "w26",
                "1 Year Performance": "w52",
                "Year To Date Performance": "ytd",
            },
        ),
    ):
        """Displays Heatmaps  [Finviz]

        Parameters
        -----------
        maps: Choose map to display
        timeline: Choose performance timeline to display
        """
        await ShowView().discord(heatmaps_command, inter, "heatmap", maps, timeline)

    @discovery.sub_command(name="tops")
    async def tops(
        self,
        inter: disnake.AppCmdInter,
        sort: str = commands.Param(
            choices={
                "Top Gainers",
                "Top Losers",
                "Most Active",
            },
        ),
        num: int = 10,
    ):
        """Displays Top Gainers/Losers, or Most Active Stocks  [Yahoo Finance]

        Parameters
        -----------
        sort: Sort by Top Gainers/Losers, or Most Active Stocks
        num: Number of stocks to display Default: 10
        """
        func = {
            "Top Gainers": gainers_command,
            "Top Losers": losers_command,
            "Most Active": active_command,
        }
        await ShowView().discord(func[sort], inter, "disc", num)

    @discovery.sub_command(name="ugs")
    async def ugs(
        self,
        inter: disnake.AppCmdInter,
        num: int = 10,
    ):
        """Displays Undervalued Growth Stocks  [Yahoo Finance]

        Parameters
        -----------
        num: Number of stocks to display Default: 10
        """
        await ShowView().discord(ugs_command, inter, "ugs", num)

    @discovery.sub_command(name="fidelity")
    async def fidelity(self, inter: disnake.AppCmdInter):
        """Display Orders by Fidelity Customers. [Fidelity]

        Parameters
        -----------
        num: Number of stocks to display
        """
        await ShowView().discord(ford_command, inter, "disc fidelity")

    @commands.slash_command(name="earnings")
    async def earnings(self, inter: disnake.AppCmdInter):
        """Display Upcoming Earnings. [Source: Seeking Alpha]"""
        await ShowView().discord(earnings_command, inter, "earnings")

    @commands.slash_command(name="ins-last")
    async def lins(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        num: int = 10,
    ):
        """Display insider activity for a given stock ticker. [Finviz]

        Parameters
        ----------
        ticker : Stock Ticker
        num : Number of latest insider activity to display
        """
        await ShowView().discord(lins_command, inter, "ins-last", ticker, num)


def setup(bot: commands.Bot):
    bot.add_cog(DiscoverCommands(bot))
