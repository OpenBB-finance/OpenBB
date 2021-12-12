import asyncio
import discord

from discordbot.run_discordbot import gst_bot
import discordbot.config_discordbot as cfg

from discordbot.stocks.options.vol import vol_command
from discordbot.stocks.options.iv import iv_command
from discordbot.stocks.options.oi import oi_command
from discordbot.stocks.options.unu import unu_command
from gamestonk_terminal.stocks.options import tradier_model

class OptionsCommands(discord.ext.commands.Cog):
    """Options menu."""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.ext.commands.command(name="iv")
    async def iv(self, ctx: discord.ext.commands.Context, ticker=""):
     async with ctx.typing():
        await asyncio.sleep(0.2)
        """Displays option IV [Barchart]

        Parameters
        -----------
        ticker: str
        """
        await iv_command(ctx, ticker)

    
    @discord.ext.commands.command(name="unu")
    async def unu(self, ctx: discord.ext.commands.Context, num=""):
     async with ctx.typing():
        await asyncio.sleep(0.2)        
        """Unusual Options

        Parameters
        -----------
        num: int
        """
        await unu_command(ctx, num)
    
    
    @discord.ext.commands.command(name="oi")
    async def oi(self, ctx: discord.ext.commands.Context, ticker="", expiry=""):
     async with ctx.typing():
        await asyncio.sleep(0.2)
        """Open Interest
        expiry = only accepts 0-9, inputs the dates up to 10 weeks
        
        if empty
        
        Sends a message to the discord user with the expiry dates.
        The user can then select a reaction to trigger the selected date.
        """

        if cfg.DEBUG:
            print(f"!oi {ticker} {expiry}")
        
        if ticker == "":
            embed = discord.Embed(
                title="ERROR Options: Open Interest",
                colour=cfg.COLOR,
                description="A stock ticker is required",
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

            await ctx.send(embed=embed)
            return
         
        dates = tradier_model.option_expirations(ticker)
        if expiry == "0":
            expiry = dates[0]
            await oi_command(ctx, ticker, expiry)
            return
        if expiry == "1":
            expiry = dates[1]
            await oi_command(ctx, ticker, expiry)
            return
        if expiry == "2":
            expiry = dates[2]
            await oi_command(ctx, ticker, expiry)
            return
        if expiry == "3":
            expiry = dates[3]
            await oi_command(ctx, ticker, expiry)
            return
        if expiry == "4":
            expiry = dates[4]
            await oi_command(ctx, ticker, expiry)
            return
        if expiry == "5":
            expiry = dates[5]
            await oi_command(ctx, ticker, expiry)
            return
        if expiry == "6":
            expiry = dates[6]
            await oi_command(ctx, ticker, expiry)
            return
        if expiry == "7":
            expiry = dates[7]
            await oi_command(ctx, ticker, expiry)
            return
        if expiry == "8":
            expiry = dates[8]
            await oi_command(ctx, ticker, expiry)
            return
        if expiry == "9":
            expiry = dates[9]
            await oi_command(ctx, ticker, expiry)
            return

        if not dates:
            embed = discord.Embed(
                title="ERROR Options: Open Interest",
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
            f"```0️⃣ " + dates[0] +"\n"
            f"1️⃣ " + dates[1] +"\n"
            f"2️⃣ " + dates[2] +"\n"
            f"3️⃣ " + dates[3] +"\n"
            f"4️⃣ " + dates[4] +"\n"
            f"5️⃣ " + dates[5] +"\n"
            f"6️⃣ " + dates[6] +"\n"
            f"7️⃣ " + dates[7] +"\n"
            f"8️⃣ " + dates[8] +"\n"
            f"9️⃣ " + dates[9] +"```"
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
            if reaction.emoji == "0️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 0")
                    expiry = dates[0]
                await oi_command(ctx, ticker, expiry)
            elif reaction.emoji == "1️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 1")
                    expiry = dates[1]
                await oi_command(ctx, ticker, expiry)
            elif reaction.emoji == "2️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 2")
                    expiry = dates[2]
                await oi_command(ctx, ticker, expiry)
            elif reaction.emoji == "3️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 3")
                    expiry = dates[3]
                await oi_command(ctx, ticker, expiry)
            elif reaction.emoji == "4️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 4")
                    expiry = dates[4]
                await oi_command(ctx, ticker, expiry)
            elif reaction.emoji == "5️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 5")
                    expiry = dates[5]
                await oi_command(ctx, ticker, expiry)
            elif reaction.emoji == "6️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 6")
                    expiry = dates[6]
                await oi_command(ctx, ticker, expiry)
            elif reaction.emoji == "7️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 7")
                    expiry = dates[7]
                await oi_command(ctx, ticker, expiry)
            elif reaction.emoji == "8️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 8")
                    expiry = dates[8]
                await oi_command(ctx, ticker, expiry)
            elif reaction.emoji == "9️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 9")
                    expiry = dates[9]
                await oi_command(ctx, ticker, expiry)

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

    @discord.ext.commands.command(name="vol")
    async def vol(self, ctx: discord.ext.commands.Context, ticker="", expiry=""):
     async with ctx.typing():
        await asyncio.sleep(0.2)
        """Open Interest

        expiry = only accepts 0-9, inputs the dates up to 10 weeks
        
        if empty
        
        Sends a message to the discord user with the expiry dates.
        The user can then select a reaction to trigger the selected date.
        """

        if cfg.DEBUG:
            print(f"!vol {ticker} {expiry}")
        
        if ticker == "":
            embed = discord.Embed(
                title="ERROR Options: Open Interest",
                colour=cfg.COLOR,
                description="A stock ticker is required",
            )
            embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
            )

            await ctx.send(embed=embed)
            return
        
        dates = tradier_model.option_expirations(ticker)
        if expiry == "0":
            expiry = dates[0]
            await vol_command(ctx, ticker, expiry)
            return
        if expiry == "1":
            expiry = dates[1]
            await vol_command(ctx, ticker, expiry)
            return
        if expiry == "2":
            expiry = dates[2]
            await vol_command(ctx, ticker, expiry)
            return
        if expiry == "3":
            expiry = dates[3]
            await vol_command(ctx, ticker, expiry)
            return
        if expiry == "4":
            expiry = dates[4]
            await vol_command(ctx, ticker, expiry)
            return
        if expiry == "5":
            expiry = dates[5]
            await vol_command(ctx, ticker, expiry)
            return
        if expiry == "6":
            expiry = dates[6]
            await vol_command(ctx, ticker, expiry)
            return
        if expiry == "7":
            expiry = dates[7]
            await vol_command(ctx, ticker, expiry)
            return
        if expiry == "8":
            expiry = dates[8]
            await vol_command(ctx, ticker, expiry)
            return
        if expiry == "9":
            expiry = dates[9]
            await vol_command(ctx, ticker, expiry)
            return

        if not dates:
            embed = discord.Embed(
                title="ERROR Options: Open Interest",
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
            f"```0️⃣ " + dates[0] +"\n"
            f"1️⃣ " + dates[1] +"\n"
            f"2️⃣ " + dates[2] +"\n"
            f"3️⃣ " + dates[3] +"\n"
            f"4️⃣ " + dates[4] +"\n"
            f"5️⃣ " + dates[5] +"\n"
            f"6️⃣ " + dates[6] +"\n"
            f"7️⃣ " + dates[7] +"\n"
            f"8️⃣ " + dates[8] +"\n"
            f"9️⃣ " + dates[9] +"```"
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
            if reaction.emoji == "0️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 0")
                    expiry = dates[0]
                await vol_command(ctx, ticker, expiry)
            elif reaction.emoji == "1️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 1")
                    expiry = dates[1]
                await vol_command(ctx, ticker, expiry)
            elif reaction.emoji == "2️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 2")
                    expiry = dates[2]
                await vol_command(ctx, ticker, expiry)
            elif reaction.emoji == "3️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 3")
                    expiry = dates[3]
                await vol_command(ctx, ticker, expiry)
            elif reaction.emoji == "4️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 4")
                    expiry = dates[4]
                await vol_command(ctx, ticker, expiry)
            elif reaction.emoji == "5️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 5")
                    expiry = dates[5]
                await vol_command(ctx, ticker, expiry)
            elif reaction.emoji == "6️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 6")
                    expiry = dates[6]
                await vol_command(ctx, ticker, expiry)
            elif reaction.emoji == "7️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 7")
                    expiry = dates[7]
                await vol_command(ctx, ticker, expiry)
            elif reaction.emoji == "8️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 8")
                    expiry = dates[8]
                await vol_command(ctx, ticker, expiry)
            elif reaction.emoji == "9️⃣":
                if cfg.DEBUG:
                    print("Reaction selected: 9")
                    expiry = dates[9]
                await vol_command(ctx, ticker, expiry)

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

def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(OptionsCommands(bot))
