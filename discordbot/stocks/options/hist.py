import os
import discord
import mplfinance as mpf
import discordbot.config_discordbot as cfg
from gamestonk_terminal.stocks.options import tradier_model


async def hist_command(
    ctx, ticker: str = None, expiry: str = "", strike: float = None, put: bool = False
):
    """Plot historical option prices

    Parameters
    ----------
    ticker: str
        Stock ticker
    expiry: str
        accepts 0-9
        0 being weeklies
        1+ for weeks out
        prompts reaction helper if empty
    strike: float
        Option strike price
    put: bool
        c for call
        p for put
    """

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.opt.hist {ticker} {strike} {put} {expiry}")

        # Check for argument
        if ticker is None:
            raise Exception("Stock ticker is required")

        if strike is None or put == "":
            raise Exception(
                'A strike and c/p is required\n```bash\n"!hist {ticker} {strike} {c/p}"```'
            )

        chain_id = None

        df_hist = tradier_model.get_historical_options(
            ticker, expiry, strike, put, chain_id
        )

        op_type = ["call", "put"][put]

        mc = mpf.make_marketcolors(
            up="green", down="red", edge="black", wick="black", volume="in", ohlc="i"
        )

        s = mpf.make_mpf_style(
            base_mpl_style="seaborn", marketcolors=mc, gridstyle=":", y_on_right=True
        )

        mpf.plot(
            df_hist,
            type="candle",
            volume=True,
            title=f"\n{ticker.upper()} {strike} {op_type} expiring {expiry} Historical",
            tight_layout=True,
            style=s,
            figratio=(10, 7),
            figscale=1.10,
            figsize=(12, 5),
            update_width_config=dict(
                candle_linewidth=1.0, candle_width=0.8, volume_linewidth=1.0
            ),
            savefig="opt_hist.png",
        )

        imagefile = "opt_hist.png"
        image = discord.File(imagefile)

        if cfg.DEBUG:
            print(f"Image: {imagefile}")
        title = " " + ticker.upper() + " Options: History"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_image(url="attachment://opt_hist.png")
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
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
