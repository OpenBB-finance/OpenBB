# pylint: disable=W0612
from __future__ import annotations

import disnake
import pandas as pd
from disnake.ext import commands

from discordbot.config_discordbot import logger
from discordbot.stocks.technical_analysis.ad import ad_command
from discordbot.stocks.technical_analysis.adosc import adosc_command
from discordbot.stocks.technical_analysis.adx import adx_command
from discordbot.stocks.technical_analysis.aroon import aroon_command
from discordbot.stocks.technical_analysis.bbands import bbands_command
from discordbot.stocks.technical_analysis.cci import cci_command
from discordbot.stocks.technical_analysis.cg import cg_command
from discordbot.stocks.technical_analysis.donchian import donchian_command
from discordbot.stocks.technical_analysis.ema import ema_command
from discordbot.stocks.technical_analysis.fib import fib_command
from discordbot.stocks.technical_analysis.fisher import fisher_command
from discordbot.stocks.technical_analysis.hma import hma_command
from discordbot.stocks.technical_analysis.kc import kc_command
from discordbot.stocks.technical_analysis.macd import macd_command
from discordbot.stocks.technical_analysis.obv import obv_command
from discordbot.stocks.technical_analysis.recom import recom_command
from discordbot.stocks.technical_analysis.rsi import rsi_command
from discordbot.stocks.technical_analysis.sma import sma_command
from discordbot.stocks.technical_analysis.stoch import stoch_command
from discordbot.stocks.technical_analysis.summary import summary_command
from discordbot.stocks.technical_analysis.view import view_command
from discordbot.stocks.technical_analysis.wma import wma_command
from discordbot.stocks.technical_analysis.zlma import zlma_command

