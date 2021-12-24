import asyncio
import discord

import discordbot.config_discordbot as cfg

from discordbot.run_discordbot import gst_bot

from discordbot.stocks.screener.historical import historical_command
from discordbot.stocks.screener.overview import overview_command
from discordbot.stocks.screener.presets_custom import presets_custom_command
from discordbot.stocks.screener.presets_default import presets_default_command
from discordbot.stocks.screener.valuation import valuation_command
from discordbot.stocks.screener.financial import financial_command
from discordbot.stocks.screener.ownership import ownership_command
from discordbot.stocks.screener.performance import performance_command
from discordbot.stocks.screener.technical import technical_command
from discordbot.stocks.screener import screener_options as so


# pylint: disable=R0912


class ScreenerCommands(discord.ext.commands.Cog):
    """Screener menu"""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.ext.commands.command(name="stocks.scr.presets_default")
    async def presets_default(self, ctx: discord.ext.commands.Context):
        """Displays every available preset"""
        await presets_default_command(ctx)

    @discord.ext.commands.command(name="stocks.scr.presets_custom")
    async def presets_custom(self, ctx: discord.ext.commands.Context):
        """Displays every available preset"""
        await presets_custom_command(ctx)

    @discord.ext.commands.command(
        name="stocks.scr.historical", usage="[signal] [start]"
    )
    async def historical(
        self,
        ctx: discord.ext.commands.Context,
        signal="most_volatile",
        start="",
    ):
        """Displays trades made by the congress/senate/house [quiverquant.com]

        Parameters
        -----------
        signal: str
            Signal. Default: most_volatile
        start:
            Starting date in YYYY-MM-DD format
        """
        await historical_command(ctx, signal, start)

    @discord.ext.commands.command(
        name="stocks.scr.overview", usage="[preset] [sort] [limit] [ascend]"
    )
    async def overview(
        self,
        ctx: discord.ext.commands.Context,
        preset="template",
        sort="",
        limit="5",
        ascend="False",
    ):
        """Displays stocks with overview data such as Sector and Industry [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await overview_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(
        name="stocks.scr.valuation", usage="[preset] [sort] [limit] [ascend]"
    )
    async def valuation(
        self,
        ctx: discord.ext.commands.Context,
        preset="template",
        sort="",
        limit="5",
        ascend="False",
    ):
        """Displays results from chosen preset focusing on valuation metrics [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await valuation_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(
        name="stocks.scr.financial", usage="[preset] [sort] [limit] [ascend]"
    )
    async def financial(
        self,
        ctx: discord.ext.commands.Context,
        preset="template",
        sort="",
        limit="5",
        ascend="False",
    ):
        """Displays returned results from preset by financial metrics [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await financial_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(
        name="stocks.scr.ownership", usage="[preset] [sort] [limit] [ascend]"
    )
    async def ownership(
        self,
        ctx: discord.ext.commands.Context,
        preset="template",
        sort="",
        limit="5",
        ascend="False",
    ):
        """Displays stocks based on own share float and ownership data [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await ownership_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(
        name="stocks.scr.performance", usage="[preset] [sort] [limit] [ascend]"
    )
    async def performance(
        self,
        ctx: discord.ext.commands.Context,
        preset="template",
        sort="",
        limit="5",
        ascend="False",
    ):
        """Displays stocks and sort by performance categories [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await performance_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(
        name="stocks.scr.technical", usage="[preset] [sort] [limit] [ascend]"
    )
    async def technical(
        self,
        ctx: discord.ext.commands.Context,
        preset="template",
        sort="",
        limit="5",
        ascend="False",
    ):
        """Displays stocks according to chosen preset, sorting by technical factors [Finviz]

        Parameters
        -----------
        preset: str
            screener preset
        sort: str
            column to sort by
        limit: int
            number of stocks to display
        ascend: boolean
            whether it's sorted by ascending order or not. Default: False
        """
        await technical_command(ctx, preset, sort, limit, ascend)

    @discord.ext.commands.command(name="stocks.scr")
    async def scr(self, ctx: discord.ext.commands.Context, preset=""):
        """Screener Context Menu

        Run `!help ScreenerCommands` to see the list of available commands.

        Returns
        -------
        Sends a message to the discord user with the commands from the screener context.
        The user can then select a reaction to trigger a command.
        """

        if preset != "" and preset not in so.all_presets:
            raise Exception("Invalid preset selected!")

        if cfg.DEBUG:
            print("!stocks.scr")

        if preset:
            text = (
                "0️⃣ !stocks.scr.presets_default\n"
                "1️⃣ !stocks.scr.presets_custom\n"
                "2️⃣ !stocks.scr.historical <SIGNAL> <START>\n"
                f"3️⃣ !stocks.scr.overview {preset} <SORT> <LIMIT> <ASCEND>\n"
                f"4️⃣ !stocks.scr.valuation {preset} <SORT> <LIMIT> <ASCEND>\n"
                f"5️⃣ !stocks.scr.financial {preset} <SORT> <LIMIT> <ASCEND>\n"
                f"6️⃣ !stocks.scr.ownership {preset} <SORT> <LIMIT> <ASCEND>\n"
                f"7️⃣ !stocks.scr.performance {preset} <SORT> <LIMIT> <ASCEND>\n"
                f"8️⃣ !stocks.scr.technical {preset} <SORT> <LIMIT> <ASCEND>"
            )
        else:
            text = (
                "0️⃣ !stocks.scr.presets_default\n"
                "1️⃣ !stocks.scr.presets_custom\n"
                "2️⃣ !stocks.scr.historical <SIGNAL> <START>\n"
                "3️⃣ !stocks.scr.overview <PRESET> <SORT> <LIMIT> <ASCEND>\n"
                "4️⃣ !stocks.scr.valuation <PRESET> <SORT> <LIMIT> <ASCEND>\n"
                "5️⃣ !stocks.scr.financial <PRESET> <SORT> <LIMIT> <ASCEND>\n"
                "6️⃣ !stocks.scr.ownership <PRESET> <SORT> <LIMIT> <ASCEND>\n"
                "7️⃣ !stocks.scr.performance <PRESET> <SORT> <LIMIT> <ASCEND>\n"
                "8️⃣ !stocks.scr.technical <PRESET> <SORT> <LIMIT> <ASCEND>"
            )

        title = "Screener Menu"
        embed = discord.Embed(title=title, description=text, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        msg = await ctx.send(embed=embed)

        emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]

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
                await presets_default_command(ctx)
            elif reaction.emoji == "1️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 1")
                await presets_custom_command(ctx)
            elif reaction.emoji == "2️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 2")
                await historical_command(ctx, preset)
            elif reaction.emoji == "3️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 3")
                await overview_command(ctx, preset)
            elif reaction.emoji == "4️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 4")
                await valuation_command(ctx, preset)
            elif reaction.emoji == "5️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 5")
                await financial_command(ctx, preset)
            elif reaction.emoji == "6️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 6")
                await ownership_command(ctx, preset)
            elif reaction.emoji == "7️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 7")
                await performance_command(ctx, preset)
            elif reaction.emoji == "8️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 8")
                await technical_command(ctx, preset)

            for emoji in emoji_list:
                await msg.remove_reaction(emoji, ctx.bot.user)

        except asyncio.TimeoutError:
            for emoji in emoji_list:
                await msg.remove_reaction(emoji, ctx.bot.user)
            if cfg.DEBUG:
                embed = discord.Embed(
                    description="Error timeout - you snooze you lose! 😋",
                    colour=cfg.COLOR,
                    title="TIMEOUT Screener Menu",
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
                await ctx.send(embed=embed)


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(ScreenerCommands(bot))
