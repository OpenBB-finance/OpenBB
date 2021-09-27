import discord_components
import asyncio
from discordbot import gst_bot
import yfinance as yf


def load(ticker, start_date):
    df_stock_candidate = yf.download(ticker, start=start_date, progress=False)
    df_stock_candidate.index.name = "date"
    return df_stock_candidate


async def pagination(cols, ctx):
    current = 0
    components = [
        [
            discord_components.Button(
                label="Prev", id="back", style=discord_components.ButtonStyle.red
            ),
            discord_components.Button(
                label=f"Page {int(cols.index(cols[current]))}/{len(cols)-1}",
                id="cur",
                style=discord_components.ButtonStyle.green,
                disabled=True,
            ),
            discord_components.Button(
                label="Next", id="front", style=discord_components.ButtonStyle.green
            ),
        ]
    ]
    main_message = await ctx.send(embed=cols[current], components=components)

    while True:
        # Try and except blocks to catch timeout and break
        try:
            interaction = await gst_bot.wait_for(
                "button_click",
                check=lambda i: i.component.id in ["back", "front"],  # You can add more
                timeout=30.0,  # 30 seconds of inactivity
            )
            # Getting the right list index
            if interaction.component.id == "back":
                current -= 1
            elif interaction.component.id == "front":
                current += 1

            # If its out of index, go back to start / end
            if current == len(cols):
                current = 0
            elif current < 0:
                current = len(cols) - 1

            # Edit to new page + the center counter changes
            components = [
                [
                    discord_components.Button(
                        label="Prev",
                        id="back",
                        style=discord_components.ButtonStyle.red,
                    ),
                    discord_components.Button(
                        label=f"Page {int(cols.index(cols[current]))}/{len(cols)-1}",
                        id="cur",
                        style=discord_components.ButtonStyle.green,
                        disabled=True,
                    ),
                    discord_components.Button(
                        label="Next",
                        id="front",
                        style=discord_components.ButtonStyle.green,
                    ),
                ]
            ]

            await interaction.edit_origin(embed=cols[current], components=components)

        except asyncio.TimeoutError:
            # Disable and get outta here
            components = [
                [
                    discord_components.Button(
                        label="Prev",
                        id="back",
                        style=discord_components.ButtonStyle.green,
                        disabled=True,
                    ),
                    discord_components.Button(
                        label=f"Page {int(cols.index(cols[current])) + 1}/{len(cols)-1}",
                        id="cur",
                        style=discord_components.ButtonStyle.grey,
                        disabled=True,
                    ),
                    discord_components.Button(
                        label="Next",
                        id="front",
                        style=discord_components.ButtonStyle.green,
                        disabled=True,
                    ),
                ]
            ]
            await main_message.edit(components=components)
            break
