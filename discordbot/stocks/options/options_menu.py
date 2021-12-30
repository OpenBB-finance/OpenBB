import asyncio
import discord

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_bot
from discordbot.reaction_helper import expiry_dates_reaction

from discordbot.stocks.options.calls import calls_command
from discordbot.stocks.options.expirations import expirations_command
from discordbot.stocks.options.hist import hist_command
from discordbot.stocks.options.iv import iv_command
from discordbot.stocks.options.oi import oi_command
from discordbot.stocks.options.puts import puts_command
from discordbot.stocks.options.unu import unu_command
from discordbot.stocks.options.vol import vol_command


class OptionsCommands(discord.ext.commands.Cog):
    """Options menu."""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.ext.commands.command(name="stocks.opt.iv", usage="[ticker]")
    async def iv(self, ctx: discord.ext.commands.Context, ticker: str = None):
        """Displays ticker options IV [Barchart]

        Parameters
        -----------
        ticker: str
            ticker,
        """
        async with ctx.typing():
            await asyncio.sleep(0.2)

            await iv_command(ctx, ticker)

    @discord.ext.commands.command(name="stocks.opt.unu", usage="[ticker]")
    async def unu(
        self,
        ctx: discord.ext.commands.Context,
        num: int = None,
    ):
        """Unusual Options

        Parameters
        -----------
        ticker: str
            ticker
        """
        async with ctx.typing():
            await asyncio.sleep(0.2)

            await unu_command(ctx, num)

    @discord.ext.commands.command(name="stocks.opt.exp", usage="[ticker]")
    async def expirations(self, ctx: discord.ext.commands.Context, ticker=""):
        """Get available expirations [yfinance]

        Parameters
        ----------
        ticker: str
            Stock ticker
        """
        await expirations_command(ctx, ticker)

    @discord.ext.commands.command(
        name="stocks.opt.calls",
        usage="[ticker] [expiration 0 - 9 (weeks out) or YYYY-MM-DD]",
    )
    async def calls(
        self, ctx: discord.ext.commands.Context, ticker: str = None, expiry: str = None
    ):
        """Get call options for ticker and given expiration

        Parameters
        ----------
        ticker: str
            Stock ticker
        expiry: str
            accepts 0-9 or YYYY-MM-DD
            0 weeklies, 1+ for weeks out
            prompts reaction helper if empty
        """
        async with ctx.typing():
            await asyncio.sleep(0.2)

            if cfg.DEBUG:
                print(f"!stocks.opt.calls {ticker} {expiry}")

            func_cmd = calls_command

            await expiry_dates_reaction(ctx, ticker, expiry, func_cmd)

    @discord.ext.commands.command(
        name="stocks.opt.puts",
        usage="[ticker] [expiration 0 - 9 (weeks out) or YYYY-MM-DD]",
    )
    async def puts(
        self, ctx: discord.ext.commands.Context, ticker: str = None, expiry: str = None
    ):
        """Get put options for ticker and given expiration

        Parameters
        ----------
        ticker: str
            Stock ticker
        expiry: str
            accepts 0-9 or YYYY-MM-DD
            0 weeklies, 1+ for weeks out
            prompts reaction helper if empty
        """
        async with ctx.typing():
            await asyncio.sleep(0.2)

            if cfg.DEBUG:
                print(f"!stocks.opt.puts {ticker} {expiry}")

            func_cmd = puts_command

            await expiry_dates_reaction(ctx, ticker, expiry, func_cmd)

    @discord.ext.commands.command(
        name="stocks.opt.oi",
        usage="[ticker] [expiration 0 - 9 (weeks out) or YYYY-MM-DD] [min strike] [max strike]",
    )
    async def oi(
        self,
        ctx: discord.ext.commands.Context,
        ticker: str = None,
        expiry: str = None,
        min_sp: float = None,
        max_sp: float = None,
    ):
        """Display options open interest for ticker and given expiration [Max Pain]

        Parameters
        -----------
        ticker: str
            ticker
        strike: float
            strike
        expiry: str
            accepts 0-9 or YYYY-MM-DD
        min_sp: float
            min strike price
        max_sp:float
            max strike price

        Sends a message to the discord user with the expiry dates if empty.
        The user can then select a reaction to trigger the selected date.
        """
        async with ctx.typing():
            await asyncio.sleep(0.2)

            if cfg.DEBUG:
                print(f"!stocks.opt.oi {ticker} {expiry} {min_sp} {max_sp}")

            call_arg = (min_sp, max_sp)
            func_cmd = oi_command

            await expiry_dates_reaction(ctx, ticker, expiry, func_cmd, call_arg)

    @discord.ext.commands.command(
        name="stocks.opt.hist",
        usage="[ticker] [strike] [c or p (call/put)] [expiration 0 - 9 (weeks out) or YYYY-MM-DD]",
    )
    async def hist(
        self,
        ctx: discord.ext.commands.Context,
        ticker: str = None,
        strike: float = None,
        put="",
        expiry: str = None,
    ):
        """Display chart of given option historical price [Tradier]

        Parameters
        -----------
        ticker: str
            ticker
        strike: float
            strike
        put: bool
            c for call
            p for put
        expiry: str
            accepts 0-9 or YYYY-MM-DD

        Sends a message to the discord user with the expiry dates if empty.
        The user can then select a reaction to trigger the selected date.
        """
        async with ctx.typing():
            await asyncio.sleep(0.2)

            if cfg.DEBUG:
                print(f"!stocks.opt.hist {ticker} {strike} {put} {expiry}")

            if strike is None or put == "":
                embed = discord.Embed(
                    title="ERROR Options: History",
                    colour=cfg.COLOR,
                    description='A strike and c/p is required\n```bash\n"!stocks.opt.hist {ticker} {strike} {c/p}"```',
                )

                await ctx.send(embed=embed)
                return

            if put == "p":
                put = bool(True)
            if put == "c":
                put = bool(False)

            call_arg = (
                strike,
                put,
            )
            func_cmd = hist_command

            await expiry_dates_reaction(ctx, ticker, expiry, func_cmd, call_arg)

    @discord.ext.commands.command(
        name="stocks.opt.vol",
        usage="[ticker] [expiration 0 - 9 (weeks out) or YYYY-MM-DD] [min strike] [max strike]",
    )
    async def vol(
        self,
        ctx: discord.ext.commands.Context,
        ticker: str = None,
        expiry: str = None,
        min_sp: float = None,
        max_sp: float = None,
    ):
        """Display options volume for ticker and given expiration

        Parameters
        -----------
        ticker: str
            ticker
        strike: float
            strike
        expiry: str
            accepts 0-9 or YYYY-MM-DD
        min_sp: float
            min strike price
        max_sp:float
            max strike price

        Sends a message to the discord user with the expiry dates if empty.
        The user can then select a reaction to trigger the selected date.
        """
        async with ctx.typing():
            await asyncio.sleep(0.2)

            if cfg.DEBUG:
                print(f"!stocks.opt.vol {ticker} {expiry} {min_sp} {max_sp}")

            call_arg = (min_sp, max_sp)
            func_cmd = vol_command

            await expiry_dates_reaction(ctx, ticker, expiry, func_cmd, call_arg)

    @discord.ext.commands.command(name="stocks.opt")
    async def opt(self, ctx: discord.ext.commands.Context, ticker="", expiration=""):
        """Stocks Context - Shows Options Menu

        Run `!help OptionsCommands` to see the list of available commands.

        Returns
        -------
        Sends a message to the discord user with the commands from the stocks/options context.
        The user can then select a reaction to trigger a command.
        """

        if cfg.DEBUG:
            print(f"!stocks.opt {ticker}")

        if not ticker:
            embed = discord.Embed(
                description="Provide a ticker and expiration date with this menu, e.g. !stocks.opt TSLA 2021-06-04",
                colour=cfg.COLOR,
                title="ERROR Stocks: Options Menu",
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            await ctx.send(embed=embed)
            return

        if expiration:
            text = (
                f"0️⃣ !stocks.opt.exp {ticker}\n"
                f"1️⃣ !stocks.opt.calls {ticker} {expiration} \n"
                f"2️⃣ !stocks.opt.puts {ticker} {expiration} \n"
                f"3️⃣ !stocks.opt.oi {ticker} {expiration} \n"
            )
        else:
            text = f"0️⃣ !stocks.opt.exp {ticker}\n"

        title = "Stocks: Options Menu"
        embed = discord.Embed(title=title, description=text, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        msg = await ctx.send(embed=embed)

        if expiration:
            emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣"]
        else:
            emoji_list = ["0️⃣"]

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
                await expirations_command(ctx, ticker)
            elif reaction.emoji == "1️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 1")
                await calls_command(ctx, ticker, expiration)
            elif reaction.emoji == "2️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 2")
                await puts_command(ctx, ticker, expiration)
            elif reaction.emoji == "3️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 3")
                await oi_command(ctx, ticker, expiration)

            for emoji in emoji_list:
                await msg.remove_reaction(emoji, ctx.bot.user)

        except asyncio.TimeoutError:
            for emoji in emoji_list:
                await msg.remove_reaction(emoji, ctx.bot.user)
            if cfg.DEBUG:
                embed = discord.Embed(
                    description="Error timeout - you snooze you lose! 😋",
                    colour=cfg.COLOR,
                    title="TIMEOUT Stocks: Options Menu",
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                await ctx.send(embed=embed)


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(OptionsCommands(bot))
