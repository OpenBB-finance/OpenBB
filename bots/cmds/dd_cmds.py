from __future__ import annotations

import disnake
from disnake.ext import commands

from bots.helpers import ShowView, ticker_autocomp
from bots.stocks.due_diligence.analyst import analyst_command
from bots.stocks.due_diligence.arktrades import arktrades_command
from bots.stocks.due_diligence.borrowed import borrowed_command
from bots.stocks.due_diligence.customer import customer_command
from bots.stocks.due_diligence.est import est_command
from bots.stocks.due_diligence.pt import pt_command
from bots.stocks.due_diligence.sec import sec_command
from bots.stocks.due_diligence.supplier import supplier_command


class DueDiligenceCommands(commands.Cog):
    """Due Diligence menu."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="dd")
    async def dd(self, inter):
        pass

    @dd.sub_command()
    async def analyst(
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays analyst recommendations [Finviz]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(analyst_command, inter, "dd analyst", ticker)

    @dd.sub_command()
    async def borrowed(
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays borrowed shares available and fee [Stocksera]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(borrowed_command, inter, "dd borrowed", ticker)

    @dd.sub_command()
    async def pt(
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        raw: bool = False,
        start="",
    ):
        """Displays chart with price targets [Business Insiders]

        Parameters
        -----------
        ticker: Stock Ticker
        raw: True or false
        start: YYYY-MM-DD format
        """
        await ShowView().discord(pt_command, inter, "dd pt", ticker, raw, start)

    @dd.sub_command()
    async def est(
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays earning estimates [Business Insider]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(est_command, inter, "dd est", ticker)

    @dd.sub_command()
    async def sec(
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays sec filings [Market Watch]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(sec_command, inter, "dd sec", ticker)

    @dd.sub_command()
    async def supplier(
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays suppliers of the company [CSIMarket]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(supplier_command, inter, "dd supplier", ticker)

    @dd.sub_command()
    async def customer(
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays customers of the company [CSIMarket]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(customer_command, inter, "dd customer", ticker)

    @dd.sub_command()
    async def arktrades(
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        num: int = 10,
    ):
        """Displays trades made by ark [cathiesark.com]

        Parameters
        -----------
        ticker: Stock Ticker
        num: number of rows displayed
        """
        await ShowView().discord(arktrades_command, inter, "dd arktrades", ticker, num)


def setup(bot: commands.Bot):
    bot.add_cog(DueDiligenceCommands(bot))
