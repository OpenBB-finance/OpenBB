from __future__ import annotations

import disnake
import disnake.ext.commands as commands

from bots.helpers import ShowView, expiry_autocomp, ticker_autocomp
from bots.stocks.candle import candle_command
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


class SlashCommands(commands.Cog):
    def __init__(self, bot):
        super().__init__
        self.bot: commands.Bot = bot

    @commands.slash_command(name="opt")
    async def opt(self, inter):
        pass

    @opt.sub_command()
    async def chains(
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
            chain_command, inter, "opt chain", ticker, expiry, opt_type, min_sp, max_sp
        )

    @opt.sub_command(name="oi")
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
            oi_command, inter, "opt oi", ticker, expiry, min_sp, max_sp
        )

    @opt.sub_command(name="info")
    async def iv(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays option information (volatility, IV rank etc) [Barchart]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(iv_command, inter, "opt info", ticker)

    @commands.slash_command(name="quote")
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

    @opt.sub_command()
    async def unu(self, inter: disnake.AppCmdInter):
        """Unusual Options"""
        await ShowView().discord(unu_command, inter, "opt unu")

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

    @commands.slash_command(name="candle")
    async def cc(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        extended_hours: bool = False,
        start="",
        end="",
    ):
        """Display Candlestick Chart

        Parameters
        ----------
        ticker : Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        extended_hours: Display Pre/After Market Hours Default: False
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ShowView().discord(
            candle_command, inter, "candle", ticker, interval, past_days, extended_hours, start, end
        )

    @commands.slash_command(name="btc")
    async def btc(
        self,
        inter: disnake.AppCmdInter,
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        start="",
        end="",
    ):
        """Display Bitcoin Chart

        Parameters
        ----------
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
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
        past_days: int = 0,
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
        past_days: int = 0,
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

    @opt.sub_command()
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
            overview_command, inter, "opt overview", ticker, expiry, min_sp, max_sp
        )

    @opt.sub_command(name="vol")
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
        await ShowView().discord(vol_command, inter, "opt vol", ticker, expiry)

    @opt.sub_command()
    async def vsurf(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        z: str = commands.Param(
            choices={
                "Volatility": "IV",
                "Open Interest": "OI",
                "Last Price": "LP",
            }
        ),
    ):
        """Display Volatility Surface

        Parameters
        ----------
        ticker: Stock Ticker
        z: The variable for the Z axis
        """
        await ShowView().discord(vsurf_command, inter, "opt vsurf", ticker, z)

    @opt.sub_command(name="grhist")
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
            hist_command, inter, "opt grhist", ticker, expiry, strike, opt_type, greek
        )

    @opt.sub_command(name="hist")
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
            cc_hist_command, inter, "opt hist", ticker, expiry, strike, opt_type
        )


def setup(bot):
    bot.add_cog(SlashCommands(bot))
