import asyncio
import discord
import discord_components
import config_discordbot as cfg
import helpers
from datetime import datetime, timedelta

from stocks.technical_analysis.ema import ema_command
from stocks.technical_analysis.sma import sma_command
from stocks.technical_analysis.wma import wma_command
from stocks.technical_analysis.hma import hma_command
from stocks.technical_analysis.zlma import zlma_command
from stocks.technical_analysis.cci import cci_command
from stocks.technical_analysis.macd import macd_command
from stocks.technical_analysis.rsi import rsi_command
from stocks.technical_analysis.stoch import stoch_command
from stocks.technical_analysis.fisher import fisher_command
from stocks.technical_analysis.cg import cg_command
from stocks.technical_analysis.adx import adx_command
from stocks.technical_analysis.aroon import aroon_command
from stocks.technical_analysis.bbands import bbands_command
from stocks.technical_analysis.donchian import donchian_command
from stocks.technical_analysis.kc import kc_command
from stocks.technical_analysis.ad import ad_command
from stocks.technical_analysis.adosc import adosc_command
from stocks.technical_analysis.obv import obv_command
from stocks.technical_analysis.fib import fib_command
from stocks.technical_analysis.view import view_command
from stocks.technical_analysis.summary import summary_command
from stocks.technical_analysis.recom import recom_command
from discordbot import gst_bot


