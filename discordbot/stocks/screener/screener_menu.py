import asyncio
import discord
import config_discordbot as cfg

# pylint: disable=wrong-import-order,too-many-branches
from discordbot import gst_bot

from stocks.screener.historical import historical_command
from stocks.screener.overview import overview_command
from stocks.screener.valuation import valuation_command
from stocks.screener.financial import financial_command
from stocks.screener.ownership import ownership_command
from stocks.screener.performance import performance_command
from stocks.screener.technical import technical_command


class ScreenerCommands(discord.ext.commands.Cog):
    """Screener menu"""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.ext.commands.command(name="stocks.scr.historical")
    async def historical(
        self,
        ctx: discord.ext.commands.Context,
        signal="",
        start="",
    ):
        """Displays trades made by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        signal: str
            Signals
        start:
            date (in date format for start date)
        """
        await historical_command(ctx, signal, start)

    @discord.ext.commands.command(name="stocks.scr.overview")
    async def overview(
            self,
            ctx: discord.ext.commands.Context,
            preset="template", sort="", limit="25", ascend="False"
    ):
        """Displays stocks with overview data such as Sector and Industry [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await overview_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(name="stocks.scr.valuation")
    async def valuation(
            self,
            ctx: discord.ext.commands.Context,
            preset="", sort="", limit="25", ascend="False"
    ):
        """Displays results from chosen preset focusing on valuation metrics [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await valuation_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(name="stocks.scr.financial")
    async def financial(
            self,
            ctx: discord.ext.commands.Context,
            preset="", sort="", limit="25", ascend="False"
    ):
        """Displays returned results from preset by financial metrics [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await financial_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(name="stocks.scr.ownership")
    async def ownership(
            self,
            ctx: discord.ext.commands.Context,
            preset="", sort="", limit="25", ascend="False"
    ):
        """Displays stocks based on own share float and ownership data [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await ownership_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(name="stocks.scr.performance")
    async def performance(
            self,
            ctx: discord.ext.commands.Context,
            preset="", sort="", limit="25", ascend="False"
    ):
        """Displays stocks and sort by performance categories [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await performance_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(name="stocks.scr.technical")
    async def technical(
            self,
            ctx: discord.ext.commands.Context,
            preset="template", sort="", limit="25", ascend="False"
    ):
        """Displays stocks according to chosen preset, sorting by technical factors [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await technical_command(ctx, preset, sort, limit, ascend)


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(ScreenerCommands(bot))
