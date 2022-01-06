import discord
import numpy as np
import pandas as pd
import requests
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import get_user_agent

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import logger


async def unu_command(ctx, num: int = None):
    """Unusual Options"""
    try:

        # Debug
        if cfg.DEBUG:
            logger.debug("!stocks.opt.unu %s", num)

        # Check for argument
        if num is None:
            num = 10

        pages = np.arange(0, num // 20 + 1)
        data_list = []
        for page_num in pages:

            r = requests.get(
                f"https://app.fdscanner.com/api2/unusualvolume?p=0&page_size=20&page={int(page_num)}",
                headers={"User-Agent": get_user_agent()},
            )

            if r.status_code != 200:
                logger.debug("Error in fdscanner request")
                return pd.DataFrame(), "request error"

            data_list.append(r.json())

        ticker, expiry, option_strike, option_type, ask, bid, oi, vol, voi = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
        for data in data_list:
            for entry in data["data"]:
                ticker.append(entry["tk"])
                expiry.append(entry["expiry"])
                option_strike.append(float(entry["s"]))
                option_type.append("Put" if entry["t"] == "P" else "Call")
                ask.append(entry["a"])
                bid.append(entry["b"])
                oi.append(entry["oi"])
                vol.append(entry["v"])
                voi.append(entry["vol/oi"])

        df = pd.DataFrame(
            {
                "Ticker": ticker,
                "Exp": expiry,
                "Strike": option_strike,
                "Type": option_type,
                "Vol/OI": voi,
                "Vol": vol,
                "OI": oi,
            }
        )

        df = df.replace({"2021-", "2022-"}, "", regex=True)

        report = (
            "```"
            + tabulate(
                df,
                headers=["T", "Exp", "ST", "C/P", "V/O", "Vol", "OI"],
                tablefmt="fancy_grid",
                showindex=False,
                floatfmt=["", "", ".1f", "", ".1f", ".0f", ".0f", ".2f", ".2f"],
            )
            + "```"
        )
        embed = discord.Embed(
            title="Unusual Options",
            description=report,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Unusual Options",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
