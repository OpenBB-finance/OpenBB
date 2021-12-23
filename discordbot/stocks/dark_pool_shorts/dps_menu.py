import asyncio
import discord
import yfinance as yf

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_bot

from discordbot.stocks.dark_pool_shorts.shorted import shorted_command
from discordbot.stocks.dark_pool_shorts.ftd import ftd_command
from discordbot.stocks.dark_pool_shorts.dpotc import dpotc_command
from discordbot.stocks.dark_pool_shorts.spos import spos_command
from discordbot.stocks.dark_pool_shorts.psi import psi_command
from discordbot.stocks.dark_pool_shorts.hsi import hsi_command
from discordbot.stocks.dark_pool_shorts.pos import pos_command
from discordbot.stocks.dark_pool_shorts.sidtc import sidtc_command


class DarkPoolShortsCommands(discord.ext.commands.Cog):
    """Dark Pool Shorts menu"""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = None

    @discord.ext.commands.command(
        name="stocks.dps.shorted",
        usage="[num]",
    )
    async def shorted(self, ctx: discord.ext.commands.Context, num="10"):
        """Show most shorted stocks [Yahoo Finance]

        Parameters
        -----------
        num: int
            Number of the most shorted stocks to retrieve
        """
        await shorted_command(ctx, num)

    @discord.ext.commands.command(
        name="stocks.dps.hsi",
        usage="[num]",
    )
    async def hsi(self, ctx: discord.ext.commands.Context, num="10"):
        """Show top high short interest stocks of over 20% ratio [shortinterest.com]

        Parameters
        -----------
        num: int
            Number of top stocks to print
        """
        await hsi_command(ctx, num)

    @discord.ext.commands.command(
        name="stocks.dps.pos",
        usage="[sort] [num]",
    )
    async def pos(self, ctx: discord.ext.commands.Context, sort="dpp_dollar", num="10"):
        """Dark pool short position [Stockgrid]

        Parameters
        -----------
        sort: str
            Field for which to sort. Possible are: `sv`, `sv_pct`, `nsv`, `nsv_dollar`,
            `dpp` and `dpp_dollar`.
            These correspond to Short Vol. (1M), Short Vol. %%, Net Short Vol. (1M),
            Net Short Vol. ($100M), DP Position (1M), DP Position ($1B), respectively.
        num: int
            Number of top tickers to show
        """
        await pos_command(ctx, sort, num)

    @discord.ext.commands.command(
        name="stocks.dps.sidtc",
        usage="[sort] [num]",
    )
    async def sidtc(self, ctx: discord.ext.commands.Context, sort="float", num="10"):
        """Short interest and days to cover [Stockgrid]

        Parameters
        -----------
        sort: str
            Field for which to sort. Possible are: `float`, `dtc`, `si`.
            These correspond to Float Short %%, Days to Cover, Short Interest, respectively.
        num: int
            Number of top tickers to show
        """
        await sidtc_command(ctx, sort, num)

    @discord.ext.commands.command(
        name="stocks.dps.ftd",
        usage="[ticker] [start] [end]",
    )
    async def ftd(self, ctx: discord.ext.commands.Context, ticker="", start="", end=""):
        """Fails-to-deliver data [SEC]

        Parameters
        ----------
        ticker: str
            Stock ticker
        start: datetime
            Starting date in YYYY-MM-DD format
        end: datetime
            Ending date in YYYY-MM-DD format
        """
        await ftd_command(ctx, ticker, start, end)

    @discord.ext.commands.command(
        name="stocks.dps.dpotc",
        usage=["ticker"],
    )
    async def dpotc(self, ctx: discord.ext.commands.Context, ticker=""):
        """Dark pools (ATS) vs OTC data [FINRA]

        Parameters
        ----------
        ticker: str
            Stock ticker
        """
        await dpotc_command(ctx, ticker)

    @discord.ext.commands.command(
        name="stocks.dps.spos",
        usage="[ticker]",
    )
    async def spos(self, ctx: discord.ext.commands.Context, ticker=""):
        """Net short vs position [Stockgrid]

        Parameters
        ----------
        ticker: str
            Stock ticker
        """
        await spos_command(ctx, ticker)

    @discord.ext.commands.command(
        name="stocks.dps.psi",
        usage="[ticker]",
    )
    async def psi(self, ctx: discord.ext.commands.Context, ticker=""):
        """Price vs short interest volume [Stockgrid]

        Parameters
        ----------
        ticker: str
            Stock ticker
        """
        await psi_command(ctx, ticker)

    @discord.ext.commands.command(
        name="stocks.dps",
        usage="[ticker]",
    )
    # pylint: disable=too-many-branches
    async def dark_pool_shorts_menu(self, ctx: discord.ext.commands.Context, ticker=""):
        """Stocks Context - Shows Dark Pool Shorts Menu

        Run `!help DarkPoolShortsCommands` to see the list of available commands.

        Returns
        -------
        Sends a message to the discord user with the commands from the dps context.
        The user can then select a reaction to trigger a command.
        """

        if cfg.DEBUG:
            print(f"\n!stocks.dps {ticker}")

        if ticker:
            stock = yf.download(ticker, progress=False)
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
            "0️⃣ !stocks.dps.shorted <NUM>\n"
            "1️⃣ !stocks.dps.hsi <NUM>\n"
            "2️⃣ !stocks.dps.pos <NUM> <SORT>\n"
            "3️⃣ !stocks.dps.sidtc <NUM> <SORT>\n"
        )
        if ticker:
            text += (
                f"4️⃣ !stocks.dps.ftd {ticker} <DATE_START> <DATE_END>\n"
                f"5️⃣ !stocks.dps.dpotc {ticker}\n"
                f"6️⃣ !stocks.dps.spos {ticker}\n"
                f"7️⃣ !stocks.dps.psi {ticker}\n"
            )
        else:
            text += (
                "\nMore commands available when providing a ticker with:"
                "\n!stocks.dps <TICKER>"
            )

        title = "Stocks: Dark Pool Shorts (DPS) Menu"
        embed = discord.Embed(title=title, description=text, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        msg = await ctx.send(embed=embed)

        emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣"]

        if ticker:
            emoji_list += ["4️⃣", "5️⃣", "6️⃣", "7️⃣"]

        for emoji in emoji_list:
            await msg.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in emoji_list

        try:
            reaction, _ = await gst_bot.wait_for(
                "reaction_add", timeout=cfg.MENU_TIMEOUT, check=check
            )
            if reaction.emoji == "0️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 0")
                await shorted_command(ctx)
            elif reaction.emoji == "1️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 1")
                await hsi_command(ctx)
            elif reaction.emoji == "2️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 2")
                await pos_command(ctx)
            elif reaction.emoji == "3️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 3")
                await sidtc_command(ctx)
            elif reaction.emoji == "4️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 4")
                await ftd_command(ctx, ticker)
            elif reaction.emoji == "5️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 5")
                await dpotc_command(ctx, ticker)
            elif reaction.emoji == "6️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 6")
                await spos_command(ctx, ticker)
            elif reaction.emoji == "7️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 7")
                await psi_command(ctx, ticker)

            for emoji in emoji_list:
                await msg.remove_reaction(emoji, ctx.bot.user)

        except asyncio.TimeoutError:
            for emoji in emoji_list:
                await msg.remove_reaction(emoji, ctx.bot.user)
            if cfg.DEBUG:
                embed = discord.Embed(
                    description="Error timeout - you snooze you lose! 😋",
                    colour=cfg.COLOR,
                    title="TIMEOUT Stocks: Dark Pool Shorts (DPS) Menu",
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                await ctx.send(embed=embed)


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(DarkPoolShortsCommands(bot))
