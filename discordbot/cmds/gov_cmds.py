from __future__ import annotations

import disnake
import pandas as pd
from disnake.ext import commands

from discordbot.config_discordbot import logger
from discordbot.stocks.government.contracts import contracts_command
from discordbot.stocks.government.gtrades import gtrades_command
from discordbot.stocks.government.histcont import histcont_command
from discordbot.stocks.government.lastcontracts import lastcontracts_command
from discordbot.stocks.government.lasttrades import lasttrades_command
from discordbot.stocks.government.lobbying import lobbying_command
from discordbot.stocks.government.qtrcontracts import qtrcontracts_command
from discordbot.stocks.government.topbuys import topbuys_command
from discordbot.stocks.government.toplobbying import toplobbying_command
from discordbot.stocks.government.topsells import topsells_command


def default_completion(inter: disnake.AppCmdInter) -> list[str]:
    return ["Start Typing", "for a", "stock ticker"]


def ticker_autocomp(inter: disnake.AppCmdInter, ticker: str):
    if not ticker:
        return default_completion(inter)
    print(f"ticker_autocomp [ticker]: {ticker}")
    tlow = ticker.lower()
    col_list = ["Name"]
    df = pd.read_csv("files/tickers.csv", usecols=col_list)
    df = df["Name"]
    return [ticker for ticker in df if ticker.lower().startswith(tlow)][:24]


class GovernmentCommands(commands.Cog):
    """Government menu"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = None

    @commands.slash_command(name="gov-lasttrades")
    async def lasttrades(
        self,
        ctx: disnake.AppCmdInter,
        gov_type: str = commands.Param(choices=["congress", "senate", "house"]),
        past_days: int = 5,
        representative="",
    ):
        """Displays trades made by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        gov_type: Government Type
        past_days: Positive number of past transaction days
        representative: Enter name of a representative
        """
        await ctx.response.defer()
        logger.info("gov-lasttrades")
        await lasttrades_command(ctx, gov_type, past_days, representative)

    @commands.slash_command(name="gov-topbuys")
    async def topbuys(
        self,
        ctx: disnake.AppCmdInter,
        gov_type: str = commands.Param(choices=["congress", "senate", "house"]),
        past_transactions_months: int = 5,
        num: int = 20,
        raw: bool = False,
    ):
        """Displays most purchased stocks by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        gov_type: Government Type
        past_transactions_months: Positive number of past transaction months
        num: Number of most sold stocks to retrieve
        raw: If raw data should be outputted
        """
        await ctx.response.defer()
        logger.info("gov-topbuys")
        await topbuys_command(ctx, gov_type, past_transactions_months, num, raw)

    @commands.slash_command(name="gov-topsells")
    async def topsells(
        self,
        ctx: disnake.AppCmdInter,
        gov_type: str = commands.Param(choices=["congress", "senate", "house"]),
        past_transactions_months: int = 5,
        num: int = 10,
        raw: bool = False,
    ):
        """Displays most sold stocks by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        gov_type: Government Type
        past_transactions_months: Positive number of past transaction months
        num: Number of most sold stocks to retrieve
        raw: If raw data should be outputted
        """
        await ctx.response.defer()
        logger.info("gov-topsells")
        await topsells_command(ctx, gov_type, past_transactions_months, num, raw)

    @commands.slash_command(name="gov-lastcontracts")
    async def lastcontracts(
        self, ctx: disnake.AppCmdInter, past_transactions_days: int = 2, num: int = 20
    ):
        """Displays last government contracts [quiverquant.com]

        Parameters
        -----------
        past_transactions_days: Positive number of past transaction days
        num: Number of contracts
        """
        await ctx.response.defer()
        logger.info("gov-lastcontracts")
        await lastcontracts_command(ctx, past_transactions_days, num)

    @commands.slash_command(name="gov-qtrcontracts")
    async def qtrcontracts(
        self,
        ctx: disnake.AppCmdInter,
        num: int = 20,
        analysis: str = commands.Param(choices=["total", "upmom", "downmom"]),
    ):
        """Displays a look at government contracts [quiverquant.com]

        Parameters
        -----------
        analysis: Possible arguments: total, upmom & downmom
        num: Number of contracts
        """
        await ctx.response.defer()
        logger.info("gov-qtrcontracts")
        await qtrcontracts_command(ctx, num, analysis)

    @commands.slash_command(name="gov-toplobbying")
    async def toplobbying(
        self, ctx: disnake.AppCmdInter, num: int = 10, raw: bool = False
    ):
        """Displays top lobbying firms [quiverquant.com]

        Parameters
        -----------
        num: Number to show
        raw: If raw data should be outputted
        """
        await ctx.response.defer()
        logger.info("gov-toplobbying")
        await toplobbying_command(ctx, num, raw)

    @commands.slash_command(name="gov-gtrades")
    async def gtrades(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        gov_type: str = commands.Param(choices=["congress", "senate", "house"]),
        past_transactions_months: int = 10,
        raw: bool = False,
    ):
        """Displays government trades [quiverquant.com]

        Parameters
        -----------
        ticker: Stock Ticker
        gov_type: Government Type
        past_transactions_months: Positive number of past transaction months
        raw: If raw data should be outputted
        """
        await ctx.response.defer()
        logger.info("gov-gtrades")
        await gtrades_command(ctx, ticker, gov_type, past_transactions_months, raw)

    @commands.slash_command(name="gov-contracts")
    async def contracts(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        past_transaction_days: int = 10,
        raw: bool = False,
    ):
        """Displays contracts associated with tickers [quiverquant.com]

        Parameters
        -----------
        ticker: Stock Ticker
        past_transaction_days: Number of past transaction months
        raw: If raw data should be outputted
        """
        await ctx.response.defer()
        logger.info("gov-contracts")
        await contracts_command(ctx, ticker, past_transaction_days, raw)

    @commands.slash_command(name="gov-histcont")
    async def histcont(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays historical quarterly-contracts [quiverquant.com]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("gov-histcont")
        await histcont_command(ctx, ticker)

    @commands.slash_command(name="gov-lobbying")
    async def lobbying(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        num: int = 10,
    ):
        """Displays lobbying details [quiverquant.com]

        Parameters
        -----------
        ticker: Stock Ticker
        num: Number of events
        """
        await ctx.response.defer()
        logger.info("gov-lobbying")
        await lobbying_command(ctx, ticker, num)


def setup(bot: commands.Bot):
    bot.add_cog(GovernmentCommands(bot))
