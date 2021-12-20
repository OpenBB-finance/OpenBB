import os
import random
from datetime import datetime, timedelta
import configparser
import discord
from matplotlib import pyplot as plt
import yfinance as yf
from pandas.plotting import register_matplotlib_converters
from finvizfinance.screener import ticker
import discordbot.config_discordbot as cfg

from discordbot.run_discordbot import gst_imgur

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.stocks.screener import finviz_view
from gamestonk_terminal.stocks.screener import finviz_model
from gamestonk_terminal.helper_funcs import plot_autoscale

# pylint:disable=no-member


async def historical_command(ctx, signal="most_volatile", start=""):
    """Displays historical price comparison between similar companies [Yahoo Finance]"""
    try:

        # Debug user input
        if cfg.DEBUG:
            print(f"!stocks.scr.historical {signal} {start}")

        register_matplotlib_converters()

        presets_path = os.path.join(cfg.GST_PATH, "stocks", "screener", "presets", "")

        screen = ticker.Ticker()

        if signal in finviz_model.d_signals:
            screen.set_filter(signal=finviz_model.d_signals[signal])

        else:
            preset_filter = configparser.RawConfigParser()
            preset_filter.optionxform = str  # type: ignore
            preset_filter.read(presets_path + signal + ".ini")

            d_general = preset_filter["General"]
            d_filters = {
                **preset_filter["Descriptive"],
                **preset_filter["Fundamental"],
                **preset_filter["Technical"],
            }

            d_filters = {k: v for k, v in d_filters.items() if v}

            if d_general["Signal"]:
                screen.set_filter(filters_dict=d_filters, signal=d_general["Signal"])
            else:
                screen.set_filter(filters_dict=d_filters)

        if start == "":
            start = datetime.now() - timedelta(days=365)
        else:
            start = datetime.strptime(start, cfg.DATE_FORMAT)

        # Output Data
        l_min = []
        l_leg = []
        l_stocks = screen.ScreenerView(verbose=0)

        if len(l_stocks) > 10:
            description = (
                "\nThe limit of stocks to compare with are 10. Hence, 10 random similar stocks will be displayed."
                "\nThe selected list will be: "
            )
            random.shuffle(l_stocks)
            l_stocks = sorted(l_stocks[:10])
            description = description + (", ".join(l_stocks))
            print(description)

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        while l_stocks:
            l_parsed_stocks = []
            for symbol in l_stocks:
                try:
                    df_similar_stock = yf.download(
                        symbol,
                        start=datetime.strftime(start, "%Y-%m-%d"),
                        progress=False,
                        threads=False,
                    )
                    if not df_similar_stock.empty:
                        plt.plot(
                            df_similar_stock.index,
                            df_similar_stock["Adj Close"].values,
                        )
                        l_min.append(df_similar_stock.index[0])
                        l_leg.append(symbol)

                    l_parsed_stocks.append(symbol)
                except Exception as e:
                    error = (
                        f"{e}\nDisregard previous error, which is due to API Rate limits from Yahoo Finance. "
                        f"Because we like '{symbol}', and we won't leave without getting data from it."
                    )
                    embed = discord.Embed(
                        title="ERROR Stocks: [Yahoo Finance] Historical Screener",
                        colour=cfg.COLOR,
                        description=error,
                    )
                    embed.set_author(
                        name=cfg.AUTHOR_NAME,
                        icon_url=cfg.AUTHOR_ICON_URL,
                    )

                    await ctx.send(embed=embed)

            for parsed_stock in l_parsed_stocks:
                l_stocks.remove(parsed_stock)

        if signal:
            plt.title(
                f"Screener Historical Price using {finviz_view.d_signals[signal]} signal"
            )
        else:
            plt.title(f"Screener Historical Price using {signal} preset")

        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.legend(l_leg)
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        # ensures that the historical data starts from same datapoint
        plt.xlim([max(l_min), df_similar_stock.index[-1]])

        plt.savefig("scr_historical.png")
        uploaded_image = gst_imgur.upload_image("scr_historical.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: [Yahoo Finance] Historical Screener"
        embed = discord.Embed(title=title, description=description, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("scr_historical.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [Yahoo Finance] Historical Screener",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
