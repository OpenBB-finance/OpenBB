# pylint: disable=W0612
from __future__ import annotations

import disnake
from disnake.ext import commands

from bots.helpers import ShowView, ticker_autocomp
from bots.stocks.technical_analysis.ad import ad_command
from bots.stocks.technical_analysis.adosc import adosc_command
from bots.stocks.technical_analysis.adx import adx_command
from bots.stocks.technical_analysis.aroon import aroon_command
from bots.stocks.technical_analysis.bbands import bbands_command
from bots.stocks.technical_analysis.cci import cci_command
from bots.stocks.technical_analysis.cg import cg_command
from bots.stocks.technical_analysis.donchian import donchian_command
from bots.stocks.technical_analysis.ema import ema_command
from bots.stocks.technical_analysis.fib import fib_command
from bots.stocks.technical_analysis.fisher import fisher_command
from bots.stocks.technical_analysis.hma import hma_command
from bots.stocks.technical_analysis.kc import kc_command
from bots.stocks.technical_analysis.macd import macd_command
from bots.stocks.technical_analysis.obv import obv_command
from bots.stocks.technical_analysis.recom import recom_command
from bots.stocks.technical_analysis.rsi import rsi_command
from bots.stocks.technical_analysis.sma import sma_command
from bots.stocks.technical_analysis.stoch import stoch_command
from bots.stocks.technical_analysis.summary import summary_command
from bots.stocks.technical_analysis.view import view_command
from bots.stocks.technical_analysis.wma import wma_command
from bots.stocks.technical_analysis.zlma import zlma_command


class TechnicalAnalysisCommands(commands.Cog):
    """Technical Analysis menu."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="ta-ema")
    async def ema(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            ema_command, inter, "ta-ema", ticker, window, offset, start, end
        )

    @commands.slash_command(name="ta-sma")
    async def sma(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            sma_command, inter, "ta-sma", ticker, window, offset, start, end
        )

    @commands.slash_command(name="ta-wma")
    async def wma(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            wma_command, inter, "ta-wma", ticker, window, offset, start, end
        )

    @commands.slash_command(name="ta-hma")
    async def hma(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            hma_command, inter, "ta-hma", ticker, window, offset, start, end
        )

    @commands.slash_command(name="ta-zlma")
    async def zlma(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            zlma_command, inter, "ta-zlma", ticker, window, offset, start, end
        )

    @commands.slash_command(name="ta-cci")
    async def cci(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            cci_command, inter, "ta-cci", ticker, length, scalar, start, end
        )

    @commands.slash_command(name="ta-macd")
    async def macd(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            macd_command, inter, "ta-macd", ticker, fast, slow, signal, start, end
        )

    @commands.slash_command(name="ta-rsi")
    async def rsi(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            rsi_command, inter, "ta-rsi", ticker, length, scalar, drift, start, end
        )

    @commands.slash_command(name="ta-stoch")
    async def stoch(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            stoch_command, inter, "ta-stoch", ticker, fast_k, slow_d, slow_k, start, end
        )

    @commands.slash_command(name="ta-fisher")
    async def fisher(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            fisher_command, inter, "ta-fisher", ticker, length, start, end
        )

    @commands.slash_command(name="ta-cg")
    async def cg(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(cg_command, inter, "ta-cg", ticker, length, start, end)

    @commands.slash_command(name="ta-adx")
    async def adx(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            adx_command, inter, "ta-adx", ticker, length, scalar, drift, start, end
        )

    @commands.slash_command(name="ta-aroon")
    async def aroon(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            aroon_command, inter, "ta-aroon", ticker, length, scalar, start, end
        )

    @commands.slash_command(name="ta-bbands")
    async def bbands(
        self,
        inter: disnake.AppCmdInter,
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
        ma_mode = str(ma_mode)
        await ShowView().discord(
            bbands_command, inter, "ta-bbands", ticker, length, std, ma_mode, start, end
        )

    @commands.slash_command(name="ta-donchian")
    async def donchian(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            donchian_command,
            inter,
            "ta-donchian",
            ticker,
            upper_length,
            lower_length,
            start,
            end,
        )

    # pylint: disable=too-many-arguments
    @commands.slash_command(name="ta-kc")
    async def kc(
        self,
        inter: disnake.AppCmdInter,
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
        ma_mode = str(ma_mode)
        await ShowView().discord(
            kc_command,
            inter,
            "ta-kc",
            ticker,
            length,
            scalar,
            ma_mode,
            offset,
            start,
            end,
        )

    @commands.slash_command(name="ta-ad")
    async def ad(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            ad_command, inter, "ta-ad", ticker, is_open, start, end
        )

    @commands.slash_command(name="ta-adosc")
    async def adosc(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(
            adosc_command, inter, "ta-adosc", ticker, is_open, fast, slow, start, end
        )

    @commands.slash_command(name="ta-obv")
    async def obv(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(obv_command, inter, "ta-obv", ticker, start, end)

    @commands.slash_command(name="ta-fib")
    async def fib(
        self,
        inter: disnake.AppCmdInter,
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
        await ShowView().discord(fib_command, inter, "ta-fib", ticker, start, end)

    @commands.slash_command(name="ta-view")
    async def view(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays image from Finviz [Finviz]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(view_command, inter, "ta-view", ticker)

    @commands.slash_command(name="ta-summary")
    async def summary(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays text of a given stocks ta summary [FinBrain API]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(summary_command, inter, "ta-summary", ticker)

    @commands.slash_command(name="ta-recom")
    async def recom(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
    ):
        """Displays text of a given stocks recommendation based on ta [Tradingview API]

        Parameters
        -----------
        ticker: Stock Ticker
        """
        await ShowView().discord(recom_command, inter, "ta-recom", ticker)


def setup(bot: commands.Bot):
    bot.add_cog(TechnicalAnalysisCommands(bot))
