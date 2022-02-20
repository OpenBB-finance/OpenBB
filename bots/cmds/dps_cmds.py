from __future__ import annotations

import disnake
from disnake.ext import commands

from bots.helpers import ShowView, ticker_autocomp
from bots.stocks.dark_pool_shorts.dpotc import dpotc_command
from bots.stocks.dark_pool_shorts.ftd import ftd_command
from bots.stocks.dark_pool_shorts.hsi import hsi_command
from bots.stocks.dark_pool_shorts.pos import pos_command
from bots.stocks.dark_pool_shorts.psi import psi_command
from bots.stocks.dark_pool_shorts.shorted import shorted_command
from bots.stocks.dark_pool_shorts.sidtc import sidtc_command
from bots.stocks.dark_pool_shorts.spos import spos_command

pos_choices = {
    "Short Vol (1M)": "sv",
    "Short Vol %": "sv_pct",
    "Net Short Vol (1M)": "nsv",
    "Net Short Vol ($100M)": "nsv_dollar",
    "DP Position (1M)": "dpp",
    "DP Position ($1B)": "dpp_dollar",
}


class DarkPoolShortsCommands(commands.Cog):
    """Dark Pool Shorts menu"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = None

    @commands.slash_command(name="dps-shorted")
    async def shorted(self, inter: disnake.AppCmdInter, num: int = 10):
        """Show most shorted stocks [Yahoo Finance]

        Parameters
        -----------
        num: Number of the most shorted stocks to retrieve
        """
        await ShowView().discord(shorted_command, inter, "dps-shorted", num)

    @commands.slash_command(name="dps-hsi")
    async def hsi(self, inter: disnake.AppCmdInter, num: int = 10):
        """Show top high short interest stocks of over 20% ratio [shortinterest.com]

        Parameters
        -----------
        num: Number of top stocks to print
        """
        await ShowView().discord(hsi_command, inter, "dps-hsi", num)

    @commands.slash_command(name="dps-pos")
    async def pos(
        self,
        inter: disnake.AppCmdInter,
        sort: str = commands.Param(choices=pos_choices),
        num: int = 10,
    ):
        """Dark pool short position [Stockgrid]

        Parameters
        -----------
        sort: Field for which to sort.
        num: Number of top tickers to show
        """
        await ShowView().discord(pos_command, inter, "dps-pos", sort, num)

    @commands.slash_command(name="dps-sidtc")
    async def sidtc(
        self,
        inter: disnake.AppCmdInter,
        sort: str = commands.Param(
            choices={
                "Float Short %": "float",
                "Days to Cover": "dtc",
                "Short Interest": "si",
            }
        ),
        num: int = 10,
    ):
        """Short interest and days to cover [Stockgrid]

        Parameters
        -----------
        sort: Field for which to sort. Possible are: `float`, `dtc`, `si`.
        num: Number of top tickers to show
        """
        await ShowView().discord(sidtc_command, inter, "dps-sidtc", sort, num)

    @commands.slash_command(name="dps-ftd")
    async def ftd(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(ftd_command, inter, "dps-ftd", ticker, start, end)

    @commands.slash_command(name="dps-dpotc")
    async def dpotc(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Dark pools (ATS) vs OTC data [FINRA]

        Parameters
        ----------
        ticker: Stock Ticker
        """
        await ShowView().discord(dpotc_command, inter, "dps-dpotc", ticker)

    @commands.slash_command(name="dps-spos")
    async def spos(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Net short vs position [Stockgrid]

        Parameters
        ----------
        ticker: Stock Ticker
        """
        await ShowView().discord(spos_command, inter, "dps-spos", ticker)

    @commands.slash_command(name="dps-psi")
    async def psi(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Price vs short interest volume [Stockgrid]

        Parameters
        ----------
        ticker: Stock Ticker
        """
        await ShowView().discord(psi_command, inter, "dps-psi", ticker)


def setup(bot: commands.Bot):
    bot.add_cog(DarkPoolShortsCommands(bot))
