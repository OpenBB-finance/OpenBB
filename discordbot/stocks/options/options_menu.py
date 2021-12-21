import asyncio

import discord
import discord_components

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

    @discord.ext.commands.command(name="stocks.opt.exp")
    async def expirations(self, ctx: discord.ext.commands.Context, ticker=""):
        """Get available expirations [yfinance]

        Parameters
        ----------
        ticker: str
            Stock ticker
        """
        await expirations_command(ctx, ticker)

    @discord.ext.commands.command(name="stocks.opt.calls")
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

    @discord.ext.commands.command(name="stocks.opt.puts")
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

    @discord.ext.commands.command(name="stocks.opt.oi")
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
    async def opt(self, ctx: discord.ext.commands.Context, ticker=""):
        """Stocks Context - Shows Options Menu"""
        if cfg.DEBUG:
            print(f"!stocks.opt {ticker}")
        cols_temp = []
        cols = []

        if ticker == "":
            embed = discord.Embed(
                title="ERROR Stocks: Options (opt) Menu",
                colour=cfg.COLOR,
                description="A stock ticker is required",
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

            await ctx.send(embed=embed)
            return

        text = (
            f"0️⃣ !stocks.opt.exp {ticker}\n"
            f"1️⃣ !stocks.opt.calls {ticker} <EXPIRATION> \n"
        )

        cols_temp.append(text)
        for col in cols_temp:
            cols.append(
                discord.Embed(
                    description=col,
                    colour=cfg.COLOR,
                    title="Stocks: Options (opt) Menu",
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

        emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣"]
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

                # pylint: disable=too-many-branches
                @gst_bot.event
                async def on_reaction_add(reaction, user):
                    if user == ctx.message.author and str(reaction.emoji) in emoji_list:
                        if reaction.emoji == "0️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 0")
                            if current == 0:
                                await expirations_command(ctx, ticker)
                        elif reaction.emoji == "1️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 1")
                            await calls_command(ctx, ticker)
                        elif reaction.emoji == "2️⃣️":
                            if cfg.DEBUG:
                                print("Reaction selected: 2")
                            await puts_command(ctx, ticker)
                        elif reaction.emoji == "3️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 3")
                            if current == 0:
                                await oi_command(ctx, ticker)

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
                embed = discord.Embed(
                    description="Error timeout - you snooze you lose! 😋",
                    colour=cfg.COLOR,
                    title="TIMEOUT Stocks: Options (opt) Menu",
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                await ctx.send(embed=embed)

                for emoji in emoji_list:
                    await main_message.remove_reaction(emoji, ctx.bot.user)
                break


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(OptionsCommands(bot))
