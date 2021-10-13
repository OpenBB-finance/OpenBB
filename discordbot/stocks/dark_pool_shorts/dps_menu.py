import discord
from discordbot import gst_bot
import config_discordbot as cfg
import asyncio

from stocks.dark_pool_shorts.shorted import shorted_command
from stocks.dark_pool_shorts.ftd import ftd_command
from stocks.dark_pool_shorts.dpotc import dpotc_command
from stocks.dark_pool_shorts.spos import spos_command
from stocks.dark_pool_shorts.psi import psi_command
from stocks.dark_pool_shorts.hsi import hsi_command
from stocks.dark_pool_shorts.pos import pos_command
from stocks.dark_pool_shorts.sidtc import sidtc_command


class DarkPoolShortsCommands(discord.ext.commands.Cog):
    """Dark Pool Shorts menu."""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.ext.commands.command(name="stocks.dps.shorted")
    async def shorted(self, ctx: discord.ext.commands.Context, arg=""):
        await shorted_command(ctx, arg)

    @discord.ext.commands.command(name="stocks.dps.hsi")
    async def hsi(self, ctx: discord.ext.commands.Context, arg=""):
        await hsi_command(ctx, arg)

    @discord.ext.commands.command(name="stocks.dps.pos")
    async def pos(self, ctx: discord.ext.commands.Context, arg="", arg2=""):
        await pos_command(ctx, arg, arg2)

    @discord.ext.commands.command(name="stocks.dps.sidtc")
    async def sidtc(self, ctx: discord.ext.commands.Context, arg="", arg2=""):
        await sidtc_command(ctx, arg, arg2)

    @discord.ext.commands.command(name="stocks.dps.ftd")
    async def ftd(self, ctx: discord.ext.commands.Context, arg, arg2="", arg3=""):
        await ftd_command(ctx, arg, arg2, arg3)

    @discord.ext.commands.command(name="stocks.dps.dpotc")
    async def dpotc(self, ctx: discord.ext.commands.Context, arg):
        await dpotc_command(ctx, arg)

    @discord.ext.commands.command(name="stocks.dps.spos")
    async def spos(self, ctx: discord.ext.commands.Context, arg):
        await spos_command(ctx, arg)

    @discord.ext.commands.command(name="stocks.dps.psi")
    async def psi(self, ctx: discord.ext.commands.Context, arg):
        await psi_command(ctx, arg)

    @discord.ext.commands.command(name="stocks.dps")
    async def dark_pool_shorts_menu(self, ctx: discord.ext.commands.Context, arg=""):
        if cfg.DEBUG:
            print("!stocks.dps")

        text = (
            "0️⃣ !stocks.dps.shorted <NUM>\n"
            "1️⃣ !stocks.dps.hsi <NUM>\n"
            "2️⃣ !stocks.dps.pos <NUM> <SORT>\n"
            "3️⃣ !stocks.dps.sidtc <NUM> <SORT>\n"
        )
        if arg:
            text += (
                f"4️⃣ !stocks.dps.ftd {arg} <DATE_START> <DATE_END>\n"
                f"5️⃣ !stocks.dps.dpotc {arg}\n"
                f"6️⃣ !stocks.dps.spos {arg}\n"
                f"7️⃣ !stocks.dps.psi {arg}\n"
            )
        else:
            text += (
                "\nMore commands available when providing a ticker with:"
                "\n!stocks.dps <TICKER>"
            )

        title = "Dark Pool Shorts (DPS) Menu"
        embed = discord.Embed(title=title, description=text, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        msg = await ctx.send(embed=embed)

        emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣"]

        if arg:
            emoji_list += ["4️⃣", "5️⃣", "6️⃣", "7️⃣"]

        for emoji in emoji_list:
            await msg.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in emoji_list

        try:
            reaction, user = await gst_bot.wait_for(
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
                await ftd_command(ctx, arg)
            elif reaction.emoji == "5️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 5")
                await dpotc_command(ctx, arg)
            elif reaction.emoji == "6️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 6")
                await spos_command(ctx, arg)
            elif reaction.emoji == "7️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 7")
                await psi_command(ctx, arg)

            for emoji in emoji_list:
                await msg.remove_reaction(emoji, ctx.bot.user)

        except asyncio.TimeoutError:
            text = text + "\n\nCommand timeout."
            embed = discord.Embed(title=title, description=text)
            await msg.edit(embed=embed)
            for emoji in emoji_list:
                await msg.remove_reaction(emoji, ctx.bot.user)


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(DarkPoolShortsCommands(bot))
