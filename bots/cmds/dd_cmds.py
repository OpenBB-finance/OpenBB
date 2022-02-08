from __future__ import annotations

import disnake
import pandas as pd
from disnake.ext import commands

from discordbot.config_discordbot import logger
from discordbot.stocks.due_diligence.analyst import analyst_command
from discordbot.stocks.due_diligence.arktrades import arktrades_command
from discordbot.stocks.due_diligence.customer import customer_command
from discordbot.stocks.due_diligence.est import est_command
from discordbot.stocks.due_diligence.pt import pt_command
from discordbot.stocks.due_diligence.sec import sec_command
from discordbot.stocks.due_diligence.supplier import supplier_command


def default_completion(inter: disnake.AppCmdInter) -> list[str]:
    return ["Start Typing", "If you want", "to", "Live"]


def ticker_autocomp(inter: disnake.AppCmdInter, ticker: str):
    if not ticker:
        return default_completion(inter)
    print(f"ticker_autocomp [ticker]: {ticker}")
    tlow = ticker.lower()
    col_list = ["Name"]
    df = pd.read_csv("files/tickers.csv", usecols=col_list)
    df = df["Name"]
    return [ticker for ticker in df if ticker.lower().startswith(tlow)][:24]


class DueDiligenceCommands(commands.Cog):
    """Due Diligence menu."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="dd-analyst")
    async def analyst(
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays analyst recommendations [Finviz]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("dd-analyst")
        await analyst_command(ctx, ticker)

    @commands.slash_command(name="dd-pt")
    async def pt(
        ctx: disnake.AppCmdInter,
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
        await ctx.response.defer()
        logger.info("dd-pt")
        await pt_command(ctx, ticker, raw, start)

    @commands.slash_command(name="dd-est")
    async def est(
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays earning estimates [Business Insider]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("dd-est")
        await est_command(ctx, ticker)

    @commands.slash_command(name="dd-sec")
    async def sec(
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays sec filings [Market Watch]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("dd-sec")
        await sec_command(ctx, ticker)

    @commands.slash_command(name="dd-supplier")
    async def supplier(
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays suppliers of the company [CSIMarket]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("dd-supplier")
        await supplier_command(ctx, ticker)

    @commands.slash_command(name="dd-customer")
    async def customer(
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays customers of the company [CSIMarket]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("dd-customer")
        await customer_command(ctx, ticker)

    @commands.slash_command(name="dd-arktrades")
    async def arktrades(
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        num: int = 10,
    ):
        """Displays trades made by ark [cathiesark.com]

        Parameters
        -----------
        ticker: Stock Ticker
        num: number of rows displayed
        """
        await ctx.response.defer()
        logger.info("dd-arktrades")
        await arktrades_command(ctx, ticker, num)


def setup(bot: commands.Bot):
    bot.add_cog(DueDiligenceCommands(bot))
