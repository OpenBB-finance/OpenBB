import os
import discord

import discordbot.config_discordbot as cfg
from discordbot.helpers import pagination


async def presets_command(ctx):
    """Displays every preset"""
    try:

        # Debug
        if cfg.DEBUG:
            print("!stocks.scr.presets")

        presets_path = os.path.join(
            cfg.GST_PATH, "gamestonk_terminal", "stocks", "screener", "presets", ""
        )

        d_signals_desc = {
            "top_gainers": "stocks with the highest %% price gain today",
            "top_losers": "stocks with the highest %% price loss today",
            "new_high": "stocks making 52-week high today",
            "new_low": "stocks making 52-week low today",
            "most_volatile": "stocks with the highest widest high/low trading range today",
            "most_active": "stocks with the highest trading volume today",
            "unusual_volume": "stocks with unusually high volume today - the highest relative volume ratio",
            "overbought": "stock is becoming overvalued and may experience a pullback.",
            "oversold": "oversold stocks may represent a buying opportunity for investors",
            "downgrades": "stocks downgraded by analysts today",
            "upgrades": "stocks upgraded by analysts today",
            "earnings_before": "companies reporting earnings today, before market open",
            "earnings_after": "companies reporting earnings today, after market close",
            "recent_insider_buying": "stocks with recent insider buying activity",
            "recent_insider_selling": "stocks with recent insider selling activity",
            "major_news": "stocks with the highest news coverage today",
            "horizontal_sr": "horizontal channel of price range between support and resistance trendlines",
            "tl_resistance": "once a rising trendline is broken",
            "tl_support": "once a falling trendline is broken",
            "wedge_up": "upward trendline support and upward trendline resistance (reversal)",
            "wedge_down": "downward trendline support and downward trendline resistance (reversal)",
            "wedge": "upward trendline support, downward trendline resistance (contiunation)",
            "triangle_ascending": "upward trendline support and horizontal trendline resistance",
            "triangle_descending": "horizontal trendline support and downward trendline resistance",
            "channel_up": "both support and resistance trendlines slope upward",
            "channel_down": "both support and resistance trendlines slope downward",
            "channel": "both support and resistance trendlines are horizontal",
            "double_top": "stock with 'M' shape that indicates a bearish reversal in trend",
            "double_bottom": "stock with 'W' shape that indicates a bullish reversal in trend",
            "multiple_top": "same as double_top hitting more highs",
            "multiple_bottom": "same as double_bottom hitting more lows",
            "head_shoulders": "chart formation that predicts a bullish-to-bearish trend reversal",
            "head_shoulders_inverse": "chart formation that predicts a bearish-to-bullish trend reversal",
        }

        presets = [
            preset.split(".")[0]
            for preset in os.listdir(presets_path)
            if preset[-4:] == ".ini"
        ]

        description = "***Custom Presets:***\n"

        for preset in presets:
            with open(
                presets_path + preset + ".ini",
                encoding="utf8",
            ) as f:
                preset_line = ""
                for line in f:
                    if line.strip() == "[General]":
                        break
                    preset_line += line.strip()
            description += f"**{preset}:** *{preset_line.split('Description: ')[1].replace('#', '')}*\n"

        description += "\n\n***Default Presets:***\n"
        for signame, sigdesc in d_signals_desc.items():
            description += f"**{signame}:** *{sigdesc}*\n"

        if len(description) <= 4000:
            embed = discord.Embed(
                title="Stocks: Screener Presets",
                description=description,
                colour=cfg.COLOR,
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

            await ctx.send(embed=embed)

        else:
            i = 0
            str_start = 0
            str_end = 4000
            columns = []
            while i <= len(description) / 4000:
                columns.append(
                    discord.Embed(
                        title="Stocks: Screener Presets",
                        description=description[str_start:str_end],
                        colour=cfg.COLOR,
                    ).set_author(
                        name=cfg.AUTHOR_NAME,
                        icon_url=cfg.AUTHOR_ICON_URL,
                    )
                )
                str_end = str_start
                str_start += 4000
                i += 1

            await pagination(columns, ctx)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Screener Presets",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
