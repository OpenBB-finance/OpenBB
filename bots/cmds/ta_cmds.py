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
from bots.stocks.technical_analysis.fib import fib_command
from bots.stocks.technical_analysis.fisher import fisher_command
from bots.stocks.technical_analysis.kc import kc_command
from bots.stocks.technical_analysis.ma import ma_command
from bots.stocks.technical_analysis.macd import macd_command
from bots.stocks.technical_analysis.obv import obv_command
from bots.stocks.technical_analysis.recom import recom_command
from bots.stocks.technical_analysis.rsi import rsi_command
from bots.stocks.technical_analysis.stoch import stoch_command
from bots.stocks.technical_analysis.summary import summary_command
from bots.stocks.technical_analysis.view import view_command


class TechnicalAnalysisCommands(commands.Cog):
    """Technical Analysis menu."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="ta")
    async def ta(self, inter):
        pass

    @commands.slash_command(name="ta-mom")
    async def ta_mom(self, inter):
        pass

    @commands.slash_command(name="ta-vol")
    async def ta_vol(self, inter):
        pass

    @commands.slash_command(name="ta-vlt")
    async def ta_vlt(self, inter):
        pass

    @commands.slash_command(name="ta-trend")
    async def ta_trend(self, inter):
        pass

    @commands.slash_command(name="ta-ma")
    async def ma(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        ma_mode: str = commands.Param(choices=["ema", "sma", "wma", "hma", "zlma"]),
        window="",
        offset: int = 0,
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with selected moving average [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        ma_mode: mode of moving average.
        window: window length. Default: 20, 50
        offset: offset. Default: 0
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            ma_command,
            inter,
            "ta-ma",
            ticker,
            interval,
            past_days,
            ma_mode,
            window,
            offset,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_mom.sub_command()
    async def cci(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        length="14",
        scalar="0.015",
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with commodity channel index [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        length:  window length. Default: 14
        scalar: scalar. Default: 0.015
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            cci_command,
            inter,
            "ta-mom cci",
            ticker,
            interval,
            past_days,
            length,
            scalar,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_mom.sub_command()
    async def macd(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        fast="12",
        slow="26",
        signal="9",
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with moving average convergence/divergence [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        fast: fast period. Default: 12
        slow: slow period. Default: 26
        signal: signal period. Default: 9
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            macd_command,
            inter,
            "ta-mom macd",
            ticker,
            interval,
            past_days,
            fast,
            slow,
            signal,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_mom.sub_command()
    async def rsi(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        length="14",
        scalar="100",
        drift="1",
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with relative strength index [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        length: length. Default: 14
        scalar: scalar. Default: 100
        drift: drift. Default: 1
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            rsi_command,
            inter,
            "ta-mom rsi",
            ticker,
            interval,
            past_days,
            length,
            scalar,
            drift,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_mom.sub_command()
    async def stoch(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        fast_k="14",
        slow_d="3",
        slow_k="3",
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with stochastic relative strength average [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        fast_k: fast_k moving average period. Default: 14
        slow_d: slow_d moving average period. Default: 3
        slow_k: slow_k moving average period. Default: 3
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            stoch_command,
            inter,
            "ta-mom stoch",
            ticker,
            interval,
            past_days,
            fast_k,
            slow_d,
            slow_k,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_mom.sub_command()
    async def fisher(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        length="14",
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with fisher transformation [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        length: length. Default: 14
        scalar: scalar. Default: 100
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            fisher_command,
            inter,
            "ta-mom fisher",
            ticker,
            interval,
            past_days,
            length,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_mom.sub_command()
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
        await ShowView().discord(
            cg_command, inter, "ta-mom cg", ticker, length, start, end
        )

    @ta_trend.sub_command()
    async def adx(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        length="14",
        scalar="100",
        drift="1",
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with average directional movement index [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        length: length. Default: 14
        scalar: scalar. Default: 100
        drift: drift. Default: 1
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default : False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            adx_command,
            inter,
            "ta-trend adx",
            ticker,
            interval,
            past_days,
            length,
            scalar,
            drift,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_trend.sub_command()
    async def aroon(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        length="25",
        scalar="100",
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with aroon indicator [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        length: length. Default: 25
        scalar: scalar. Default: 100
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            aroon_command,
            inter,
            "ta-trend aroon",
            ticker,
            interval,
            past_days,
            length,
            scalar,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_vlt.sub_command()
    async def bbands(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        length="20",
        std: float = 2.0,
        ma_mode: str = commands.Param(choices=["ema", "sma", "wma", "hma", "zlma"]),
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with bollinger bands [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        length: length. Default: 5
        std: standard deviation. Default: 2.0
        ma_mode: mode of moving average.
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            bbands_command,
            inter,
            "ta-vlt bbands",
            ticker,
            interval,
            past_days,
            length,
            std,
            ma_mode,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_vlt.sub_command()
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
            "ta-vlt donchian",
            ticker,
            upper_length,
            lower_length,
            start,
            end,
        )

    # pylint: disable=too-many-arguments
    @ta_vlt.sub_command()
    async def kc(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        length="20",
        scalar="2",
        ma_mode: str = commands.Param(choices=["ema", "sma", "wma", "hma", "zlma"]),
        offset="0",
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with keltner channel [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        length: length. Default: 20
        scalar: scalar. Default: 2
        ma_mode: mode of moving average.
        offset: offset value. Default: 0
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        ma_mode = str(ma_mode)
        await ShowView().discord(
            kc_command,
            inter,
            "ta-vlt kc",
            ticker,
            interval,
            past_days,
            length,
            scalar,
            ma_mode,
            offset,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_vol.sub_command()
    async def ad(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        is_open="False",
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with accumulation/distribution line [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        is_open: whether open price is used. Default: False
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            ad_command,
            inter,
            "ta-vol ad",
            ticker,
            interval,
            past_days,
            is_open,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_vol.sub_command()
    async def adosc(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        is_open: bool = False,
        fast="3",
        slow="10",
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with chaikin oscillator [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        is_open: whether open price is used. Default: False
        fast: fast value. Default: 3
        slow: slow value. Default: 10
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            adosc_command,
            inter,
            "ta-vol adosc",
            ticker,
            interval,
            past_days,
            is_open,
            fast,
            slow,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta_vol.sub_command()
    async def obv(
        self,
        inter: disnake.AppCmdInter,
        ticker: str = commands.Param(autocomplete=ticker_autocomp),
        interval: int = commands.Param(choices=[1, 5, 15, 30, 60, 1440]),
        past_days: int = 0,
        start="",
        end="",
        extended_hours: bool = False,
        heikin_candles: bool = False,
    ):
        """Displays chart with on balance volume [Yahoo Finance]

        Parameters
        -----------
        ticker: Stock Ticker
        interval : Chart Minute Interval, 1440 for Daily
        past_days: Past Days to Display. Default: 0(Not for Daily)
        start: YYYY-MM-DD format
        end: YYYY-MM-DD format
        extended_hours: Display Pre/After Market Hours. Default: False
        heikin_candles: Heikin Ashi candles. Default: False
        """
        await ShowView().discord(
            obv_command,
            inter,
            "ta-vol obv",
            ticker,
            interval,
            past_days,
            start,
            end,
            extended_hours,
            heikin_candles,
        )

    @ta.sub_command()
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
        await ShowView().discord(fib_command, inter, "ta fib", ticker, start, end)

    @ta.sub_command()
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
        await ShowView().discord(view_command, inter, "ta view", ticker)

    @ta.sub_command()
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
        await ShowView().discord(summary_command, inter, "ta summary", ticker)

    @ta.sub_command()
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
        await ShowView().discord(recom_command, inter, "ta recom", ticker)


def setup(bot: commands.Bot):
    bot.add_cog(TechnicalAnalysisCommands(bot))
