import asyncio

import discord

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_bot
from discordbot.stocks.options.calls import calls_command
from discordbot.stocks.options.expirations import expirations_command
from discordbot.stocks.options.oi import oi_command
from discordbot.stocks.options.puts import puts_command


class OptionsCommands(discord.ext.commands.Cog):
    """Dark Pool Shorts menu"""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

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
        name="stocks.opt.calls", usage="[ticker] [expiration]"
    )
    async def calls(
        self, ctx: discord.ext.commands.Context, ticker="", expiration: str = ""
    ):
        """Get call options for ticker and given expiration

        Parameters
        ----------
        ticker: str
            Stock ticker
        expiration: str
            Expiration date
        """
        await calls_command(ctx, ticker, expiration)

    @discord.ext.commands.command(name="stocks.opt.puts", usage="[ticker] [expiration]")
    async def puts(
        self, ctx: discord.ext.commands.Context, ticker="", expiration: str = ""
    ):
        """Get put options for ticker and given expiration

        Parameters
        ----------
        ticker: str
            Stock ticker
        expiration: str
            Expiration date
        """
        await puts_command(ctx, ticker, expiration)

    @discord.ext.commands.command(name="stocks.opt.oi", usage="[ticker] [expiration]")
    async def oi(
        self, ctx: discord.ext.commands.Context, ticker="", expiration: str = ""
    ):
        """Get put options for ticker and given expiration

        Parameters
        ----------
        ticker: str
            Stock ticker
        expiration: str
            Expiration date
        """
        await oi_command(ctx, ticker, expiration)

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
                    title="TIMEOUT Stocks: Government (GOV) Menu",
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                await ctx.send(embed=embed)


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(OptionsCommands(bot))