class TechnicalAnalysisCommands(discord.ext.commands.Cog):
    """Technical Analysis menu."""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.ext.commands.command(name="stocks.ta.ema")
    async def ema(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        window="",
        offset="",
        start="",
        end="",
    ):
        """Displays chart with ema of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        window: int
            window length. Default: 20, 50
        offset: int
            offset. Default: 0
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await ema_command(ctx, ticker, window, offset, start, end)

    @discord.ext.commands.command(name="stocks.ta.sma")
    async def sma(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        window="",
        offset="",
        start="",
        end="",
    ):
        """Displays chart with sma of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        window: int
            window length. Default: 20, 50
        offset: int
            offset. Default: 0
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await sma_command(ctx, ticker, window, offset, start, end)

    @discord.ext.commands.command(name="stocks.ta.wma")
    async def wma(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        window="",
        offset="",
        start="",
        end="",
    ):
        """Displays chart with wma of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        window: int
            window length. Default: 20, 50
        offset: int
            offset. Default: 0
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await wma_command(ctx, ticker, window, offset, start, end)

    @discord.ext.commands.command(name="stocks.ta.hma")
    async def hma(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        window="",
        offset="",
        start="",
        end="",
    ):
        """Displays chart with hma of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        window: int
            window length. Default: 20, 50
        offset: int
            offset. Default: 0
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await hma_command(ctx, ticker, window, offset, start, end)

    @discord.ext.commands.command(name="stocks.ta.zlma")
    async def zlma(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        window="",
        offset="",
        start="",
        end="",
    ):
        """Displays chart with zlma of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        window: int
            window length. Default: 20
        offset: int
            offset. Default: 0
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await zlma_command(ctx, ticker, window, offset, start, end)

    @discord.ext.commands.command(name="stocks.ta.cci")
    async def cci(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        length="",
        scalar="",
        start="",
        end="",
    ):
        """Displays chart with cci of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        length: int
            window length. Default: 14
        scalar: int
            scalar. Default: 0.015
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await cci_command(ctx, ticker, length, scalar, start, end)

    @discord.ext.commands.command(name="stocks.ta.macd")
    async def macd(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        fast="",
        slow="",
        signal="",
        start="",
        end="",
    ):
        """Displays chart with macd of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        fast: int
            fast period. Default: 12
        slow: int
            slow period. Default: 26
        signal: int
            signal period. Default: 9
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await macd_command(ctx, ticker, fast, slow, signal, start, end)

    @discord.ext.commands.command(name="stocks.ta.rsi")
    async def rsi(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        length="",
        scalar="",
        drift="",
        start="",
        end="",
    ):
        """Displays chart with rsi of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        length: int
            length. Default: 14
        scalar: int
            scalar. Default: 100
        drift: int
            drift. Default: 1
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await rsi_command(ctx, ticker, length, scalar, drift, start, end)

    @discord.ext.commands.command(name="stocks.ta.stoch")
    async def stoch(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        fast_k="",
        slow_d="",
        slow_k="",
        start="",
        end="",
    ):
        """Displays chart with stoch of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        fast_k: int
            fast_k moving average period. Default: 14
        slow_d: int
            slow_d moving average period. Default: 3
        slow_k: int
            slow_k moving average period. Default: 3
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await stoch_command(ctx, ticker, fast_k, slow_d, slow_k, start, end)

    @discord.ext.commands.command(name="stocks.ta.fisher")
    async def fisher(
        self, ctx: discord.ext.commands.Context, ticker="", length="", start="", end=""
    ):
        """Displays chart with fisher of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        length: int
            length. Default: 14
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await fisher_command(ctx, ticker, length, start, end)

    @discord.ext.commands.command(name="stocks.ta.cg")
    async def cg(
        self, ctx: discord.ext.commands.Context, ticker="", length="", start="", end=""
    ):
        """Displays chart with cg of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        length: int
            length. Default: 14
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await cg_command(ctx, ticker, length, start, end)

    @discord.ext.commands.command(name="stocks.ta.adx")
    async def adx(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        length="",
        scalar="",
        drift="",
        start="",
        end="",
    ):
        """Displays chart with adx of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        length: int
            length. Default: 14
        scalar: int
            scalar. Default: 100
        drift: int
            drift. Default: 1
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await adx_command(ctx, ticker, length, scalar, drift, start, end)

    @discord.ext.commands.command(name="stocks.ta.aroon")
    async def aroon(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        length="",
        scalar="",
        start="",
        end="",
    ):
        """Displays chart with aroon of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        length: int
            length. Default: 25
        scalar: int
            scalar. Default: 100
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await aroon_command(ctx, ticker, length, scalar, start, end)

    @discord.ext.commands.command(name="stocks.ta.bbands")
    async def bbands(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        length="",
        std="",
        ma_mode="",
        start="",
        end="",
    ):
        """Displays chart with bbands of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        length: int
            length. Default: 5
        std: int
            standard deviation. Default: 2
        ma_mode: str
            mode of moving average. Default: sma
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await bbands_command(ctx, ticker, length, std, ma_mode, start, end)

    @discord.ext.commands.command(name="stocks.ta.donchian")
    async def donchian(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        upper_length="",
        lower_length="",
        start="",
        end="",
    ):
        """Displays chart with a donchian channel of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        upper_length: int
            length. Default: 25
        lower_length: int
            standard deviation. Default: 100
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await donchian_command(ctx, ticker, upper_length, lower_length, start, end)

    @discord.ext.commands.command(name="stocks.ta.kc")
    async def kc(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        length="",
        scalar="",
        ma_mode="",
        offset="",
        start="",
        end="",
    ):
        """Displays chart with kc of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        length: int
            length. Default: 20
        scalar: int
            scalar. Default: 2
        ma_mode: str
            mode of moving average. Default: sma
        offset: int
            offset value. Default: 0
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await kc_command(ctx, ticker, length, scalar, ma_mode, offset, start, end)

    @discord.ext.commands.command(name="stocks.ta.ad")
    async def ad(
        self, ctx: discord.ext.commands.Context, ticker="", open="", start="", end=""
    ):
        """Displays chart with ad of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        open: bool
            whether open price is used. Default: False
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await ad_command(ctx, ticker, open, start, end)

    @discord.ext.commands.command(name="stocks.ta.adosc")
    async def adosc(
        self,
        ctx: discord.ext.commands.Context,
        ticker="",
        open="",
        fast="",
        slow="",
        start="",
        end="",
    ):
        """Displays chart with adosc of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        open: bool
            whether open price is used. Default: False
        fast: int
            fast value. Default: 3
        slow: int
            slow value. Default: 10
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await adosc_command(ctx, ticker, open, fast, slow, start, end)

    @discord.ext.commands.command(name="stocks.ta.obv")
    async def obv(self, ctx: discord.ext.commands.Context, ticker="", start="", end=""):
        """Displays chart with obv of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await obv_command(ctx, ticker, start, end)

    @discord.ext.commands.command(name="stocks.ta.fib")
    async def fib(self, ctx: discord.ext.commands.Context, ticker="", start="", end=""):
        """Displays chart with fib of a given stock and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        start:
            date (in date format for start date)
        end:
            date (in date format for end date)
        """

        await fib_command(ctx, ticker, start, end)

    @discord.ext.commands.command(name="stocks.ta.view")
    async def view(self, ctx: discord.ext.commands.Context, ticker=""):
        """Displays an image of a given stocks data from Finviz and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        """

        await view_command(ctx, ticker)

    @discord.ext.commands.command(name="stocks.ta.summary")
    async def summary(self, ctx: discord.ext.commands.Context, ticker=""):
        """Displays a summary of a given stocks ta from FinBrain and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        """

        await summary_command(ctx, ticker)

    @discord.ext.commands.command(name="stocks.ta.recom")
    async def recom(self, ctx: discord.ext.commands.Context, ticker=""):
        """Displays a recommendation of a given stocks ta from Tradingview and sends it

        Parameters
        -----------
        ticker: str
            ticker, -h or help
        """

        await recom_command(ctx, ticker)

    @discord.ext.commands.command(name="stocks.ta")
    async def ta(self, ctx: discord.ext.commands.Context, ticker=""):
        """Stocks Context - Shows Technical Analysis Menu

        Returns
        -------
        Sends a message to the discord user with the commands from the stocks.ta context.
        The user can then select a reaction to trigger a command.
        """

        if cfg.DEBUG:
            print(f"!stocks.ta {ticker}")

        cols_temp = []
        cols = []

        if ticker != "":
            stock = helpers.load(ticker, datetime.now() - timedelta(days=365))
            if stock.empty:
                embed = discord.Embed(
                    title="ERROR Stocks: Dark Pool and Short data",
                    colour=cfg.COLOR,
                    description="Stock ticker is invalid",
                )
                embed.set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )

                await ctx.send(embed=embed)
                return
            text = (
                f"0️⃣ !stocks.ta.view {ticker}\n"
                f"1️⃣ !stocks.ta.summary {ticker}\n"
                f"2️⃣ !stocks.ta.recom {ticker}\n"
                f"3️⃣ !stocks.ta.ema {ticker} <WINDOW> <OFFSET> <START> <END>\n"
                f"4️⃣ !stocks.ta.sma {ticker} <WINDOW> <OFFSET> <START> <END>\n"
                f"5️⃣ !stocks.ta.wma {ticker} <WINDOW> <OFFSET> <START> <END>\n"
                f"6️⃣ !stocks.ta.hma {ticker} <WINDOW> <OFFSET> <START> <END>\n"
                f"7️⃣ !stocks.ta.zlma {ticker} <WINDOW> <OFFSET> <START> <END>\n"
                f"8️⃣ !stocks.ta.cci {ticker} <LENGTH> <SCALAR> <START> <END>\n"
                f"9️⃣ !stocks.ta.macd {ticker} <FAST> <SLOW> <SIGNAL> <START> <END>"
            )
            cols_temp.append(text)
            text = (
                f"0️⃣ !stocks.ta.rsi {ticker} <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
                f"1️⃣ !stocks.ta.stoch {ticker} <FAST_K> <SLOW_D> <SLOW_K> <START> <END>\n"
                f"2️⃣ !stocks.ta.fisher {ticker} <LENGTH> <START> <END>\n"
                f"3️⃣ !stocks.ta.cg {ticker} <LENGTH> <START> <END>\n"
                f"4️⃣ !stocks.ta.adx {ticker} <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
                f"5️⃣ !stocks.ta.aroon {ticker} <LENGTH> <SCALAR> <START> <END>\n"
                f"6️⃣ !stocks.ta.bbands {ticker} <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
                f"7️⃣ !stocks.ta.donchian {ticker} <LOWER_LENGTH> <UPPER_LENGTH> <START> <END>\n"
                f"8️⃣ !stocks.ta.kc {ticker} <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
                f"9️⃣ !stocks.ta.ad {ticker} <OPEN> <START> <END>"
            )
            cols_temp.append(text)
            text = (
                f"0️⃣ !stocks.ta.adosc {ticker} <OPEN> <FAST> <SLOW> <START> <END>\n"
                f"1️⃣ !stocks.ta.obv {ticker} <START> <END>\n"
                f"2️⃣ !stocks.ta.fib {ticker} <START> <END>\n"
            )
            cols_temp.append(text)
            for col in cols_temp:
                cols.append(
                    discord.Embed(
                        description=col,
                        colour=cfg.COLOR,
                        title="Technical Analysis (TA) Menu",
                    ).set_author(
                        name=cfg.AUTHOR_NAME,
                        icon_url=cfg.AUTHOR_ICON_URL,
                    )
                )

        else:
            text = (
                "\nAll commands aro only available when providing a ticker with:"
                "\n!stocks.ta <TICKER>"
            )
            cols.append(text)

        emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "9️⃣"]

        current = 0
        components = [
            [
                discord_components.Button(
                    label="Prev", id="back", style=discord_components.ButtonStyle.red
                ),
                discord_components.Button(
                    label=f"Page {int(cols.index(cols[current]))}/{len(cols) - 1}",
                    id="cur",
                    style=discord_components.ButtonStyle.green,
                    disabled=True,
                ),
                discord_components.Button(
                    label="Next", id="front", style=discord_components.ButtonStyle.green
                ),
            ]
        ]
        main_message = await ctx.send(embed=cols[current], components=components)
        for emoji in emoji_list:
            await main_message.add_reaction(emoji)

        try:

            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in emoji_list

            reaction, _ = await gst_bot.wait_for(
                "reaction_add", timeout=cfg.MENU_TIMEOUT, check=check
            )

            if reaction.emoji == "0️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 0")
                if current == 0:
                    await view_command(ctx, ticker)
                elif current == 1:
                    await rsi_command(ctx, ticker)
                elif current == 2:
                    await adosc_command(ctx, ticker)
            elif reaction.emoji == "1️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 1")
                if current == 0:
                    await summary_command(ctx, ticker)
                elif current == 1:
                    await stoch_command(ctx, ticker)
                elif current == 2:
                    await obv_command(ctx, ticker)
            elif reaction.emoji == "2️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 2")
                if current == 0:
                    await recom_command(ctx, ticker)
                elif current == 1:
                    await fisher_command(ctx, ticker)
                elif current == 2:
                    await fib_command(ctx, ticker)
            elif reaction.emoji == "3️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 3")
                if current == 0:
                    await ema_command(ctx, ticker)
                elif current == 1:
                    await cg_command(ctx, ticker)
            elif reaction.emoji == "4️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 4")
                if current == 0:
                    await sma_command(ctx, ticker)
                elif current == 1:
                    await adx_command(ctx, ticker)
            elif reaction.emoji == "5️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 5")
                if current == 0:
                    await wma_command(ctx, ticker)
                elif current == 1:
                    await aroon_command(ctx, ticker)
            elif reaction.emoji == "6️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 6")
                if current == 0:
                    await hma_command(ctx, ticker)
                elif current == 1:
                    await bbands_command(ctx, ticker)
            elif reaction.emoji == "7️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 7")
                if current == 0:
                    await zlma_command(ctx, ticker)
                elif current == 1:
                    await donchian_command(ctx, ticker)
            elif reaction.emoji == "8️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 8")
                if current == 0:
                    await cci_command(ctx, ticker)
                elif current == 1:
                    await kc_command(ctx, ticker)
            elif reaction.emoji == "9️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 9")
                if current == 0:
                    await macd_command(ctx, ticker)
                elif current == 1:
                    await ad_command(ctx, ticker)
        except asyncio.TimeoutError:
            text = text + "\n\nCOMMAND TIMEOUT."
            embed = discord.Embed(
                title="Technical Analysis (TA) Menu", description=text
            )
            await main_message.edit(embed=embed)
            for emoji in emoji_list:
                await main_message.remove_reaction(emoji, ctx.bot.user)
            components = [
                [
                    discord_components.Button(
                        label="Prev",
                        id="back",
                        style=discord_components.ButtonStyle.green,
                        disabled=True,
                    ),
                    discord_components.Button(
                        label=f"Page {int(cols.index(cols[current]))}/{len(cols) - 1}",
                        id="cur",
                        style=discord_components.ButtonStyle.grey,
                        disabled=True,
                    ),
                    discord_components.Button(
                        label="Next",
                        id="front",
                        style=discord_components.ButtonStyle.green,
                        disabled=True,
                    ),
                ]
            ]
            await main_message.edit(components=components)
            return

        while True:
            # Try and except blocks to catch timeout and break
            try:
                interaction = await gst_bot.wait_for(
                    "button_click",
                    check=lambda i: i.component.id
                    in ["back", "front"],  # You can add more
                    timeout=cfg.MENU_TIMEOUT,  # Some seconds of inactivity
                )

                # Getting the right list index
                if interaction.component.id == "back":
                    current -= 1
                elif interaction.component.id == "front":
                    current += 1

                # If its out of index, go back to start / end
                if current == len(cols):
                    current = 0
                elif current < 0:
                    current = len(cols) - 1

                # Edit to new page + the center counter changes
                components = [
                    [
                        discord_components.Button(
                            label="Prev",
                            id="back",
                            style=discord_components.ButtonStyle.red,
                        ),
                        discord_components.Button(
                            label=f"Page {int(cols.index(cols[current]))}/{len(cols) - 1}",
                            id="cur",
                            style=discord_components.ButtonStyle.green,
                            disabled=True,
                        ),
                        discord_components.Button(
                            label="Next",
                            id="front",
                            style=discord_components.ButtonStyle.green,
                        ),
                    ]
                ]
                await interaction.edit_origin(
                    embed=cols[current], components=components
                )

            except asyncio.TimeoutError:
                # Disable and get outta here
                components = [
                    [
                        discord_components.Button(
                            label="Prev",
                            id="back",
                            style=discord_components.ButtonStyle.green,
                            disabled=True,
                        ),
                        discord_components.Button(
                            label=f"Page {int(cols.index(cols[current]))}/{len(cols) - 1}",
                            id="cur",
                            style=discord_components.ButtonStyle.grey,
                            disabled=True,
                        ),
                        discord_components.Button(
                            label="Next",
                            id="front",
                            style=discord_components.ButtonStyle.green,
                            disabled=True,
                        ),
                    ]
                ]
                await main_message.edit(components=components)
                for emoji in emoji_list:
                    await main_message.remove_reaction(emoji, ctx.bot.user)
                break


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(TechnicalAnalysisCommands(bot))
