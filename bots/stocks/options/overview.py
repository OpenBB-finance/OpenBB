import logging
import os
import time
from functools import reduce
from multiprocessing import Pool

import disnake
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.options import op_helpers, yfinance_model
from openbb_terminal.stocks.options.barchart_model import get_options_info

# pylint: disable=W0640,W0631
logger = logging.getLogger(__name__)


def unpack(tup):

    return reduce(np.append, tup)


column_map = {"openInterest": "oi", "volume": "vol", "impliedVolatility": "iv"}
columns = [
    "strike",
    "bid",
    "ask",
    "volume",
    "openInterest",
    "impliedVolatility",
]


# pylint: disable=R0912,R0913,R0914,R0915
@log_start_end(log=logger)
def options_run(
    ticker,
    url,
    expiry,
    dates,
    df_bcinfo,
    calls,
    puts,
    df_opt,
    current_price,
    min_strike,
    max_strike,
    min_strike2,
    max_strike2,
    max_pain,
):
    """Options Overview"""
    titles, reports, embeds, embeds_img, choices, images_list = [], [], [], [], [], []
    fig = go.Figure()

    dmax = df_opt[["OI_call", "OI_put"]].values.max()
    dmin = df_opt[["OI_call", "OI_put"]].values.min()
    fig.add_trace(
        go.Scatter(
            x=df_opt.index,
            y=df_opt["OI_call"],
            name="Calls",
            mode="lines+markers",
            line=dict(color=imps.PLT_SCAT_INCREASING, width=3),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_opt.index,
            y=df_opt["OI_put"],
            name="Puts",
            mode="lines+markers",
            line=dict(color=imps.PLT_SCAT_DECREASING, width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[current_price, current_price],
            y=[dmin, dmax],
            mode="lines",
            line=dict(color=imps.PLT_SCAT_PRICE, width=2),
            name="Current Price",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[max_pain, max_pain],
            y=[dmin, dmax],
            mode="lines",
            line=dict(color="grey", width=3, dash="dash"),
            name=f"Max Pain: {max_pain}",
        )
    )
    if imps.PLT_WATERMARK:
        fig.add_layout_image(imps.PLT_WATERMARK)
    fig.update_xaxes(
        range=[min_strike, max_strike],
        constrain="domain",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=60, b=20),
        template=imps.PLT_SCAT_STYLE_TEMPLATE,
        title=f"Open Interest for {ticker.upper()} expiring {expiry}",
        title_x=0.5,
        legend_title="",
        xaxis_title="Strike",
        yaxis_title="Open Interest (1k)",
        xaxis=dict(
            rangeslider=dict(visible=False),
        ),
        font=imps.PLT_FONT,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            font_size=8,
            bgcolor="rgba(0, 0, 0, 0)",
            x=0.01,
        ),
        dragmode="pan",
    )

    imagefile = "opt-oi.png"

    plt_link = ""
    if imps.INTERACTIVE:
        plt_link = imps.inter_chart(fig, imagefile, callback=False)
        reports.append(plt_link)

    imagefile = imps.image_border(imagefile, fig=fig)

    if imps.IMAGES_URL or not imps.IMG_HOST_ACTIVE:
        image_link_oi = imps.multi_image(imagefile)
        images_list.append(imagefile)
    else:
        image_link_oi = imps.multi_image(imagefile)

    calls_df = calls[columns].rename(columns=column_map)
    calls_df = calls_df[calls_df["strike"] >= min_strike2]
    calls_df = calls_df[calls_df["strike"] <= max_strike2]
    calls_df["iv"] = pd.to_numeric(calls_df["iv"].astype(float))

    formats = {"iv": "{:.2f}"}
    for col, f in formats.items():
        calls_df[col] = calls_df[col].map(lambda x: f.format(x))

    calls_df = calls_df.fillna("")
    calls_df.set_index("strike", inplace=True)

    if "^" not in ticker:
        if "-" in df_bcinfo.iloc[0, 1]:
            iv = f"```diff\n-             {df_bcinfo.iloc[0, 1]}\n```"
        else:
            iv = f"```yaml\n              {df_bcinfo.iloc[0, 1]}\n```"

    pfix, sfix = f"{ticker.upper()} ", f" expiring {expiry}"
    if expiry == dates[0]:
        pfix = f"{ticker.upper()} Weekly "
        sfix = ""

    titles.append(
        f"{ticker.upper()} Overview",
    )
    titles.append(
        f"{pfix}Open Interest{sfix}",
    )
    embeds.append(
        disnake.Embed(
            title=f"{ticker.upper()} Overview",
            color=imps.COLOR,
        ),
    )
    embeds.append(
        disnake.Embed(
            title=f"{pfix}Open Interest{sfix}",
            description=plt_link,
            colour=imps.COLOR,
        ),
    )
    choices.append(
        disnake.SelectOption(label=f"{ticker.upper()} Overview", value="0", emoji="🟢"),
    )
    choices.append(
        disnake.SelectOption(label=f"{pfix}Open Interest{sfix}", value="1", emoji="🟢"),
    )

    i, i2, end = 0, 0, 20
    df_calls = []
    dindex = len(calls_df.index)
    while i < dindex:
        df_calls = calls_df.iloc[i:end]
        df_calls.append(df_calls)
        figc = imps.plot_df(
            df_calls,
            fig_size=(1000, (40 + (40 * 20))),
            col_width=[3, 3, 3, 3],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        imagefile = "opt-calls.png"
        imagefile = imps.save_image(imagefile, figc)

        if imps.IMAGES_URL or not imps.IMG_HOST_ACTIVE:
            image_link = imps.multi_image(imagefile)
            images_list.append(imagefile)
        else:
            image_link = imps.multi_image(imagefile)

        embeds_img.append(
            f"{image_link}",
        )
        titles.append(
            f"{pfix}Calls{sfix}",
        )
        embeds.append(
            disnake.Embed(
                title=f"{pfix}Calls{sfix}",
                colour=imps.COLOR,
            ),
        )
        i2 += 1
        i += 20
        end += 20

    # Add Calls page field
    i, page, puts_page = 2, 0, 3
    i3 = i2 + 2
    choices.append(
        disnake.SelectOption(label="Calls Page 1", value="2", emoji="🟢"),
    )
    for i in range(2, i3):
        page += 1
        puts_page += 1

        embeds[i].add_field(name=f"Calls Page {page}", value="_ _", inline=True)

    puts_df = puts[columns].rename(columns=column_map)

    puts_df = puts_df[puts_df["strike"] >= min_strike2]
    puts_df = puts_df[puts_df["strike"] <= max_strike2]

    puts_df["iv"] = pd.to_numeric(puts_df["iv"].astype(float))

    formats = {"iv": "{:.2f}"}
    for col, f in formats.items():
        puts_df[col] = puts_df[col].map(lambda x: f.format(x))  # pylint: disable=W0640

    puts_df = puts_df.fillna("")
    puts_df.set_index("strike", inplace=True)

    pfix, sfix = f"{ticker.upper()} ", f" expiring {expiry}"
    if expiry == dates[0]:
        pfix = f"{ticker.upper()} Weekly "
        sfix = ""

    # Puts Pages
    i, end = 0, 20
    df_puts = []

    dindex = len(puts_df.index)
    while i < dindex:
        df_puts = puts_df.iloc[i:end]
        df_puts.append(df_puts)
        figp = imps.plot_df(
            df_puts,
            fig_size=(1000, (40 + (40 * 20))),
            col_width=[3, 3, 3, 3],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        imagefile = "opt-puts.png"
        imagefile = imps.save_image(imagefile, figp)

        if imps.IMAGES_URL or not imps.IMG_HOST_ACTIVE:
            image_link = imps.multi_image(imagefile)
            images_list.append(imagefile)
        else:
            image_link = imps.multi_image(imagefile)

        embeds_img.append(
            f"{image_link}",
        )
        titles.append(
            f"{pfix}Puts{sfix}",
        )
        embeds.append(
            disnake.Embed(
                title=f"{pfix}Puts{sfix}",
                colour=imps.COLOR,
            ),
        )
        i2 += 1
        i += 20
        end += 20

    # Add Puts page field
    i, page = 0, 0
    puts_page -= 1
    i2 += 2
    choices.append(
        disnake.SelectOption(label="Puts Page 1", value=f"{puts_page}", emoji="🟢"),
    )
    for i in range(puts_page, i2):
        page += 1
        embeds[i].add_field(name=f"Puts Page {page}", value="_ _", inline=True)

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

    # Set images to Pages
    i = 0
    img_i = 0
    embeds[1].set_image(url=image_link_oi)
    for i in range(2, i2):
        embeds[i].set_image(url=embeds_img[img_i])
        img_i += 1
        i += 1

    if url:
        embeds[0].set_thumbnail(url=f"{url}")
    else:
        embeds[0].set_thumbnail(url=imps.AUTHOR_ICON_URL)

    # Overview Section
    if "^" not in ticker:
        reports.append(
            f"{'':^5}*{df_bcinfo.iloc[0, 0]:^25}*{'':^5}*{df_bcinfo.iloc[1, 0]:^25}*{'':^5}\n"
        )
        reports.append(
            f"{'':^8}{df_bcinfo.iloc[0, 1]:^25}{'':^5}{df_bcinfo.iloc[1, 1]:^25}\n"
        )
        i, i2 = 2, 3
        while i < 11:
            text = (
                f"{'':^5}*{df_bcinfo.iloc[i, 0]:^25}*{'':^5}*{df_bcinfo.iloc[i2, 0]:^25}*{'':^5}\n"
                f"{'':^5}{df_bcinfo.iloc[i, 1]:^30}{'':^5}{df_bcinfo.iloc[i2, 1]:^25}{'':^10}\n"
            )
            reports.append(text)
            i += 1
            i2 += 1

        embeds[0].add_field(name=f"{df_bcinfo.iloc[0, 0]}", value=iv, inline=False)
        embeds[0].add_field(
            name=f"•{df_bcinfo.iloc[1, 0]}",
            value=f"```css\n{df_bcinfo.iloc[1, 1]}\n```",
            inline=True,
        )

        for N in range(2, 6):
            embeds[0].add_field(
                name=f"_ _ _ _ _ _ _ _ _ _ •{df_bcinfo.iloc[N, 0]}",
                value=f"```css\n{df_bcinfo.iloc[N, 1]}\n```",
                inline=True,
            )

        embeds[0].add_field(name="_ _", value="_ _", inline=False)
        for N in range(6, 8):
            embeds[0].add_field(
                name=f"_ _ _ _ _ _ _ _ _ _ •{df_bcinfo.iloc[N, 0]}",
                value=f"```css\n{df_bcinfo.iloc[N, 1]}\n```",
                inline=True,
            )

        embeds[0].add_field(name="_ _", value="_ _", inline=False)
        for N in range(8, 10):
            embeds[0].add_field(
                name=f"_ _ _ _ _ _ _ _ _ _ •{df_bcinfo.iloc[N, 0]}",
                value=f"```css\n{df_bcinfo.iloc[N, 1]}\n```",
                inline=True,
            )

        embeds[0].add_field(name="_ _", value="_ _", inline=False)
        for N in range(10, 12):
            embeds[0].add_field(
                name=f"_ _ _ _ _ _ _ _ _ _ •{df_bcinfo.iloc[N, 0]}",
                value=f"```css\n{df_bcinfo.iloc[N, 1]}\n```",
                inline=True,
            )

        embeds[0].set_footer(text=f"Page 1 of {len(embeds)}")

    return titles, reports, embeds, choices, embeds_img, images_list


@log_start_end(log=logger)
def options_data(
    ticker: str = None,
    expiry: str = None,
    min_sp: float = None,
    max_sp: float = None,
):

    # Debug
    if imps.DEBUG:
        logger.debug("opt overview %s %s %s %s", ticker, expiry, min_sp, max_sp)

    # Check for argument
    if ticker is None:
        raise Exception("Stock ticker is required")

    # Get options info/dates, Look for logo_url
    if "^" not in ticker:
        df_bcinfo = get_options_info(ticker)  # Barchart Options IV Overview
        df_bcinfo = df_bcinfo.fillna("")
        df_bcinfo = df_bcinfo.set_axis(
            [
                " ",
                "",
            ],
            axis="columns",
        )
        df_bcinfo[""] = df_bcinfo[""].str.lstrip()
    else:
        df_bcinfo = ""

    dates = yfinance_model.option_expirations(ticker)  # Expiration dates
    tup = f"{ticker.upper()}"
    url = yf.Ticker(tup).info["logo_url"]
    url += "?raw=true" if url else ""

    if not dates:
        raise Exception("Stock ticker is invalid")

    options = yfinance_model.get_option_chain(ticker, str(expiry))
    calls = options.calls.fillna(0)
    puts = options.puts.fillna(0)

    current_price = yfinance_model.get_price(ticker)

    min_strike2 = np.percentile(calls["strike"], 1)
    max_strike2 = np.percentile(calls["strike"], 100)
    min_strike = 0.75 * current_price
    max_strike = 1.95 * current_price

    if len(calls) > 40:
        min_strike = 0.75 * current_price
        max_strike = 1.25 * current_price

    if min_sp:
        min_strike = min_sp
        min_strike2 = min_sp
    if max_sp:
        max_strike = max_sp
        max_strike2 = max_sp
        if min_sp > max_sp:  # type: ignore
            min_sp, max_sp = max_strike2, min_strike2

    call_oi = calls.set_index("strike")["openInterest"] / 1000
    put_oi = puts.set_index("strike")["openInterest"] / 1000

    df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
    df_opt = df_opt.rename(
        columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
    )

    max_pain = op_helpers.calculate_max_pain(df_opt)
    data = [
        ticker,
        url,
        expiry,
        dates,
        df_bcinfo,
        calls,
        puts,
        df_opt,
        current_price,
        min_strike,
        max_strike,
        min_strike2,
        max_strike2,
        max_pain,
    ]
    return data


@log_start_end(log=logger)
def run(
    ticker: str = None,
    expiry: str = None,
    min_sp: float = None,
    max_sp: float = None,
):
    cpus = os.cpu_count()
    data = options_data(ticker, expiry, min_sp, max_sp)
    with Pool(processes=cpus) as p:
        time.sleep(1)
        titles, reports, embeds, choices, embeds_img, images_list = zip(
            *p.starmap(options_run, [(*data,)], chunksize=1)
        )

    return (
        unpack(titles),
        unpack(reports),
        unpack(embeds),
        unpack(choices),
        unpack(embeds_img),
        unpack(images_list),
    )


@log_start_end(log=logger)
def overview_command(
    ticker: str = None,
    expiry: str = None,
    min_sp: float = None,
    max_sp: float = None,
):
    """Options Overview"""

    titles, reports, embeds, choices, embeds_img, images_list = run(
        ticker, expiry, min_sp, max_sp
    )
    description = f"```\n{''.join(reports)}\n```"

    return {
        "view": imps.Menu,
        "titles": titles,
        "description": description,
        "embed": embeds,
        "choices": choices,
        "embeds_img": embeds_img,
        "images_list": images_list,
    }
