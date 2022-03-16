import difflib
import logging
from collections import OrderedDict

import numpy as np
import plotly.graph_objects as go
import yfinance

import bots.config_discordbot as cfg
from bots import helpers
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.sector_industry_analysis import financedatabase_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def metric_command(
    finance_key: str,
    finance_metric: str,
    ticker: str = "",
):
    """Display financials bars comparing sectors, industry, analysis, countries, market cap and excluding exchanges.

    Parameters
    ----------
    finance_key: str
        Select finance key from Yahoo Finance(e.g. financialData, defaultKeyStatistics, summaryProfile)
    finance_metric: str
        Select finance metric from Yahoo Finance (e.g. operatingCashflow, revenueGrowth, ebitda, freeCashflow)
    ticker: str
        Company ticker to use as the basis.
    """
    logger.info("metrics")
    exclude_exchanges: bool = True
    limit: int = 10
    ticker = ticker.lower()
    if ticker:
        data = yfinance.utils.get_json(f"https://finance.yahoo.com/quote/{ticker}")

        if "summaryProfile" in data:
            country = data["summaryProfile"]["country"]
            if country not in financedatabase_model.get_countries():
                similar_cmd = difflib.get_close_matches(
                    country,
                    financedatabase_model.get_countries(),
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    country = similar_cmd[0]
            sector = data["summaryProfile"]["sector"]
            if sector not in financedatabase_model.get_sectors():
                similar_cmd = difflib.get_close_matches(
                    sector,
                    financedatabase_model.get_sectors(),
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    sector = similar_cmd[0]
            industry = data["summaryProfile"]["industry"]
            if industry not in financedatabase_model.get_industries():
                similar_cmd = difflib.get_close_matches(
                    industry,
                    financedatabase_model.get_industries(),
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    industry = similar_cmd[0]
            mktcap = ""

    stocks_data = financedatabase_model.get_stocks_data(
        country, sector, industry, mktcap, exclude_exchanges
    )

    metric_data = {}
    for symbol in list(stocks_data.keys()):
        if finance_key in stocks_data[symbol] and "quoteType" in stocks_data[symbol]:
            stock_name = stocks_data[symbol]["quoteType"]["longName"]
            metric = (
                stocks_data[symbol][finance_key][finance_metric]
                if stocks_data[symbol][finance_key] is not None
                and finance_metric in stocks_data[symbol][finance_key]
                else None
            )
            if metric and stock_name:
                metric_data[stock_name] = (metric, symbol)

    if len(metric_data) > 1:

        metric_data = dict(
            OrderedDict(
                sorted(metric_data.items(), key=lambda t: t[1][0], reverse=True)
            )
        )

        company_names = list()
        company_metrics = list()
        company_tickers = list()
        for name, metric in metric_data.items():
            company_names.append(name)
            company_metrics.append(metric[0])
            company_tickers.append(metric[1])

        company_name = np.array(company_names)[:limit]
        company_metric = np.array(company_metrics)[:limit]
        company_ticker = np.array(company_tickers)[:limit]

        magnitude = 0
        while max(company_metric) > 1_000 or abs(min(company_metric)) > 1_000:
            company_metric = np.divide(company_metric, 1_000)
            magnitude += 1

        # check if the value is a percentage
        if (magnitude == 0) and all(company_metric >= 0) and all(company_metric <= 1):
            unit = "%"
            company_metric = company_metric * 100

        else:
            unit = " KMBTP"[magnitude]

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

        fig = go.Figure()

        i = 0
        for name, metric, ticker in zip(
            company_name[::-1], company_metric[::-1], company_ticker[::-1]
        ):
            if len(name.split(" ")) > 6 and len(name) > 40:
                name = (
                    f'{" ".join(name.split(" ")[:4])}\n{" ".join(name.split(" ")[4:])}'
                )
            df_name = []
            df_metric = []
            df_ticker = []
            df_name.append(name)
            df_metric.append(metric)
            df_ticker.append(ticker)
            fig.add_trace(
                go.Bar(
                    name=ticker,
                    y=[name],
                    x=[metric],
                    orientation="h",
                    marker=dict(
                        color=colors[i],
                        line=dict(color="rgb(248, 248, 249)", width=1),
                    ),
                ),
            )
            i += 1

        metric_title = (
            "".join(
                " " + char if char.isupper() else char.strip()
                for char in finance_metric
            )
            .strip()
            .capitalize()
        )

        benchmark = np.median(company_metric)
        if unit != " ":
            units = f" [{unit}] "
        else:
            units = " "

        title = f"{metric_title.capitalize()}{units}with benchmark of {benchmark:.2f} {unit}<br>"
        title += mktcap + " cap companies " if mktcap else "Companies "
        if industry:
            title += f"in {industry} industry<br>"
        elif sector:
            title += f"in {sector} sector<br>"

        if country:
            title += f"in {country}"
            title += " " if (industry or sector) else "<br>"

        title += (
            "(excl. data from international exchanges)"
            if exclude_exchanges
            else "(incl. data from international exchanges)"
        )
        fig.add_vline(
            x=benchmark,
            fillcolor="grey",
            opacity=1,
            layer="below",
            line_width=3,
            line=dict(color="grey", dash="dash"),
        )
        if cfg.PLT_WATERMARK:
            fig.add_layout_image(cfg.PLT_WATERMARK)
        fig.update_layout(
            margin=dict(l=40, r=0, t=100, b=20),
            template=cfg.PLT_CANDLE_STYLE_TEMPLATE,
            title=title,
            colorway=colors,
            font=cfg.PLT_FONT,
            legend={"traceorder": "reversed"},
        )
        imagefile = "sia_metrics.png"

        # Check if interactive settings are enabled
        plt_link = ""
        if cfg.INTERACTIVE:
            plt_link = helpers.inter_chart(fig, imagefile, callback=False)

        fig.update_layout(
            width=800,
            height=500,
        )

        imagefile = helpers.image_border(imagefile, fig=fig)

        return {
            "title": "Consumer Prices Index",
            "description": plt_link,
            "imagefile": imagefile,
        }

    if len(metric_data) == 1:
        raise Exception(
            f"Only 1 company found '{list(metric_data.keys())[0]}'. No barchart will be depicted.\n"
        )
    else:
        raise Exception("No company found. No barchart will be depicted.\n")
