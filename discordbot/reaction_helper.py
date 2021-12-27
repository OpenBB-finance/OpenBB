import asyncio
import discord

from gamestonk_terminal.config_terminal import TRADIER_TOKEN
from gamestonk_terminal.stocks.options import tradier_model, yfinance_model
from discordbot.run_discordbot import gst_bot
import discordbot.config_discordbot as cfg


async def expiry_dates_reaction(ctx, ticker, expiry, func_cmd, call_arg: tuple = None):
    if TRADIER_TOKEN == "REPLACE_ME":
        dates = yfinance_model.option_expirations(ticker)
    else:
        dates = tradier_model.option_expirations(ticker)

    if expiry is not None:

        index = int(expiry)

        if 0 <= index <= 9:
            expiry = dates[index]
            if call_arg is None:
                await func_cmd(ctx, ticker, expiry)
            else:
                await func_cmd(ctx, ticker, expiry, *call_arg)
            return

    if not dates:
        embed = discord.Embed(
            title="ERROR Options",
            colour=cfg.COLOR,
            description="Enter a valid stock ticker",
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
        return

    text = (
        "```0️⃣ " + dates[0] + "\n"
        "1️⃣ " + dates[1] + "\n"
        "2️⃣ " + dates[2] + "\n"
        "3️⃣ " + dates[3] + "\n"
        "4️⃣ " + dates[4] + "\n"
        "5️⃣ " + dates[5] + "\n"
        "6️⃣ " + dates[6] + "\n"
        "7️⃣ " + dates[7] + "\n"
        "8️⃣ " + dates[8] + "\n"
        "9️⃣ " + dates[9] + "```"
    )

    title = " " + ticker.upper() + " Options: Expiry Date"
    embed = discord.Embed(title=title, description=text, colour=cfg.COLOR)
    embed.set_author(
        name=cfg.AUTHOR_NAME,
        icon_url=cfg.AUTHOR_ICON_URL,
    )

    msg = await ctx.send(embed=embed)

    emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    for emoji in emoji_list:
        await msg.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) in emoji_list

    try:
        reaction, _ = await gst_bot.wait_for(
            "reaction_add", timeout=cfg.MENU_TIMEOUT, check=check
        )
        for N in range(0, 10):
            if reaction.emoji == emoji_list[N]:
                if cfg.DEBUG:
                    print(f"Reaction selected: {N}")
                    expiry = dates[N]
                    if call_arg is None:
                        await func_cmd(ctx, ticker, expiry)
                    else:
                        await func_cmd(ctx, ticker, expiry, *call_arg)

        for emoji in emoji_list:
            await msg.remove_reaction(emoji, ctx.bot.user)

    except asyncio.TimeoutError:
        for emoji in emoji_list:
            await msg.remove_reaction(emoji, ctx.bot.user)
        embed = discord.Embed(
            description="Error timeout - you snooze you lose! 😋",
            colour=cfg.COLOR,
            title="TIMEOUT  " + ticker.upper() + " Options: Expiry Date",
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        await ctx.send(embed=embed)
