from __future__ import annotations

import pickle
import time

import disnake
import disnake.ext.commands as commands
import pandas as pd

from discordbot.config_discordbot import logger
from discordbot.stocks.candle import candle_command
from discordbot.stocks.disc.ford import ford_command
from discordbot.stocks.insider.lins import lins_command
from discordbot.stocks.options.cc_hist import cc_hist_command
from discordbot.stocks.options.hist import hist_command
from discordbot.stocks.options.iv import iv_command
from discordbot.stocks.options.oi import oi_command
from discordbot.stocks.options.opt_chain import chain_command
from discordbot.stocks.options.overview import overview_command
from discordbot.stocks.options.unu import unu_command
from discordbot.stocks.options.vol import vol_command
from discordbot.stocks.options.vsurf import vsurf_command
from gamestonk_terminal.stocks.options import yfinance_model

startTime = time.time()
data = []


class Ticker:
    def __init__(self, ticker):
        super().__init__()
        global tickerr
        self._ticker = ticker
        tickerr = ticker

    @property
    def ticker(self):
        return self._ticker

    def __repr__(self) -> str:
        data.append(f"{self._ticker}")
        file = open("ticker", "wb")
        pickle.dump(data, file)
        file.close()
        return f"{self._ticker}"


def default_completion(inter: disnake.AppCmdInter) -> list[str]:
    return ["Start Typing", "for a", "stock ticker"]


def ticker_autocomp(inter: disnake.AppCmdInter, ticker: str):
    if not ticker:
        return default_completion(inter)
    if ticker:
        ticker = str(Ticker(ticker))
    print(f"ticker_autocomp [ticker]: {ticker}")
    tlow = ticker.lower()
    col_list = ["Name"]
    df = pd.read_csv("files/tickers.csv", usecols=col_list)
    df = df["Name"]
    return [ticker for ticker in df if ticker.lower().startswith(tlow)][:24]


def expiry_autocomp(inter: disnake.AppCmdInter, tickerr: str):
    file = open("ticker", "rb")
    data = pickle.load(file)
    file.close()
    print(data)
    dates = yfinance_model.option_expirations(data[-1])
    return [dates for dates in dates][:24]


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
        await inter.response.defer()
        logger.info("opt-chain")
        await chain_command(inter, ticker, expiry, opt_type, min_sp, max_sp)

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
        await inter.response.defer()
        logger.info("opt-oi")
        await oi_command(inter, ticker, expiry, min_sp, max_sp)

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
        await inter.response.defer()
        logger.info("opt-iv")
        await iv_command(inter, ticker)

    @commands.slash_command(name="disc-ford")
    async def ford(self, inter: disnake.AppCmdInter):
        """Display Orders by Fidelity Customers. [Fidelity]

        Parameters
        -----------
        num: Number of stocks to display
        """
        await inter.response.defer()
        logger.info("disc-ford")
        await ford_command(inter)

    @commands.slash_command(name="opt-unu")
    async def unu(self, inter: disnake.AppCmdInter):
        """Unusual Options"""
        await inter.response.defer()
        logger.info("disc-ford")
        await unu_command(inter)

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
        await inter.response.defer()
        logger.info("ins-last")
        await lins_command(inter, ticker, num)

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
        await inter.response.defer()
        logger.info("cc")
        await candle_command(inter, ticker, interval, past_days, start, end)

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
        await inter.response.defer()
        logger.info("btc")
        await candle_command(inter, "btc-usd", interval, past_days, start, end)

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
        await inter.response.defer()
        logger.info("eth")
        await candle_command(inter, "eth-usd", interval, past_days, start, end)

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
        await inter.response.defer()
        logger.info("sol")
        await candle_command(inter, "sol-usd", interval, past_days, start, end)

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
        await inter.response.defer()
        logger.info("opt-overview")
        await overview_command(inter, ticker, expiry, min_sp, max_sp)

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
        await inter.response.defer()
        logger.info("opt-vol")
        await vol_command(inter, ticker, expiry)

    @commands.slash_command(name="opt-vsurf")
    async def vsurf(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        z: str = commands.Param(choices=["Volatility", "Open Interest", "Last Price"]),
    ):
        """Display Volatility Surface

        Parameters
        ----------
        ticker: Stock Ticker
        z: The variable for the Z axis
        """
        await inter.response.defer()
        logger.info("opt-vsurf")

        if z == "Volatility":
            z = "IV"
        if z == "Open Interest":
            z = "OI"
        if z == "Last Price":
            z = "LP"

        await vsurf_command(inter, ticker, z)

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
        type: Calls or Puts
        greek: Greek variable to plot
        """
        await inter.response.defer()
        logger.info("opt-hist")
        await hist_command(inter, ticker, expiry, strike, opt_type, greek)

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
        type: Calls or Puts
        """
        await inter.response.defer()
        logger.info("opt-cc-hist")
        await cc_hist_command(inter, ticker, expiry, strike, opt_type)


def setup(bot):
    bot.add_cog(SlashCommands(bot))
    executionTime = time.time() - startTime
    print(f"> Extension {__name__} is ready: time in seconds: {str(executionTime)}\n")
