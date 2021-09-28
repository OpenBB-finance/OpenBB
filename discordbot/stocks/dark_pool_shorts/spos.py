import discord
import os
import config_discordbot as cfg
from discordbot import gst_imgur
from matplotlib import pyplot as plt
from gamestonk_terminal.config_plot import PLOT_DPI

from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model


async def spos_command(ctx, arg):
    # Help
    if arg == "-h" or arg == "help":
        help_txt = "Plot net short position. [Source: Stockgrid]\n"
        help_txt += "\nPossible arguments:\n"
        help_txt += "<TICKER> Stock ticker. REQUIRED!\n"
        embed = discord.Embed(
            title="Stocks: [Stockgrid] Net Short vs Position HELP",
            description=help_txt,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    else:
        # Parse argument
        ticker = arg.upper()

        plt.ion()
        title = "Stocks: [Stockgrid] Net Short vs Position " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        df = stockgrid_model.get_net_short_position(ticker)
        fig = plt.figure(dpi=PLOT_DPI)

        ax = fig.add_subplot(111)
        ax.bar(
            df["dates"],
            df["dollar_net_volume"] / 1_000,
            color="r",
            alpha=0.4,
            label="Net Short Vol. (1k $)",
        )
        ax.set_ylabel("Net Short Vol. (1k $)")

        ax2 = ax.twinx()
        ax2.plot(
            df["dates"].values,
            df["dollar_dp_position"],
            c="tab:blue",
            label="Position (1M $)",
        )
        ax2.set_ylabel("Position (1M $)")

        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left")

        ax.grid()
        plt.title(f"Net Short Vol. vs Position for {ticker}")
        plt.gcf().autofmt_xdate()
        file_name = ticker + "_spos.png"
        plt.savefig(file_name)
        plt.close("all")
        uploaded_image = gst_imgur.upload_image(file_name, title="something")
        image_link = uploaded_image.link
        embed.set_image(url=image_link)
        os.remove(file_name)

        await ctx.send(embed=embed)
