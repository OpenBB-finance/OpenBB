import discord
import config_discordbot as cfg
from discordbot import gst_imgur
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import os
import helpers

from gamestonk_terminal.stocks.due_diligence import business_insider_model


async def pt_command(ctx, ticker="", raw="", start=""):
    """Displays price targets [Business Insider]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.dd.pt {ticker}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        if start == "":
            start = datetime.now() - timedelta(days=365)
        else:
            start = datetime.strptime(start, cfg.DATE_FORMAT)

        if raw == "false" or raw == "False" or raw == "FALSE" or raw == "":
            raw = False
        elif raw == "true" or raw == "True" or raw == "TRUE":
            raw = True
        else:
            raise Exception("raw argument has to be true or false")

        df_analyst_data = business_insider_model.get_price_target_from_analysts(ticker)
        stock = helpers.load(ticker, start)

        if df_analyst_data.empty or stock.empty:
            raise Exception("Enter valid ticker")

        # Output Data

        if raw:
            df_analyst_data.sort_index(ascending=False)
            report = "´´´" + df_analyst_data.to_string() + "´´´"
            embed = discord.Embed(
                title="Stocks: [Business Insider] Price Targets",
                description=report,
                colour=cfg.COLOR,
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            ctx.send(embed=embed)
        else:
            if start:
                df_analyst_data = df_analyst_data[start:]

            plt.plot(stock.index, stock["Adj Close"].values, lw=3)

            plt.plot(df_analyst_data.groupby(by=["Date"]).mean())

            plt.scatter(
                df_analyst_data.index, df_analyst_data["Price Target"], c="r", s=40
            )

            plt.legend(["Closing Price", "Average Price Target", "Price Target"])

            plt.title(f"{ticker} (Time Series) and Price Target")
            plt.xlim(stock.index[0], stock.index[-1])
            plt.xlabel("Time")
            plt.ylabel("Share Price")
            plt.grid(b=True, which="major", color="#666666", linestyle="-")

            plt.savefig("ta_pt.png")
            uploaded_image = gst_imgur.upload_image("ta_pt.png", title="something")
            image_link = uploaded_image.link
            if cfg.DEBUG:
                print(f"Image URL: {image_link}")
            title = "Stocks: [Business Insider] Price Targets " + ticker
            embed = discord.Embed(title=title, colour=cfg.COLOR)
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            embed.set_image(url=image_link)
            os.remove("ta_pt.png")

            await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [Business Insider] Price Targets",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
