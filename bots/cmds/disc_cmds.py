from __future__ import annotations

import disnake
from disnake.ext import commands

from bots.helpers import ShowView
from bots.stocks.disc.active import active_command
from bots.stocks.disc.ford import ford_command
from bots.stocks.disc.topgainers import gainers_command
from bots.stocks.disc.toplosers import losers_command
from bots.stocks.disc.ugs import ugs_command


class DiscoverCommands(commands.Cog):
    """Discover menu."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def disc(self, inter):
        pass

    @disc.sub_command(name="tops")
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

    @disc.sub_command(name="ugs")
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

    @disc.sub_command(name="fidelity")
    async def fidelity(self, inter: disnake.AppCmdInter):
        """Display Orders by Fidelity Customers. [Fidelity]

        Parameters
        -----------
        num: Number of stocks to display
        """
        await ShowView().discord(ford_command, inter, "disc fidelity")


def setup(bot: commands.Bot):
    bot.add_cog(DiscoverCommands(bot))