possible_ma = [
    "dema",
    "ema",
    "fwma",
    "hma",
    "linreg",
    "midpoint",
    "pwma",
    "rma",
    "sinwma",
    "sma",
    "swma",
    "t3",
    "tema",
    "trima",
    "vidya",
    "wma",
    "zlma",
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


class TechnicalAnalysisCommands(commands.Cog):
    """Technical Analysis menu."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="ta-ema")
    async def ema(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        window="",
        offset: int = 0,
        start="",
        end="",
    ):
        """Displays chart with exponential moving average [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        window: window length. Default: 20, 50
        offset: offset. Default: 0
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-ema")
        await ema_command(ctx, ticker, window, offset, start, end)

    @commands.slash_command(name="ta-sma")
    async def sma(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        window="",
        offset: int = 0,
        start="",
        end="",
    ):
        """Displays chart with simple moving average [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        window: window length. Default: 20, 50
        offset: offset. Default: 0
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-sma")
        await sma_command(ctx, ticker, window, offset, start, end)

    @commands.slash_command(name="ta-wma")
    async def wma(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        window="",
        offset: int = 0,
        start="",
        end="",
    ):
        """Displays chart with weighted moving average [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        window: window length. Default: 20, 50
        offset: offset. Default: 0
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-wma")
        await wma_command(ctx, ticker, window, offset, start, end)

    @commands.slash_command(name="ta-hma")
    async def hma(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        window="",
        offset: int = 0,
        start="",
        end="",
    ):
        """Displays chart with hull moving average [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        window: window length. Default: 20, 50
        offset: offset. Default: 0
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-hma")
        await hma_command(ctx, ticker, window, offset, start, end)

    @commands.slash_command(name="ta-zlma")
    async def zlma(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        window="",
        offset: int = 0,
        start="",
        end="",
    ):
        """Displays chart with zero lag moving average [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        window: window length. Default: 20
        offset: offset. Default: 0
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-zlma")
        await zlma_command(ctx, ticker, window, offset, start, end)

    @commands.slash_command(name="ta-cci")
    async def cci(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        length="14",
        scalar="0.015",
        start="",
        end="",
    ):
        """Displays chart with commodity channel index [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        length:  window length. Default: 14
        scalar: scalar. Default: 0.015
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-cci")
        await cci_command(ctx, ticker, length, scalar, start, end)

    @commands.slash_command(name="ta-macd")
    async def macd(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        fast="12",
        slow="26",
        signal="9",
        start="",
        end="",
    ):
        """Displays chart with moving average convergence/divergence [Yahoo Finance]

        Parameters
        -----------
        ticker:  Stock Ticker
        fast: fast period. Default: 12
        slow: slow period. Default: 26
        signal: signal period. Default: 9
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-macd")
        await macd_command(ctx, ticker, fast, slow, signal, start, end)

    @commands.slash_command(name="ta-rsi")
    async def rsi(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        length="14",
        scalar="100",
        drift="1",
        start="",
        end="",
    ):
        """Displays chart with relative strength index [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        length: length. Default: 14
        scalar: scalar. Default: 100
        drift: drift. Default: 1
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-rsi")
        await rsi_command(ctx, ticker, length, scalar, drift, start, end)

    @commands.slash_command(name="ta-stoch")
    async def stoch(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        fast_k="14",
        slow_d="3",
        slow_k="3",
        start="",
        end="",
    ):
        """Displays chart with stochastic relative strength average [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        fast_k: fast_k moving average period. Default: 14
        slow_d: slow_d moving average period. Default: 3
        slow_k: slow_k moving average period. Default: 3
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-stoch")
        await stoch_command(ctx, ticker, fast_k, slow_d, slow_k, start, end)

    @commands.slash_command(name="ta-fisher")
    async def fisher(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        length="14",
        start="",
        end="",
    ):
        """Displays chart with fisher transformation [Yahoo Finance]

        Parameters
        -----------
        ticker:  Stock Ticker
        length: length. Default: 14
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-fisher")
        await fisher_command(ctx, ticker, length, start, end)

    @commands.slash_command(name="ta-cg")
    async def cg(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        length="14",
        start="",
        end="",
    ):
        """Displays chart with centre of gravity [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker ticker
        length: length. Default: 14
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-cg")
        await cg_command(ctx, ticker, length, start, end)

    @commands.slash_command(name="ta-adx")
    async def adx(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        length="14",
        scalar="100",
        drift="1",
        start="",
        end="",
    ):
        """Displays chart with average directional movement index [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        length: length. Default: 14
        scalar: scalar. Default: 100
        drift: drift. Default: 1
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-adx")
        await adx_command(ctx, ticker, length, scalar, drift, start, end)

    @commands.slash_command(name="ta-aroon")
    async def aroon(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        length="25",
        scalar="100",
        start="",
        end="",
    ):
        """Displays chart with aroon indicator [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        length: length. Default: 25
        scalar: scalar. Default: 100
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-aroon")
        await aroon_command(ctx, ticker, length, scalar, start, end)

    @commands.slash_command(name="ta-bbands")
    async def bbands(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        length="5",
        std="2",
        ma_mode: str = commands.Param(choices=["ema", "sma", "wma", "hma", "zlma"]),
        start="",
        end="",
    ):
        """Displays chart with bollinger bands [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        length: length. Default: 5
        std: standard deviation. Default: 2
        ma_mode: mode of moving average.
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-bbands")
        ma_mode = str(ma_mode)
        await bbands_command(ctx, ticker, length, std, ma_mode, start, end)

    @commands.slash_command(name="ta-donchian")
    async def donchian(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        upper_length="25",
        lower_length="100",
        start="",
        end="",
    ):
        """Displays chart with donchian channel [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        upper_length: length. Default: 25
        lower_length: standard deviation. Default: 100
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-donchian")
        await donchian_command(ctx, ticker, upper_length, lower_length, start, end)

    # pylint: disable=too-many-arguments
    @commands.slash_command(name="ta-kc")
    async def kc(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        length="20",
        scalar="2",
        ma_mode: str = commands.Param(choices=["ema", "sma", "wma", "hma", "zlma"]),
        offset="0",
        start="",
        end="",
    ):
        """Displays chart with keltner channel [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        length: length. Default: 20
        scalar: scalar. Default: 2
        ma_mode: mode of moving average.
        offset: offset value. Default: 0
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-kc")
        ma_mode = str(ma_mode)
        await kc_command(ctx, ticker, length, scalar, ma_mode, offset, start, end)

    @commands.slash_command(name="ta-ad")
    async def ad(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        is_open="False",
        start="",
        end="",
    ):
        """Displays chart with accumulation/distribution line [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        is_open: whether open price is used. Default: False
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-ad")
        await ad_command(ctx, ticker, is_open, start, end)

    @commands.slash_command(name="ta-adosc")
    async def adosc(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        is_open="False",
        fast="3",
        slow="10",
        start="",
        end="",
    ):
        """Displays chart with chaikin oscillator [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        is_open: whether open price is used. Default: False
        fast: fast value. Default: 3
        slow: slow value. Default: 10
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-adosc")
        await adosc_command(ctx, ticker, is_open, fast, slow, start, end)

    @commands.slash_command(name="ta-obv")
    async def obv(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        start="",
        end="",
    ):
        """Displays chart with on balance volume [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        start: YYYY-MM-DD
        end: YYYY-MM-DD
        """
        await ctx.response.defer()
        logger.info("ta-obv")
        await obv_command(ctx, ticker, start, end)

    @commands.slash_command(name="ta-fib")
    async def fib(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        start="",
        end="",
    ):
        """Displays chart with fibonacci retracement [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("ta-fib")
        await fib_command(ctx, ticker, start, end)

    @commands.slash_command(name="ta-view")
    async def view(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays image from Finviz [Finviz]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("ta-view")
        await view_command(ctx, ticker)

    @commands.slash_command(name="ta-summary")
    async def summary(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays text of a given stocks ta summary [FinBrain API]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("ta-summary")
        await summary_command(ctx, ticker)

    @commands.slash_command(name="ta-recom")
    async def recom(
        self,
        ctx: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays text of a given stocks recommendation based on ta [Tradingview API]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ctx.response.defer()
        logger.info("ta-recom")
        await recom_command(ctx, ticker)


def setup(bot: commands.Bot):
    bot.add_cog(TechnicalAnalysisCommands(bot))
