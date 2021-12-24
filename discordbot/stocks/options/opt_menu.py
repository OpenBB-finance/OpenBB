import asyncio
import discord

from discordbot.run_discordbot import gst_bot
import discordbot.config_discordbot as cfg
from gamestonk_terminal.stocks.options import tradier_model
from discordbot.reaction_helper import expiry_dates_reaction

from discordbot.stocks.options.hist import hist_command
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
    async def iv(self, ctx: discord.ext.commands.Context, ticker: str= None):
     async with ctx.typing():
        await asyncio.sleep(0.2)
        """Displays option IV [Barchart]

        Parameters
        -----------
        ticker: str
            ticker,
        """
        await iv_command(ctx, ticker)

    
    @discord.ext.commands.command(name="unu")
    async def unu(self, ctx: discord.ext.commands.Context, num: int= None):
     async with ctx.typing():
        await asyncio.sleep(0.2)        
        """Unusual Options"""
        await unu_command(ctx, num)
    
    @discord.ext.commands.command(name="hist")
    async def hist(self, ctx: discord.ext.commands.Context, ticker: str= None, strike: float= None, put="", expiry: str= None):
     async with ctx.typing():
        await asyncio.sleep(0.2)        
        """Historical Options

        Parameters
        -----------
        ticker: str
            ticker
        strike: float
            strike 
        put: bool
            c for call
            p for put
        """
        if cfg.DEBUG:
            print(f"!hist {ticker} {strike} {put} {expiry}")
        
        if strike is None or put =="":
            embed = discord.Embed(
                title="ERROR Options: History",
                colour=cfg.COLOR,
                description="A strike and c/p is required\n```bash\n\"!hist {ticker} {strike} {c/p}\"```",
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

            await ctx.send(embed=embed)
            return

        if put == "p":
            put = bool(True)
        if put == "c":
            put = bool(False)
        
        call_arg = (strike, put,)
        func_cmd= hist_command
    

        await expiry_dates_reaction(ctx, ticker, call_arg, expiry, func_cmd)
    
    
    @discord.ext.commands.command(name="oi")
    async def oi(self, ctx: discord.ext.commands.Context, ticker: str= None, expiry: str= None, min_sp: float= None, max_sp: float= None):
     async with ctx.typing():
        await asyncio.sleep(0.2)
        """Open Interest
        expiry = only accepts 0-9, inputs the dates up to 10 weeks
        
        if empty
        
        Sends a message to the discord user with the expiry dates.
        The user can then select a reaction to trigger the selected date.
        """

        if cfg.DEBUG:
            print(f"!oi {ticker} {expiry} {min_sp} {max_sp}")
        
        if ticker is None:
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
        
        call_arg = (min_sp, max_sp)
        func_cmd= oi_command
    

        await expiry_dates_reaction(ctx, ticker, call_arg, expiry, func_cmd)

    @discord.ext.commands.command(name="vol")
    async def vol(self, ctx: discord.ext.commands.Context, ticker: str= None, expiry: str= None, min_sp: float= None, max_sp: float= None):
     async with ctx.typing():
        await asyncio.sleep(0.2)
        """Open Interest
        expiry = only accepts 0-9, inputs the dates up to 10 weeks
        
        if empty
        
        Sends a message to the discord user with the expiry dates.
        The user can then select a reaction to trigger the selected date.
        """

        if cfg.DEBUG:
            print(f"!vol {ticker} {expiry} {min_sp} {max_sp}")
        
        if ticker is None:
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
        
        call_arg = (min_sp, max_sp)
        func_cmd= vol_command
    

        await expiry_dates_reaction(ctx, ticker, call_arg, expiry, func_cmd)


def setup(bot: discord.ext.commands.Bot):
    gst_bot.add_cog(OptionsCommands(bot))
