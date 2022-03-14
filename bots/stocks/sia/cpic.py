import textwrap
from collections import OrderedDict

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import bots.config_discordbot as cfg
from bots import helpers
from gamestonk_terminal.stocks.sector_industry_analysis import financedatabase_model


def cpic_command(
    industry: str,
    mktcap: str = "",
    exclude_exchanges: bool = False,
    export: str = "",
    raw: bool = False,
    max_countries_to_display: int = 15,
    min_pct_to_display_country: float = 0.015,
):
    """Display number of companies per country in a specific industry. [Source: Finance Database]

    Parameters
    ----------
    industry: str
        Select industry to get number of companies by each country
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges
    export: str
        Format to export data as
    raw: bool
        Output all raw data
    max_countries_to_display: int
        Maximum number of countries to display
    min_pct_to_display_country: float
        Minimum percentage to display country
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    companies_per_country = financedatabase_model.get_companies_per_country_in_industry(
        industry, mktcap, exclude_exchanges
    )

    companies_per_country = dict(
        OrderedDict(
            sorted(companies_per_country.items(), key=lambda t: t[1], reverse=True)
        )
    )

    for key, value in companies_per_country.copy().items():
        if value == 0:
            del companies_per_country[key]

    if not companies_per_country:
        raise Exception("No companies found with these parameters!\n")

    df = pd.DataFrame.from_dict(companies_per_country, orient="index")
    df.index.name = "Country"
    df.columns = ["Number of companies"]
    df["Number of companies"] = df["Number of companies"].astype(int)

    title = mktcap + " cap companies " if mktcap else "Companies "
    title += f"per country in {industry} industry"
    title += " excl. exchanges" if exclude_exchanges else " incl. all exchanges"
    title = textwrap.fill(title, 40)
    title_plot = textwrap.indent(text=title, prefix="<br>")

    if raw:
        output = {
            "title": "Consumer Prices Index",
            "description": f"{df}",
        }
    else:

        if len(companies_per_country) > 1:
            total_num_companies = sum(companies_per_country.values())
            min_companies_to_represent = round(
                min_pct_to_display_country * total_num_companies
            )
            filter_countries_to_display = (
                np.array(list(companies_per_country.values()))
                > min_companies_to_represent
            )

            if any(filter_countries_to_display):

                if not all(filter_countries_to_display):
                    num_countries_to_display = np.where(~filter_countries_to_display)[
                        0
                    ][0]

                    if num_countries_to_display < max_countries_to_display:
                        max_countries_to_display = num_countries_to_display

            else:
                raise Exception(
                    "The minimum threshold percentage specified is too high, thus it will be ignored."
                )

            if len(companies_per_country) > max_countries_to_display:

                companies_per_country_sliced = dict(
                    list(companies_per_country.items())[: max_countries_to_display - 1]
                )
                companies_per_country_sliced["Others"] = sum(
                    dict(
                        list(companies_per_country.items())[
                            max_countries_to_display - 1 :
                        ]
                    ).values()
                )

                legend, values = zip(*companies_per_country_sliced.items())

            else:
                legend, values = zip(*companies_per_country.items())

            fig = go.Figure()
            colors = [
                "#ffed00",
                "#ef7d00",
                "#e4003a",
                "#c13246",
                "#822661",
                "#48277c",
                "#005ca9",
                "#00aaff",
                "#9b30d9",
                "#af005f",
                "#5f00af",
                "#af87ff",
            ]

            fig.add_trace(
                go.Pie(
                    labels=legend,
                    values=values,
                    textinfo="label+percent",
                    showlegend=False,
                )
            )
            fig.update_traces(
                textposition="outside",
                textfont_size=15,
                marker=dict(
                    colors=colors,
                    line=dict(color="#F5EFF3", width=0.8),
                ),
            )
            if cfg.PLT_WATERMARK:
                fig.add_layout_image(cfg.PLT_WATERMARK)
            fig.update_layout(
                margin=dict(l=40, r=0, t=80, b=40),
                title=dict(
                    text=title_plot,
                    y=1,
                    x=0.5,
                    xanchor="center",
                    yanchor="top",
                ),
                template=cfg.PLT_CANDLE_STYLE_TEMPLATE,
                colorway=colors,
                font=cfg.PLT_FONT,
            )

        elif len(companies_per_country) == 1:
            raise Exception(
                f"Only 1 sector found '{list(companies_per_country.keys())[0]}'. No pie chart will be depicted."
            )
        else:
            raise Exception("No sector found. No pie chart will be depicted.")

        imagefile = "sia_cpic.png"

        # Check if interactive settings are enabled
        plt_link = ""
        if cfg.INTERACTIVE:
            plt_link = helpers.inter_chart(fig, imagefile, callback=False)

        fig.update_layout(
            width=800,
            height=500,
        )

        imagefile = helpers.image_border(imagefile, fig=fig)

        output = {
            "title": "Consumer Prices Index",
            "description": plt_link,
            "imagefile": imagefile,
        }

    return output
