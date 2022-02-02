from __future__ import annotations

import disnake
import pandas as pd
from disnake.ext import commands

from discordbot.config_discordbot import logger
from discordbot.stocks.screener.financial import financial_command
from discordbot.stocks.screener.historical import historical_command
from discordbot.stocks.screener.overview import overview_command
from discordbot.stocks.screener.ownership import ownership_command
from discordbot.stocks.screener.performance import performance_command
from discordbot.stocks.screener.presets_custom import presets_custom_command
from discordbot.stocks.screener.presets_default import presets_default_command
from discordbot.stocks.screener.technical import technical_command
from discordbot.stocks.screener.valuation import valuation_command

presets_custom = [
    "potential_reversals",
    "golden_cross_penny",
    "rosenwald_gtfo",
    "golden_cross",
    "bull_runs_over_10pct",
    "recent_growth_and_support",
    "heavy_inst_ins",
    "short_squeeze_scan",
    "under_15dol_stocks",
    "top_performers_healthcare",
    "oversold_under_3dol",
    "value_stocks",
    "cheap_dividend",
    "death_cross",
    "top_performers_tech",
    "unusual_volume",
    "cheap_oversold",
    "undervalue",
    "high_vol_and_low_debt",
    "simplistic_momentum_scanner_under_7dol",
    "5pct_above_low",
    "growth_stocks",
    "cheap_bottom_dividend",
    "analyst_strong_buy",
    "oversold",
    "rosenwald",
    "weak_support_and_top_performers",
    "channel_up_and_low_debt_and_sma_50and200",
    "template",
    "modified_neff",
    "buffett_like",
    "oversold_under_5dol",
    "sexy_year",
    "news_scanner",
    "top_performers_all",
    "stocks_strong_support_levels",
    "continued_momentum_scan",
    "modified_dreman",
    "break_out_stocks",
]
signals = [
    "top_gainers",
    "top_losers",
    "new_high",
    "new_low",
    "most_volatile",
    "most_active",
    "unusual_volume",
    "overbought",
    "oversold",
    "downgrades",
    "upgrades",
    "earnings_before",
    "earnings_after",
    "recent_insider_buying",
    "recent_insider_selling",
    "major_news",
    "horizontal_sr",
    "tl_resistance",
    "tl_support",
    "wedge_up",
    "wedge_down",
    "wedge",
    "triangle_ascending",
    "triangle_descending",
    "channel_up",
    "channel_down",
    "channel",
    "double_top",
    "double_bottom",
    "multiple_top",
    "multiple_bottom",
    "head_shoulders",
    "head_shoulders_inverse",
]
sort = {
    "overview": [
        "Ticker",
        "Company",
        "Sector",
        "Industry",
        "Country",
        "Market Cap",
        "P/E",
        "Price",
        "Change",
        "Volume",
    ],
    "valuation": [
        "Ticker",
        "Market Cap",
        "P/E",
        "Fwd P/E",
        "PEG",
        "P/S",
        "P/B",
        "P/C",
        "P/FCF",
        "EPS this Y",
        "EPS next Y",
        "EPS past 5Y",
        "EPS next 5Y",
        "Sales past 5Y",
        "Price",
        "Change",
        "Volume",
    ],
    "financial": [
        "Ticker",
        "Market Cap",
        "Dividend",
        "ROA",
        "ROE",
        "ROI",
        "Curr R",
        "Quick R",
        "LTDebt/Eq",
        "Debt/Eq",
        "Gross M",
        "Oper M",
        "Profit M",
        "Earnings",
        "Price",
        "Change",
        "Volume",
    ],
    "ownership": [
        "Ticker",
        "Market Cap",
        "Outstanding",
        "Float",
        "Insider Own",
        "Insider Trans",
        "Inst Own",
        "Inst Trans",
        "Float Short",
        "Short Ratio",
        "Avg Volume",
        "Price",
        "Change",
        "Volume",
    ],
    "performance": [
        "Ticker",
        "Perf Week",
        "Perf Month",
        "Perf Quart",
        "Perf Half",
        "Perf Year",
        "Perf YTD",
        "Volatility W",
        "Volatility M",
        "Recom",
        "Avg Volume",
        "Rel Volume",
        "Price",
        "Change",
        "Volume",
    ],
    "technical": [
        "Ticker",
        "Beta",
        "ATR",
        "SMA20",
        "SMA50",
        "SMA200",
        "52W High",
        "52W Low",
        "RSI",
        "Price",
        "Change",
        "from Open",
        "Gap",
        "Volume",
    ],
}
# pylint: disable=R0912


