import logging

import disnake
import pandas as pd

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import finviz_model
from openbb_terminal.helper_funcs import lambda_long_number_format

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def performance_command(economy_group="sector"):
    """Performance of sectors, industry, country [Finviz]"""

    d_economy_group = {
        "sector": "Sector",
        "industry": "Industry",
        "basic_materials": "Industry (Basic Materials)",
        "communication_services": "Industry (Communication Services)",
        "consumer_cyclical": "Industry (Consumer Cyclical)",
        "consumer_defensive": "Industry (Consumer Defensive)",
        "energy": "Industry (Energy)",
        "financial": "Industry (Financial)",
        "healthcare": "Industry (Healthcare)",
        "industrials": "Industry (Industrials)",
        "real_estate": "Industry (Real Estate)",
        "technology": "Industry (Technology)",
        "utilities": "Industry (Utilities)",
        "country": "Country (U.S. listed stocks only)",
        "capitalization": "Capitalization",
    }

    # Debug user input
    if imps.DEBUG:
        logger.debug("econ-performance %s", economy_group)

    # Select default group
    if not economy_group:
        if imps.DEBUG:
            logger.debug("Use default economy_group: 'sector'")
        economy_group = "sector"

    # Check for argument
    possible_groups = list(d_economy_group.keys())

    if economy_group not in possible_groups:
        possible_group_list = ", ".join(possible_groups)
        raise Exception(f"Select a valid group from {possible_group_list}")  # nosec

    group = d_economy_group[economy_group]

    # Retrieve data
    df_group = finviz_model.get_valuation_performance_data(group, "performance")

    # Check for argument
    if df_group.empty:
        raise Exception("No available data found")

    # Output data
    df = pd.DataFrame(df_group)

    df["Volume"] = df["Volume"] / 1_000_000
    df["Avg Volume"] = df["Avg Volume"] / 1_000_000

    formats = {
        "Perf Month": "{:.2f}",
        "Perf Quart": "{:.2f}%",
        "Perf Half": "{:.2f}%",
        "Perf Year": "{:.2f}%",
        "Perf YTD": "{:.2f}%",
        "Avg Volume": "{:.0f}M",
        "Change": "{:.2f}%",
        "Volume": "{:.0f}M",
    }
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.set_axis(
        [
            "Name",
            "Week",
            "Month",
            "3 Mouth",
            "6 Mouth",
            "1 Year",
            "YTD",
            "Recom",
            "Avg Volume",
            "Rel Volume",
            "Change",
            "Volume",
        ],
        axis="columns",
    )
    df.set_index("Name", inplace=True)
    df = df.fillna("-")
    df = df.applymap(lambda x: lambda_long_number_format(x, 2))

    title = f"Economy: [WSJ] Performance {group}"

    dindex = len(df.index)
    if dindex > 2:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 2
        df_pg, embeds_img, images_list = pd.DataFrame(), [], []
        while i < dindex:
            df_pg = df.iloc[i:end]
            df_pg.append(df_pg)
            fig = imps.plot_df(
                df_pg.transpose(),
                fig_size=(800, 720),
                col_width=[6, 10],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(cells=(dict(align=["center", "right"])))
            imagefile = "econ_performance.png"
            imagefile = imps.save_image(imagefile, fig)

            if imps.IMAGES_URL or not imps.IMG_HOST_ACTIVE:
                image_link = imps.multi_image(imagefile)
                images_list.append(imagefile)
            else:
                image_link = imps.multi_image(imagefile)

            embeds_img.append(
                f"{image_link}",
            )
            embeds.append(
                disnake.Embed(
                    title=title,
                    colour=imps.COLOR,
                ),
            )
            i2 += 1
            i += 2
            end += 2

        # Author/Footer
        for i in range(0, i2):
            embeds[i].set_author(
                name=imps.AUTHOR_NAME,
                url=imps.AUTHOR_URL,
                icon_url=imps.AUTHOR_ICON_URL,
            )
            embeds[i].set_footer(
                text=imps.AUTHOR_NAME,
                icon_url=imps.AUTHOR_ICON_URL,
            )

        i = 0
        for i in range(0, i2):
            embeds[i].set_image(url=embeds_img[i])

            i += 1
        embeds[0].set_footer(text=f"Page 1 of {len(embeds)}")
        choices = [
            disnake.SelectOption(label="Home", value="0", emoji="🟢"),
        ]

        output = {
            "view": imps.Menu,
            "title": title,
            "embed": embeds,
            "choices": choices,
            "embeds_img": embeds_img,
            "images_list": images_list,
        }
    else:
        fig = imps.plot_df(
            df.transpose(),
            fig_size=(800, 720),
            col_width=[6, 10],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "right"])))
        imagefile = imps.save_image("econ_performance.png", fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
