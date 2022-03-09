from __future__ import annotations

import disnake
import disnake.ext.commands as commands

from bots.helpers import ShowView, expiry_autocomp, ticker_autocomp
from bots.stocks.candle import candle_command
from bots.stocks.disc.ford import ford_command
from bots.stocks.insider.lins import lins_command
from bots.stocks.options.cc_hist import cc_hist_command
from bots.stocks.options.hist import hist_command
from bots.stocks.options.iv import iv_command
from bots.stocks.options.oi import oi_command
from bots.stocks.options.opt_chain import chain_command
from bots.stocks.options.overview import overview_command
from bots.stocks.options.unu import unu_command
from bots.stocks.options.vol import vol_command
from bots.stocks.options.vsurf import vsurf_command
from bots.stocks.quote import quote_command
from bots.common import commands_dict


class SlashCommands(commands.Cog):
    def __init__(self, bot):
        super().__init__
        self.bot: commands.Bot = bot

    @commands.slash_command(name="opt-chain")
    async def opt_chain(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        expiry: str = commands.Param(autocomplete=expiry_autocomp),
        opt_type: str = commands.Param(choices=["Calls", "Puts"]),
        min_sp: float = None,
        max_sp: float = None,
    ):
        """Open Interest

        Parameters
        ----------
        ticker: Stock Ticker
        expiry: Expiration Date
        opt_type: Calls or Puts
        min_sp: Minimum Strike Price
        max_sp: Maximum Strike Price
        """
        await ShowView().discord(
            chain_command, inter, "opt-chain", ticker, expiry, opt_type, min_sp, max_sp
        )

    @commands.slash_command(name="opt-oi")
    async def open_interest(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        expiry: str = commands.Param(autocomplete=expiry_autocomp),
        min_sp: float = None,
        max_sp: float = None,
    ):
        """Open Interest

        Parameters
        ----------
        ticker: Stock Ticker
        expiry: Expiration Date
        min_sp: Minimum Strike Price
        max_sp: Maximum Strike Price
        """
        await ShowView().discord(
            oi_command, inter, "opt-oi", ticker, expiry, min_sp, max_sp
        )

    @commands.slash_command(name="opt-iv")
    async def iv(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays ticker options IV [Barchart]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(iv_command, inter, "opt-iv", ticker)

    @commands.slash_command(name="q")
    async def quote(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays ticker quote [yFinance]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(quote_command, inter, "quote", ticker)

    @commands.slash_command(name="disc-ford")
    async def ford(self, inter: disnake.AppCmdInter):
        """Display Orders by Fidelity Customers. [Fidelity]

        Parameters
        -----------
        num: Number of stocks to display
        """
        await ShowView().discord(ford_command, inter, "disc-ford")

    @commands.slash_command(name="opt-unu")
    async def unu(self, inter: disnake.AppCmdInter):
        """Unusual Options"""
        await ShowView().discord(unu_command, inter, "disc-ford")

    @commands.slash_command(name="ins-last")
    async def lins(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        num: int = 10,
    ):
        """Display insider activity for a given stock ticker. [Source: Finviz]

        Parameters
        ----------
        ticker : Stock Ticker
        num : Number of latest insider activity to display
        """
        await lins_command(inter, "ins-last", ticker, num)

    @commands.slash_command(name="cc")
    async def cc(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 1,
        start="",
        end="",
    ):
        """Display Candlestick Chart

        Parameters
        ----------
        ticker : Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ShowView().discord(
            candle_command, inter, "cc", ticker, interval, past_days, start, end
        )

    @commands.slash_command(name="btc")
    async def btc(
        self,
        inter: disnake.AppCmdInter,
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 1,
        start="",
        end="",
    ):
        """Display Bitcoin Chart

        Parameters
        ----------
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 1(Not for Daily)
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ShowView().discord(
            candle_command, inter, "btc", "btc-usd", interval, past_days, start, end
        )

    @commands.slash_command(name="eth")
    async def eth(
        self,
        inter: disnake.AppCmdInter,
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 1,
        start="",
        end="",
    ):
        """Display Ethereum Chart

        Parameters
        ----------
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 1(Not for Daily)
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ShowView().discord(
            candle_command, inter, "eth", "eth-usd", interval, past_days, start, end
        )

    @commands.slash_command(name="sol")
    async def sol(
        self,
        inter: disnake.AppCmdInter,
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 1,
        start="",
        end="",
    ):
        """Display Solana Chart

        Parameters
        ----------
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 1(Not for Daily)
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ShowView().discord(
            candle_command, inter, "sol", "sol-usd", interval, past_days, start, end
        )

    @commands.slash_command(name="opt-overview")
    async def overview(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        expiry: str = commands.Param(autocomplete=expiry_autocomp),
        min_sp: float = None,
        max_sp: float = None,
    ):
        """Options Overview

        Parameters
        ----------
        ticker: Stock Ticker
        expiry: Expiration Date
        min_sp: Minimum Strike Price
        max_sp: Maximum Strike Price
        """
        await ShowView().discord(
            overview_command, inter, "opt-overview", ticker, expiry, min_sp, max_sp
        )

    @commands.slash_command(name="opt-vol")
    async def volume(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        expiry: str = commands.Param(autocomplete=expiry_autocomp),
    ):
        """Options Volume

        Parameters
        ----------
        ticker: Stock Ticker
        expiry: Expiration Date
        """
        await ShowView().discord(vol_command, inter, "opt-vol", ticker, expiry)

    @commands.slash_command(name="opt-vsurf")
    async def vsurf(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        z: str = commands.Param(choices=commands_dict.options_vsurf_choices),
    ):
        """Display Volatility Surface

        Parameters
        ----------
        ticker: Stock Ticker
        z: The variable for the Z axis
        """
        await ShowView().discord(vsurf_command, inter, "opt-vsurf", ticker, z)

    @commands.slash_command(name="opt-hist")
    async def history(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        expiry: str = commands.Param(autocomplete=expiry_autocomp),
        strike: float = commands.Param(),
        opt_type: str = commands.Param(choices=["Calls", "Puts"]),
        greek: str = commands.Param(
            default="",
            choices=[
                "iv",
                "gamma",
                "delta",
                "theta",
                "rho",
                "vega",
            ],
        ),
    ):
        """Options Price History

        Parameters
        ----------
        ticker: Stock Ticker
        expiry: Expiration Date
        strike: Options Strike Price
        opt_type: Calls or Puts
        greek: Greek variable to plot
        """
        await ShowView().discord(
            hist_command, inter, "opt-hist", ticker, expiry, strike, opt_type, greek
        )

    @commands.slash_command(name="opt-cc-hist")
    async def cc_history(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        expiry: str = commands.Param(autocomplete=expiry_autocomp),
        strike: float = commands.Param(),
        opt_type: str = commands.Param(choices=["Calls", "Puts"]),
    ):
        """Options Price History

        Parameters
        ----------
        ticker: Stock Ticker
        expiry: Expiration Date
        strike: Options Strike Price
        opt_type: Calls or Puts
        """
        await ShowView().discord(
            cc_hist_command, inter, "opt-cc-hist", ticker, expiry, strike, opt_type
        )


def setup(bot):
    bot.add_cog(SlashCommands(bot))
