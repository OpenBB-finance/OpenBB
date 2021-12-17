import asyncio
import discord
import discord_components

import discordbot.config_discordbot as cfg

from discordbot.run_discordbot import gst_bot

from discordbot.economy.feargreed import feargreed_command
from discordbot.economy.overview import overview_command
from discordbot.economy.indices import indices_command
from discordbot.economy.futures import futures_command
from discordbot.economy.usbonds import usbonds_command
from discordbot.economy.glbonds import glbonds_command
from discordbot.economy.currencies import currencies_command
from discordbot.economy.energy import energy_command
from discordbot.economy.metals import metals_command
from discordbot.economy.grains import grains_command
from discordbot.economy.meats import meats_command
from discordbot.economy.softs import softs_command
from discordbot.economy.valuation import valuation_command
from discordbot.economy.performance import performance_command


class EconomyCommands(discord.ext.commands.Cog):
    """Economy Commands menu"""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.ext.commands.command(name="economy.feargreed")
    async def feargreed(self, ctx: discord.ext.commands.Context, indicator=""):
        """CNN Fear and Greed Index [CNN]

        Parameters
        -----------
        indicator: str
            Possible indicatores are: jbd, mv, pco, mm, sps, spb, shd. Which stand for
            Junk Bond Demand, Market Volatility, Put and Call Options, Market Momentum,
            Stock Price Strength, Stock Price Breadth, Safe Heaven Demand.
        """
        await feargreed_command(ctx, indicator)

    @discord.ext.commands.command(name="economy.overview")
    async def overview(self, ctx: discord.ext.commands.Context):
        """Market data overview [Wall St. Journal]"""
        await overview_command(ctx)

    @discord.ext.commands.command(name="economy.indices")
    async def indices(self, ctx: discord.ext.commands.Context):
        """US indices overview [Wall St. Journal]"""
        await indices_command(ctx)

    @discord.ext.commands.command(name="economy.futures")
    async def futures(self, ctx: discord.ext.commands.Context):
        """Futures and commodities overview [Wall St. Journal]"""
        await futures_command(ctx)

    @discord.ext.commands.command(name="economy.usbonds")
    async def usbonds(self, ctx: discord.ext.commands.Context):
        """US bonds overview [Wall St. Journal]"""
        await usbonds_command(ctx)

    @discord.ext.commands.command(name="economy.glbonds")
    async def glbonds(self, ctx: discord.ext.commands.Context):
        """Global bonds overview [Wall St. Journal]"""
        await glbonds_command(ctx)

    @discord.ext.commands.command(name="economy.energy")
    async def energy(self, ctx: discord.ext.commands.Context):
        """Displays energy futures data [Finviz]"""
        await energy_command(ctx)

    @discord.ext.commands.command(name="economy.metals")
    async def metals(self, ctx: discord.ext.commands.Context):
        """Displays metals futures data [Finviz]"""
        await metals_command(ctx)

    @discord.ext.commands.command(name="economy.meats")
    async def meats(self, ctx: discord.ext.commands.Context):
        """Displays meats futures data [Finviz]"""
        await meats_command(ctx)

    @discord.ext.commands.command(name="economy.grains")
    async def grains(self, ctx: discord.ext.commands.Context):
        """Displays grains futures data [Finviz]"""
        await grains_command(ctx)

    @discord.ext.commands.command(name="economy.softs")
    async def softs(self, ctx: discord.ext.commands.Context):
        """Displays softs futures data [Finviz]"""
        await softs_command(ctx)

    @discord.ext.commands.command(name="economy.currencies")
    async def currencies(self, ctx: discord.ext.commands.Context):
        """Currencies overview [Wall St. Journal]"""
        await currencies_command(ctx)

    @discord.ext.commands.command(name="economy.valuation")
    async def valuation(self, ctx: discord.ext.commands.Context, economy_group=""):
        """Valuation of sectors, industry, country [Finviz]

        Parameters
        -----------
        economy_group: str
            Possible groups are: sector, industry, basic_materials, communication_services,
            consumer_cyclical, consumer_defensive, energy, financial, healthcare, industrials,
            real_estate, technology, utilities, country, capitalization.
        """
        await valuation_command(ctx, economy_group)

    @discord.ext.commands.command(name="economy.performance")
    async def performance(self, ctx: discord.ext.commands.Context, economy_group=""):
        """Performance of sectors, industry, country [Finviz]

        Parameters
        -----------
        economy_group: str
            Possible groups are: sector, industry, basic_materials, communication_services,
            consumer_cyclical, consumer_defensive, energy, financial, healthcare, industrials,
            real_estate, technology, utilities, country, capitalization.
        """
        await performance_command(ctx, economy_group)

    @discord.ext.commands.command(name="economy")
    async def economy(self, ctx: discord.ext.commands.Context):
        """Economy Context Menu

        Returns
        -------
        Sends a message to the discord user with the commands from the economy context.
        The user can then select a reaction to trigger a command.
        """

        if cfg.DEBUG:
            print("!economy")

        cols_temp = []
        cols = []

        text = (
            "0️⃣ !economy.overview\n"
            "1️⃣ !economy.futures\n"
            "2️⃣ !economy.usbonds\n"
            "3️⃣ !economy.glbonds\n"
            "4️⃣ !economy.indices\n"
            "5️⃣ !economy.currencies\n"
            "6️⃣ !economy.feargreed\n"
            "7️⃣ !economy.valuation <GROUP>\n"
            "8️⃣ !economy.performance <GROUP>\n"
            "9️⃣ !economy.energy"
        )
        cols_temp.append(text)
        text = (
            "0️⃣ !economy.metals\n"
            "1️⃣ !economy.meats\n"
            "2️⃣ !economy.grains\n"
            "3️⃣ !economy.softs"
        )
        cols_temp.append(text)
        for col in cols_temp:
            cols.append(
                discord.Embed(
                    description=col,
                    colour=cfg.COLOR,
                    title="Economy Menu",
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

        emoji_list = [
            "0️⃣",
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
        ]

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
                                await overview_command(ctx)
                            elif current == 1:
                                await metals_command(ctx)
                        elif reaction.emoji == "1️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 1")
                            if current == 0:
                                await futures_command(ctx)
                            elif current == 1:
                                await meats_command(ctx)
                        elif reaction.emoji == "2️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 2")
                            if current == 0:
                                await usbonds_command(ctx)
                            elif current == 1:
                                await grains_command(ctx)
                        elif reaction.emoji == "3️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 3")
                            if current == 0:
                                await glbonds_command(ctx)
                            elif current == 1:
                                await softs_command(ctx)
                        elif reaction.emoji == "4️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 4")
                            await indices_command(ctx)
                        elif reaction.emoji == "5️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 5")
                            await currencies_command(ctx)
                        elif reaction.emoji == "6️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 6")
                            await feargreed_command(ctx)
                        elif reaction.emoji == "7️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 7")
                            await valuation_command(ctx)
                        elif reaction.emoji == "8️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 8")
                            await performance_command(ctx)
                        elif reaction.emoji == "9️⃣":
                            if cfg.DEBUG:
                                print("Reaction selected: 9")
                            await energy_command(ctx)
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
                    title="TIMEOUT Economy Menu",
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                await ctx.send(embed=embed)

                for emoji in emoji_list:
                    await main_message.remove_reaction(emoji, ctx.bot.user)
                break


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(EconomyCommands(bot))
