from __future__ import annotations

import disnake
import pandas as pd
from disnake.ext import commands

from discordbot.config_discordbot import logger
from discordbot.stocks.dark_pool_shorts.dpotc import dpotc_command
from discordbot.stocks.dark_pool_shorts.ftd import ftd_command
from discordbot.stocks.dark_pool_shorts.hsi import hsi_command
from discordbot.stocks.dark_pool_shorts.pos import pos_command
from discordbot.stocks.dark_pool_shorts.psi import psi_command
from discordbot.stocks.dark_pool_shorts.shorted import shorted_command
from discordbot.stocks.dark_pool_shorts.sidtc import sidtc_command
from discordbot.stocks.dark_pool_shorts.spos import spos_command

pos_choices = [
    "Short Vol (1M)",
    "Short Vol %",
    "Net Short Vol (1M)",
    "Net Short Vol ($100M)",
    "DP Position (1M)",
    "DP Position ($1B)",
]


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


class DarkPoolShortsCommands(commands.Cog):
    """Dark Pool Shorts menu"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = None

    @commands.slash_command(name="dps-shorted")
    async def shorted(self, ctx: disnake.AppCmdInter, num: int = 10):
        """Show most shorted stocks [Yahoo Finance]

        Parameters
        -----------
        num: Number of the most shorted stocks to retrieve
        """
        await ctx.response.defer()
        logger.info("dps-shorted")
        await shorted_command(ctx, num)

    @commands.slash_command(name="dps-hsi")
    async def hsi(self, ctx: disnake.AppCmdInter, num: int = 10):
        """Show top high short interest stocks of over 20% ratio [shortinterest.com]

        Parameters
        -----------
        num: Number of top stocks to print
        """
        await ctx.response.defer()
        logger.info("dps-hsi")
        await hsi_command(ctx, num)

    @commands.slash_command(name="dps-pos")
    async def pos(
        self,
        ctx: disnake.AppCmdInter,
        sort: str = commands.Param(choices=pos_choices),
        num: int = 10,
    ):
        """Dark pool short position [Stockgrid]

        Parameters
        -----------
        sort: Field for which to sort.
        num: Number of top tickers to show
        """
        await ctx.response.defer()
        logger.info("dps-pos")

        if str(sort) == "Short Vol (1M)":
            sort = "sv"
        if str(sort) == "Short Vol %":
            sort = "sv_pct"
        if str(sort) == "Net Short Vol (1M)":
            sort = "nsv"
        if str(sort) == "Net Short Vol ($100M)":
            sort = "nsv_dollar"
        if str(sort) == "DP Position (1M)":
            sort = "dpp"
        if str(sort) == "DP Position ($1B)":
            sort = "dpp_dollar"

        await pos_command(ctx, sort, num)

    @commands.slash_command(name="dps-sidtc")
    async def sidtc(
        self,
        ctx: disnake.AppCmdInter,
        sort: str = commands.Param(
            choices=["Float Short %", "Days to Cover", "Short Interest"]
        ),
        num: int = 10,
    ):
        """Short interest and days to cover [Stockgrid]

        Parameters
        -----------
        sort: Field for which to sort. Possible are: `float`, `dtc`, `si`.
        num: Number of top tickers to show
        """
        await ctx.response.defer()
        logger.info("dps-sidtc")

        if str(sort) == "Float Short %":
            sort = "float"
        if str(sort) == "Days to Cover":
            sort = "dtc"
        if str(sort) == "Short Interest":
            sort = "si"

        await sidtc_command(ctx, sort, num)

    @commands.slash_command(name="dps-ftd")
    async def ftd(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        start="",
        end="",
    ):
        """Fails-to-deliver data [SEC]

        Parameters
        ----------
        ticker: Stock Ticker
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("dps-ftd")
        await ftd_command(ctx, ticker, start, end)

    @commands.slash_command(name="dps-dpotc")
    async def dpotc(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Dark pools (ATS) vs OTC data [FINRA]

        Parameters
        ----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("dps-dpotc")
        await dpotc_command(ctx, ticker)

    @commands.slash_command(name="dps-spos")
    async def spos(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Net short vs position [Stockgrid]

        Parameters
        ----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("dps-spos")
        await spos_command(ctx, ticker)

    @commands.slash_command(name="dps-psi")
    async def psi(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Price vs short interest volume [Stockgrid]

        Parameters
        ----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("dps-psi")
        await psi_command(ctx, ticker)


def setup(bot: commands.Bot):
    bot.add_cog(DarkPoolShortsCommands(bot))
