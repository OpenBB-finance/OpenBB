from __future__ import annotations

import disnake
from disnake.ext import commands

from bots.etf.holdings import holdings_command
from bots.etf.whatetf import by_ticker_command
from bots.helpers import ShowView
from bots.stocks.disc.etfs import etfs_command


class EtfCommands(commands.Cog):
    """Discover menu."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def etf(self, inter):
        pass

    @etf.sub_command(name="tops")
    async def etf_disc(
        inter: disnake.AppCmdInter,
        sort: str = commands.Param(
            choices={
                "Top Gainers": "gainers",
                "Top Decliners": "decliners",
                "Most Active": "active",
            },
        ),
    ):
        """Displays ETF's Top Gainers/Decliners, Most Active  [Wall Street Journal]

        Parameters
        -----------
        sort: Sort by Top Gainers, Top Decliners, or Most Active
        """
        await ShowView().discord(etfs_command, inter, "etf disc-tops", sort)

    @etf.sub_command_group()
    async def holdings(self, inter):
        pass

    @holdings.sub_command(name="by-etf")
    async def by_etf(
        inter: disnake.AppCmdInter,
        etf: str,
        num: int = 15,
    ):
        """Displays ETF's Holdings  [StockAnalysis]

        Parameters
        -----------
        etf: ETF Symbol
        num: Amount of holdings to display Default 15
        """
        await ShowView().discord(holdings_command, inter, "etf by-etf", etf, num)

    @holdings.sub_command(name="by-ticker")
    async def by_ticker(
        inter: disnake.AppCmdInter,
        ticker: str,
        num: int = 15,
    ):
        """Displays ETF Holdings By Ticker  [ETF DataBase]

        Parameters
        -----------
        ticker: Ticker to Search
        num: Amount of ETFs to display Default 15
        """
        await ShowView().discord(by_ticker_command, inter, "etf by-ticker", ticker, num)


def setup(bot: commands.Bot):
    bot.add_cog(EtfCommands(bot))