def default_completion(inter: disnake.AppCmdInter) -> list[str]:
    return ["Start Typing", "for a", "stock ticker"]


def presets_custom_autocomp(inter: disnake.AppCmdInter, preset: str):
    df = presets_custom
    if not preset:
        return df[:24]
    plow = preset.lower()
    print(f"preset_custom_autocomp [preset]: {preset}")
    return [preset for preset in df if preset.lower().startswith(plow)][:24]


def signals_autocomp(inter: disnake.AppCmdInter, signal: str):
    df = signals
    if not signal:
        return df[:24]
    print(f"signal_autocomp [signal]: {signal}")
    slow = signal.lower()
    return [signal for signal in df if signal.lower().startswith(slow)][:24]


def ticker_autocomp(inter: disnake.AppCmdInter, ticker: str):
    if not ticker:
        return default_completion(inter)
    print(f"ticker_autocomp [ticker]: {ticker}")
    tlow = ticker.lower()
    col_list = ["Name"]
    df = pd.read_csv("files/tickers.csv", usecols=col_list)
    df = df["Name"]
    return [ticker for ticker in df if ticker.lower().startswith(tlow)][:24]


class ScreenerCommands(commands.Cog):
    """Screener menu"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="scr-presets_default")
    async def presets_default(self, ctx: disnake.AppCmdInter):
        """Displays every available preset"""
        logger.info("scr-presets_default")
        await presets_default_command(ctx)

    @commands.slash_command(name="scr-presets_custom")
    async def presets_custom(self, ctx: disnake.AppCmdInter):
        """Displays every available preset"""
        logger.info("scr-presets_custom")
        await presets_custom_command(ctx)

    @commands.slash_command(name="scr-historical")
    async def historical(
        self,
        ctx: disnake.AppCmdInter,
        signal: str = commands.Param(autocomplete=signals_autocomp),
        start="",
    ):
        """Displays trades made by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        signal: Signal. Default: most_volatile
        start: Starting date in YYYY-MM-DD format
        """
        await ctx.response.defer()
        logger.info("scr-historical")
        await historical_command(ctx, signal, start)

    @commands.slash_command(name="scr-overview")
    async def overview(
        self,
        ctx: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["overview"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays stocks with overview data such as Sector and Industry [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ctx.response.defer()
        logger.info("scr-overview")
        await overview_command(ctx, preset, sort, limit, ascend)

    @commands.slash_command(name="scr-valuation")
    async def valuation(
        self,
        ctx: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["valuation"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays results from chosen preset focusing on valuation metrics [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ctx.response.defer()
        logger.info("scr-valuation")
        await valuation_command(ctx, preset, sort, limit, ascend)

    @commands.slash_command(name="scr-financial")
    async def financial(
        self,
        ctx: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["financial"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays returned results from preset by financial metrics [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ctx.response.defer()
        logger.info("scr-financial")
        await financial_command(ctx, preset, sort, limit, ascend)

    @commands.slash_command(name="scr-ownership")
    async def ownership(
        self,
        ctx: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["ownership"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays stocks based on own share float and ownership data [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ctx.response.defer()
        logger.info("scr-ownership")
        await ownership_command(ctx, preset, sort, limit, ascend)

    @commands.slash_command(name="scr-performance")
    async def performance(
        self,
        ctx: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["performance"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays stocks and sort by performance categories [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ctx.response.defer()
        logger.info("scr-performance")
        await performance_command(ctx, preset, sort, limit, ascend)

    @commands.slash_command(name="scr-technical")
    async def technical(
        self,
        ctx: disnake.AppCmdInter,
        preset: str = commands.Param(autocomplete=presets_custom_autocomp),
        sort: str = commands.Param(choices=sort["technical"]),
        limit: int = 5,
        ascend: bool = False,
    ):
        """Displays stocks according to chosen preset, sorting by technical factors [Finviz]

        Parameters
        -----------
        preset: screener preset
        sort: column to sort by
        limit: number of stocks to display
        ascend: whether it's sorted by ascending order or not. Default: False
        """
        await ctx.response.defer()
        logger.info("scr-technical")
        await technical_command(ctx, preset, sort, limit, ascend)


def setup(bot: commands.Bot):
    bot.add_cog(ScreenerCommands(bot))
