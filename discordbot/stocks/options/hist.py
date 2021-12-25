import os
import discord
import matplotlib.pyplot as plt
import mplfinance as mpf
import seaborn as sns
import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.options import tradier_model




async def hist_command(ctx,  ticker: str= None, strike: float= None, put: bool= False, expiry: str= None):
    """Options History Chart"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.opt.hist {ticker} {strike} {put} {expiry}")

        # Check for argument
        if ticker is None:
            raise Exception("Stock ticker is required")        
        
        """Plot historical option prices

        Parameters
        ----------
        ticker: str
            Stock ticker
        expiry: str
            Expiry date of option
        strike: float
            Option strike price
        put: bool
            c for calls
            p for puts
        chain_id: str
            OCC option symbol
        """
        chain_id: str= None


        df_hist = tradier_model.get_historical_options(
            ticker, expiry, strike, put, chain_id
        )

        op_type = ["call", "put"][put]

        mc = mpf.make_marketcolors(
            up="green", down="red", edge="black", wick="black", volume="in", ohlc="i"
        )

        s = mpf.make_mpf_style(base_mpl_style='seaborn', marketcolors=mc, gridstyle=":", y_on_right=True)

        mpf.plot(
            df_hist,
            type="candle",
            volume=True,
            title=f"\n{ticker.upper()} {strike} {op_type} expiring {expiry} Historical",
            tight_layout=True,
            style=s,
            figratio=(12, 5),
            figscale=2.10,
            figsize=(12,5),
            update_width_config=dict(
                candle_linewidth=1.0, candle_width=1.2, volume_linewidth=1.0
            ),
            savefig="opt_hist.png",
        )

        imagefile = "opt_hist.png"
        image = discord.File(imagefile)

        if cfg.DEBUG:
            print(f"Image: {imagefile}")
        title = " " + ticker.upper() + " Options: History"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_image(
            url="attachment://opt_hist.png"
        )
        os.remove("opt_hist.png")

        await ctx.send(embed=embed, file=image)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Options: History",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
             name=cfg.AUTHOR_NAME,
             icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
