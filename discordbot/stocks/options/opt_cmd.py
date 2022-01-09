import asyncio

import discord
import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_bot, logger
from discordbot.stocks.options.calls import calls_command
from discordbot.stocks.options.expirations import expirations_command
from discordbot.stocks.options.hist import hist_command
from discordbot.stocks.options.iv import iv_command
from discordbot.stocks.options.oi import oi_command
from discordbot.stocks.options.puts import puts_command
from discordbot.stocks.options.unu import unu_command
from discordbot.stocks.options.vol import vol_command

# pylint: disable=R0912


async def opt_command(ctx, ticker="", expiration="", strike="", put=""):
    """Options Menu command"""

    if cfg.DEBUG:
        logger.debug("!stocks.opt %s %s %s %s", ticker, expiration, strike, put)

    if ticker:
        current = 1
        hist = (
            f"7️⃣ !stocks.opt.hist {ticker} (strike*) (c/p*) {expiration}\n\n* Required"
        )
        if strike and put:
            hist = f"7️⃣ !stocks.opt.hist {ticker} {strike} {put} {expiration}"
            current = 2
        text = (
            "```0️⃣ !stocks.opt.unu\n"
            f"1️⃣ !stocks.opt.exp {ticker}\n"
            f"2️⃣ !stocks.opt.iv {ticker}\n"
            f"3️⃣ !stocks.opt.calls {ticker} {expiration} \n"
            f"4️⃣ !stocks.opt.puts {ticker} {expiration} \n"
            f"5️⃣ !stocks.opt.oi {ticker} {expiration} \n"
            f"6️⃣ !stocks.opt.vol {ticker} {expiration} \n"
            f"{hist}```"
        )

    if put == "p":
        put = bool(True)
    if put == "c":
        put = bool(False)

    title = "Stocks: Options Menu"
    embed = discord.Embed(title=title, description=text, colour=cfg.COLOR)
    embed.set_author(
        name=cfg.AUTHOR_NAME,
        icon_url=cfg.AUTHOR_ICON_URL,
    )
    msg = await ctx.send(embed=embed, delete_after=60.0)

    if current == 1:
        emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
    if current == 2:
        emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]

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
            await unu_command(ctx)
        elif reaction.emoji == "1️⃣":
            if cfg.DEBUG:
                print("Reaction selected: 1")
            await expirations_command(ctx, ticker)
        elif reaction.emoji == "2️⃣":
            if cfg.DEBUG:
                print("Reaction selected: 2")
            await iv_command(ctx, ticker)
        elif reaction.emoji == "3️⃣":
            if cfg.DEBUG:
                print("Reaction selected: 3")
            await calls_command(ctx, ticker, expiration)
        elif reaction.emoji == "4️⃣":
            if cfg.DEBUG:
                print("Reaction selected: 4")
            await puts_command(ctx, ticker, expiration)
        elif reaction.emoji == "5️⃣":
            if cfg.DEBUG:
                print("Reaction selected: 5")
            await oi_command(ctx, ticker, expiration)
        elif reaction.emoji == "6️⃣":
            if cfg.DEBUG:
                print("Reaction selected: 6")
            await vol_command(ctx, ticker, expiration)
        elif reaction.emoji == "7️⃣":
            if cfg.DEBUG:
                print("Reaction selected: 7")
            strike = float(strike)
            await hist_command(ctx, ticker, expiration, strike, put)

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
            await ctx.send(embed=embed, delete_after=30.0)
