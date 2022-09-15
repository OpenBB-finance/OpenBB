import io
import datetime
from typing import Dict
import numpy as np

import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pandas as pd

# import sys
# sys.path.append('../../')

from openbb_terminal.api import widgets
from openbb_terminal.api import openbb
from openbb_terminal.helper_classes import TerminalStyle

# Detect if prediction capabilities are present. If they are not, disable prediction in the rest of the script
# so that the report can still be generated without prediction results.
# predictions = True
# try:
#     openbb.stocks.pred.models
# except Exception as e:
#     predictions = False

# TODO Fix predictions virtual path on api refactored

predictions = False

theme = TerminalStyle("light", "light", "light")
stylesheet = widgets.html_report_stylesheet()

parameters = {"symbol": "AAPL", "report_name": "Equity Report for AAPL"}


def run_report(symbol: str = "", report_name: str = ""):
    """
    Runs the report
    """

    if "." in symbol:
        import sys

        sys.exit(0)

    ticker_data = openbb.stocks.load(
        symbol=symbol,
        start_date=datetime.datetime.now() - datetime.timedelta(days=18 * 30),
    )
    ticker_data = openbb.stocks.process_candle(df=ticker_data)

    author = ""
    report_title = f"Investment Research Report on {symbol.upper()}"
    report_date = datetime.datetime.now().strftime("%d %B, %Y")
    report_time = datetime.datetime.now().strftime("%H:%M")
    report_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    info = openbb.stocks.fa.info(symbol=symbol).transpose()

    if info["Long business summary"][0] != "NA":
        overview = info["Long business summary"][0]
    else:
        overview = info["Long name"][0]

    (
        df_year_estimates,
        df_quarter_earnings,
        df_quarter_revenues,
    ) = openbb.stocks.dd.est(symbol=symbol)

    display_year = sorted(df_year_estimates.columns.tolist())[:3]
    df_year_estimates = df_year_estimates[display_year].head(5)

    tables = openbb.etf.news(info["Short name"][0], 5)
    for table in tables:
        table[0].loc["link"] = (
            table[0].loc["link"].apply(lambda x: f'<a href="{x}">{x}</a>')
        )

    quote_data = openbb.stocks.quote(symbol)

    (
        df_major_holders,
        df_institutional_shareholders,
        df_mutualfund_shareholders,
    ) = openbb.stocks.fa.shrs(symbol)
    df_institutional_shareholders.index += 1

    df_sec_filings = openbb.stocks.dd.sec(symbol=symbol)[
        ["Type", "Category", "Link"]
    ].head(5)
    df_sec_filings["Link"] = df_sec_filings["Link"].apply(
        lambda x: f'<a href="{x}">{x}</a>'
    )

    df_analyst = openbb.stocks.dd.analyst(symbol=symbol)
    if not df_analyst.empty:
        if "target" in df_analyst.columns:
            df_analyst["target_to"] = df_analyst["target_to"].combine_first(
                df_analyst["target"]
            )
        df_analyst = df_analyst[["category", "analyst", "rating", "target_to"]].rename(
            columns={
                "category": "Category",
                "analyst": "Analyst",
                "rating": "Rating",
                "target_to": "Price Target",
            }
        )

    df_rating = openbb.stocks.dd.rating(symbol)
    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.options.pcr(
        symbol,
        window=30,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    pcr_chart = f.getvalue().decode("utf-8")

    expiry_dates = openbb.stocks.options.option_expirations(symbol)
    exp = expiry_dates[0]

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.options.vol_yf(
        symbol,
        exp,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    vol_chart = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 8), dpi=150)
    openbb.stocks.options.voi_yf(
        symbol,
        exp,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    voi_chart = f.getvalue().decode("utf-8")

    current_price = float(info["Previous close"][0])
    options_df = openbb.stocks.options.chains_yf(
        symbol, exp, min_sp=0.9 * current_price, max_sp=1.1 * current_price
    )
    options_df.reset_index(drop=True, inplace=True)

    fig, ax1 = plt.subplots(figsize=(11, 5), dpi=150)
    ax2 = ax1.twinx()
    openbb.stocks.dps.spos(
        symbol=symbol,
        limit=84,
        raw=False,
        export="",
        external_axes=[ax1, ax2],
        chart=True,
    )
    fig.tight_layout()

    f = io.BytesIO()
    fig.savefig(f, format="svg")
    net_short_position = f.getvalue().decode("utf-8")

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(11, 5), dpi=150)
    openbb.stocks.dps.dpotc(symbol=symbol, external_axes=[ax1, ax2], chart=True)
    fig.tight_layout()

    f = io.BytesIO()
    fig.savefig(f, format="svg")
    dark_pools = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.gov.gtrades(
        symbol,
        past_transactions_months=12,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    gtrades_chart = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.gov.contracts(
        symbol,
        past_transaction_days=365,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    gov_contracts_chart = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.ba.mentions(
        symbol,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    google_mentions_chart = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.ba.regions(
        symbol,
        limit=10,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    google_regions_chart = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.ba.cramer_ticker(
        symbol,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    cramer_chart = f.getvalue().decode("utf-8")

    similar_companies = openbb.stocks.ca.polygon_peers(symbol)
    similar_companies.append(symbol)

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.ca.hist(
        similar_companies,
        external_axes=[
            ax,
        ],
        normalize=False,
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    historical_similar = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.ca.hcorr(
        similar_companies,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    hcorr_similar = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.ca.volume(
        similar_companies,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    vol_similar = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.ca.scorr(
        similar_companies,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    scorr_similar = f.getvalue().decode("utf-8")

    income_comparison = openbb.stocks.ca.income(similar_companies)

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.gov.histcont(
        symbol,
        external_axes=[
            ax,
        ],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    gov_histcont_chart = f.getvalue().decode("utf-8")

    # Remove for now as it doesn't always work

    # df_related_queries = openbb.stocks.ba.queries(symbol)
    # df_related_queries.index += 1
    # df_related_queries.index

    # Remove for now as it doesn't always work

    # df_rising_queries = openbb.stocks.ba.rise(symbol)
    # df_rising_queries.index += 1
    # df_rising_queries

    df_lobbying = openbb.stocks.gov.lobbying(symbol, limit=5)

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(11, 5), dpi=150)
    ax3 = ax1.twinx()
    openbb.stocks.dps.psi_sg(
        symbol=symbol,
        external_axes=[ax1, ax2, ax3],
        chart=True,
    )
    fig.tight_layout()

    f = io.BytesIO()
    fig.savefig(f, format="svg")
    price_vs_short_interest = f.getvalue().decode("utf-8")

    fig, (candles, volume) = plt.subplots(nrows=2, ncols=1, figsize=(11, 5), dpi=150)
    openbb.stocks.candle(
        symbol=symbol,
        data=ticker_data,
        use_matplotlib=True,
        external_axes=[candles, volume],
        chart=True,
    )
    candles.set_xticklabels("")
    fig.tight_layout()

    f = io.BytesIO()
    fig.savefig(f, format="svg")
    price_chart = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.dd.pt(
        symbol=symbol,
        start_date="2022-01-01",
        data=ticker_data,
        limit=10,
        raw=False,
        external_axes=[ax],
        chart=True,
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    price_target_chart = f.getvalue().decode("utf-8")

    df = openbb.stocks.dd.pt(symbol=symbol)
    avg_ratings_last_30_days = 0
    days = 0
    if not df.empty:
        df_ratings = df[datetime.datetime.now() - datetime.timedelta(days=days) :]
        while df_ratings.empty:
            days += 30
            df_ratings = df[datetime.datetime.now() - datetime.timedelta(days=days) :]

            if days > 100:
                break

        if not df_ratings.empty:
            avg_ratings_last_30_days = round(
                np.mean(df_ratings["Price Target"].values), 2
            )
        else:
            avg_ratings_last_30_days = 0

    last_price = round(ticker_data["Close"][-1], 2)

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.dd.rot(
        symbol=symbol, limit=10, raw=False, export="", external_axes=[ax], chart=True
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    ratings_over_time_chart = f.getvalue().decode("utf-8")

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(11, 3), dpi=150)
    openbb.common.ta.rsi(ticker_data["Close"], external_axes=[ax1, ax2], chart=True)
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    ta_rsi = f.getvalue().decode("utf-8")

    df = openbb.common.ta.rsi(ticker_data["Close"])
    rsi_value = round(df.values[-1][0], 2)

    model = LinearRegression().fit(
        np.array(range(len(ticker_data["Close"][-30:].index))).reshape(-1, 1),
        ticker_data["Close"][-30:].values,
    )
    regression_slope = round(model.coef_[0], 2)

    df_insider = pd.DataFrame.from_dict(openbb.stocks.ins.lins(symbol=symbol)).head(10)
    df_insider["Val ($)"] = df_insider["Value ($)"].replace({",": ""}, regex=True)
    df_insider["Trade"] = df_insider.apply(
        lambda row: (-1 * float(row["Val ($)"]))
        if row["Transaction"] == "Sale"
        else (float(row["Val ($)"]) if row["Transaction"] == "Buy" else 0),
        axis=1,
    )
    last_10_insider_trading = round(sum(df_insider["Trade"]) / 1_000_000, 2)
    df_insider = df_insider.drop(columns=["Val ($)", "Trade"])

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.stocks.ba.headlines(symbol=symbol, external_axes=[ax], chart=True)
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    finbrain_sentiment = f.getvalue().decode("utf-8")

    df_sentiment_finbrain = openbb.stocks.ca.sentiment(symbols=[symbol])
    finbrain_sentiment_val = float(df_sentiment_finbrain.values[-1][0])

    (
        watchlist_count,
        n_cases,
        n_bull,
        n_bear,
    ) = openbb.stocks.ba.bullbear(symbol=symbol)
    stocktwits_sentiment = f"Watchlist count: {watchlist_count}</br>"
    if n_cases > 0:
        stocktwits_sentiment += f"\nLast {n_cases} sentiment messages:</br>"
        stocktwits_sentiment += f"Bullish {round(100*n_bull/n_cases, 2)}%</br>"
        stocktwits_sentiment += f"Bearish {round(100*n_bear/n_cases, 2)}%"
    else:
        stocktwits_sentiment += "No messages found"

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(11, 5), dpi=150)
    openbb.stocks.ba.snews(symbol, external_axes=[ax1, ax2], chart=True)
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    snews = f.getvalue().decode("utf-8")

    ticker_data_all = openbb.stocks.load(
        symbol=symbol,
        start_date=datetime.datetime.now() - datetime.timedelta(days=5 * 12 * 21),
    )
    ticker_data_all["Returns"] = ticker_data_all["Adj Close"].pct_change()

    # TODO Fix predictions virtual path on api refactored

    if predictions:
        regression_val = round(
            openbb.stocks.pred.models.regression.get_regression_model(
                ticker_data_all["Close"], 1, 80, 20, 1
            )[0][-1],
            2,
        )

    # TODO Fix predictions virtual path on api refactored

    if predictions:
        fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
        openbb.stocks.pred.regression(
            symbol, ticker_data_all["Close"], 1, 80, 20, 1, external_axes=[ax]
        )
        fig.tight_layout()
        f = io.BytesIO()
        fig.savefig(f, format="svg")
        regression = f.getvalue().decode("utf-8")

    # TODO Fix predictions virtual path on api refactored

    if predictions:
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(11, 3), dpi=150)
        openbb.stocks.pred.mc(ticker_data["Close"], 30, 100, external_axes=[ax1, ax2])
        fig.tight_layout()
        f = io.BytesIO()
        fig.savefig(f, format="svg")
        mc = f.getvalue().decode("utf-8")

    # TODO Fix predictions virtual path on api refactored

    if predictions:
        fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
        openbb.stocks.pred.regression(
            symbol, ticker_data_all["Close"], 1, 80, 20, 1, external_axes=[ax]
        )
        fig.tight_layout()
        f = io.BytesIO()
        fig.savefig(f, format="svg")
        regression = f.getvalue().decode("utf-8")

    income_df = openbb.stocks.fa.yf_financials(symbol, "financials")
    data_df = openbb.stocks.fa.data(symbol)
    mgmt_df = openbb.stocks.fa.mgmt(symbol)
    mgmt_df["Info"] = mgmt_df["Info"].apply(lambda x: f'<a href="{x}">{x}</a>')
    mgmt_df["Insider Activity"] = mgmt_df["Insider Activity"].apply(
        lambda x: f'<a href="{x}">{x}</a>' if x != "-" else x
    )
    hist_dcf = openbb.stocks.fa.dcf(symbol)
    enterprise_df = openbb.stocks.fa.enterprise(symbol)
    score = openbb.stocks.fa.score(symbol)
    if score:
        score = round(float(score), 2)

    fig, (ax1, ax2, ax3) = plt.subplots(
        nrows=3, ncols=1, figsize=(11, 8), sharex=True, dpi=150
    )
    openbb.common.ta.ma(ticker_data["Close"], symbol=symbol, external_axes=[ax1])
    openbb.common.ta.ma(
        ticker_data["Close"], symbol=symbol, ma_type="SMA", external_axes=[ax2]
    )
    openbb.common.ta.ma(
        ticker_data["Close"], symbol=symbol, ma_type="WMA", external_axes=[ax3]
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    ma_chart = f.getvalue().decode("utf-8")

    fig, (ax, ax1) = plt.subplots(
        nrows=2, ncols=1, figsize=(11, 5), sharex=True, dpi=150
    )
    openbb.common.ta.macd(
        ticker_data["Close"], symbol=symbol, external_axes=[ax, ax1], chart=True
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    macd_chart = f.getvalue().decode("utf-8")

    fig, (ax, ax1) = plt.subplots(
        nrows=2, ncols=1, figsize=(11, 5), sharex=True, dpi=150
    )
    openbb.common.ta.cci(
        ticker_data, symbol=symbol, external_axes=[ax, ax1], chart=True
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    cci_chart = f.getvalue().decode("utf-8")

    fig, (ax, ax1) = plt.subplots(nrows=2, ncols=1, figsize=(11, 5), dpi=150)
    ax2 = ax1.twinx()
    openbb.common.ta.stoch(
        ticker_data, symbol=symbol, external_axes=[ax, ax1, ax2], chart=True
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    stoch_chart = f.getvalue().decode("utf-8")

    fig, (ax, ax1) = plt.subplots(2, 1, sharex=True, figsize=(11, 5), dpi=150)
    openbb.common.ta.adx(
        ticker_data, symbol=symbol, external_axes=[ax, ax1], chart=True
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    adx_chart = f.getvalue().decode("utf-8")

    fig, ax = plt.subplots(figsize=(11, 3), dpi=150)
    openbb.common.ta.bbands(ticker_data, symbol=symbol, external_axes=[ax], chart=True)
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    bbands_chart = f.getvalue().decode("utf-8")

    fig, (ax, ax1, ax2) = plt.subplots(3, 1, sharex=True, figsize=(11, 8), dpi=150)
    openbb.common.ta.ad(
        ticker_data, symbol=symbol, external_axes=[ax, ax1, ax2], chart=True
    )
    fig.tight_layout()
    f = io.BytesIO()
    fig.savefig(f, format="svg")
    ad_chart = f.getvalue().decode("utf-8")

    body = ""

    img = "./openbb_terminal/reports/OpenBB_reports_logo.png"
    floppy_disk_img = ("./openbb_terminal/reports/floppy-disc.png",)
    body += widgets.header(
        img,
        floppy_disk_img,
        author,
        report_date,
        report_time,
        report_timezone,
        report_title,
    )

    body += widgets.tablinks(
        [
            "Summary",
            "Overview",
            "Fundamental Analysis",
            "Technical Analysis",
            "Behavioural Analysis",
            "Government Menu",
            "Comparison Menu",
            "Options",
            "Dark Pool and Shorts",
            "Analyst Opinions",
            "Insider Trading",
            #    "Prediction Techniques",
        ]
    )

    htmlcode = widgets.h(3, "KPIs")
    htmlcode += widgets.kpi(
        [last_price],
        [
            "Last closing price is above the average price ratings of last 30 days",
            "Average price ratings of last 30 day is above last closing price",
        ],
        avg_ratings_last_30_days,
    )
    if predictions:
        htmlcode += widgets.kpi(
            [0],
            [
                "Regression (dollars per market day) on last 30 market days is negative",
                "Regression (dollars per market day) on last 30 market days is positive",
            ],
            regression_slope,
        )
    htmlcode += widgets.kpi(
        [30, 70],
        ["RSI level is oversold", "RSI level is normal", "RSI level is overbought"],
        rsi_value,
    )
    htmlcode += widgets.kpi(
        [0],
        [
            "The sum of last 10 insider trading (in millions) was negative",
            "The sum of last 10 insider trading (in millions) was positive",
        ],
        last_10_insider_trading,
    )
    htmlcode += widgets.kpi(
        [-0.1, 0.1],
        [
            "Last FinBrain sentiment is bearish",
            " Last FinBrain sentiment is neutral",
            "Last FinBrain sentiment is bullish",
        ],
        finbrain_sentiment_val,
    )
    if score:
        htmlcode += widgets.kpi(
            [25, 75],
            [
                "Buffet Score is not favourable",
                "Buffet Score is neutral",
                "Buffet Score is favourable",
            ],
            score,
        )
    if predictions:
        htmlcode += widgets.kpi(
            [0],
            [
                "The regression for the next 20th market price is below closing price",
                "The regression for the next 20th market price is above closing price",
            ],
            round(regression_val - last_price, 2),
        )
    body += widgets.add_tab("Summary", htmlcode)

    htmlcode = widgets.row([widgets.h(3, "Description") + widgets.p(overview)])
    htmlcode += widgets.row([widgets.h(3, "Price Chart") + price_chart])
    htmlcode += widgets.row([widgets.h(3, "Quote") + quote_data.to_html()])
    htmlcode += widgets.row([widgets.h(3, "Latest News for " + symbol)])
    for table in tables:
        htmlcode += widgets.row(
            [widgets.h(4, table[1]["title"]) + table[0].to_html(escape=False)]
        )
    htmlcode += widgets.row(
        [widgets.h(3, f"Management team of {symbol}") + mgmt_df.to_html(escape=False)]
    )
    body += widgets.add_tab("Overview", htmlcode)

    htmlcode = widgets.row([widgets.h(3, "Price Target Chart") + price_target_chart])
    htmlcode += widgets.row(
        [widgets.h(3, "Analyst Ratings over time") + ratings_over_time_chart]
    )
    htmlcode += widgets.row([widgets.h(3, "Analyst Ratings") + df_analyst.to_html()])
    htmlcode += widgets.row(
        [widgets.h(3, "Analyst Recommendations") + df_rating.to_html()]
    )

    body += widgets.add_tab("Analyst Opinions", htmlcode)

    htmlcode = widgets.row(
        [widgets.h(3, "Estimates") + df_year_estimates.head().to_html()]
    )
    htmlcode += widgets.row(
        [widgets.h(3, "Earnings") + df_quarter_earnings.head().to_html()]
    )
    htmlcode += widgets.row(
        [widgets.h(3, "Revenues") + df_quarter_revenues.head().to_html()]
    )
    htmlcode += widgets.row(
        [
            widgets.h(3, "Major Institutional Shareholders")
            + df_institutional_shareholders.head().to_html()
        ]
    )
    htmlcode += widgets.row(
        [widgets.h(3, f"Historical DCF for {symbol}") + hist_dcf.to_html()]
    )
    htmlcode += widgets.row(
        [widgets.h(3, f"Enterprise data for {symbol}") + enterprise_df.to_html()]
    )
    htmlcode += widgets.row(
        [widgets.h(3, f"Income Statement for {symbol}") + income_df.to_html()]
    )
    htmlcode += widgets.row([widgets.h(3, f"Data for {symbol}") + data_df.to_html()])
    htmlcode += widgets.row(
        [widgets.h(3, "SEC filings") + df_sec_filings.to_html(escape=False)]
    )
    body += widgets.add_tab("Fundamental Analysis", htmlcode)

    htmlcode = widgets.row([widgets.h(3, "Put to call ratio") + pcr_chart])
    htmlcode += widgets.row(
        [widgets.h(3, "Option Volume for closest expiry date") + vol_chart]
    )
    htmlcode += widgets.row(
        [widgets.h(3, "Volume and Open Interest for closest expiry date") + voi_chart]
    )
    htmlcode += widgets.row([widgets.h(3, "Option Chains") + options_df.to_html()])
    body += widgets.add_tab("Options", htmlcode)

    htmlcode = widgets.row([net_short_position])
    htmlcode += widgets.row([price_vs_short_interest])
    # htmlcode += widgets.row([dark_pools])
    body += widgets.add_tab("Dark Pool and Shorts", htmlcode)

    htmlcode = widgets.row(
        [
            widgets.h(3, "Congress trading in the past 12 months for " + symbol)
            + gtrades_chart
        ]
    )
    htmlcode += widgets.row([gov_histcont_chart])
    htmlcode += widgets.row([gov_contracts_chart])
    htmlcode += widgets.row([widgets.h(3, "Recent Corporate Lobbying by " + symbol)])
    for _, row in df_lobbying.iterrows():
        amount = (
            "$" + str(int(float(row["Amount"]))) if row["Amount"] is not None else "N/A"
        )
        htmlcode += widgets.row([widgets.p(f"{row['Date']}: {row['Client']} {amount}")])
        if (row["Amount"] is not None) and (row["Specific_Issue"] is not None):
            htmlcode += widgets.row(
                [
                    widgets.p(
                        "\t"
                        + row["Specific_Issue"].replace("\n", " ").replace("\r", "")
                    )
                ]
            )

    body += widgets.add_tab("Government Menu", htmlcode)

    htmlcode = widgets.row(
        [
            widgets.h(3, f"Price over the past year for companies similar to {symbol}")
            + historical_similar
        ]
    )
    htmlcode += widgets.row(
        [
            widgets.h(3, f"Price correlation with similar companies for {symbol}")
            + hcorr_similar
        ]
    )
    htmlcode += widgets.row(
        [
            widgets.h(3, f"Volume over the past year for companies similar to {symbol}")
            + vol_similar
        ]
    )
    htmlcode += widgets.row(
        [
            widgets.h(3, f"Sentiment correlation with similar companies for {symbol}")
            + scorr_similar
        ]
    )
    htmlcode += widgets.row(
        [
            widgets.h(3, f"Income data for similar companies to {symbol}")
            + income_comparison.to_html()
        ]
    )
    htmlcode += widgets.row(
        [
            widgets.p(
                "Note that similar companies have been found using openbb.stocks.ca.polygon_peers"
            )
        ]
    )
    body += widgets.add_tab("Comparison Menu", htmlcode)

    htmlcode = widgets.row([widgets.h(3, f"Moving Averages for {symbol}") + ma_chart])
    htmlcode += widgets.row([macd_chart])
    htmlcode += widgets.row([ta_rsi])
    htmlcode += widgets.row([stoch_chart])
    htmlcode += widgets.row([cci_chart])
    htmlcode += widgets.row([ad_chart])
    htmlcode += widgets.row([bbands_chart])
    htmlcode += widgets.row([adx_chart])
    body += widgets.add_tab("Technical Analysis", htmlcode)

    htmlcode = widgets.row(
        [widgets.h(3, "Last Activity") + df_insider.head(10).to_html(col_space="75px")]
    )
    body += widgets.add_tab("Insider Trading", htmlcode)

    htmlcode = widgets.row([finbrain_sentiment])
    htmlcode += widgets.row([snews])
    htmlcode += widgets.row(
        [
            widgets.h(3, "Interest in " + symbol + " based on google analytics")
            + google_mentions_chart
        ]
    )
    htmlcode += widgets.row(
        [
            widgets.h(3, f"Regions with highest interest in {symbol}")
            + google_regions_chart
        ]
    )
    # htmlcode += widgets.row(
    #    [widgets.h(3, f"Top queries related to {symbol}") + df_related_queries.to_html()]
    # )
    # htmlcode += widgets.row(
    #    [
    #        widgets.h(3, f"Top rising queries related to {symbol}")
    #        + df_rising_queries.to_html()
    #    ]
    # )
    htmlcode += widgets.row(
        [widgets.h(3, f"Lord Cramer's recommendation for {symbol}") + cramer_chart]
    )
    htmlcode += widgets.row(
        [widgets.h(3, f"Stocktwits sentiment for {symbol}") + stocktwits_sentiment]
    )
    body += widgets.add_tab("Behavioural Analysis", htmlcode)

    if predictions:
        htmlcode = widgets.row([regression])
        htmlcode += widgets.row([mc])
    else:
        htmlcode = widgets.row(["Prediction features not enabled."])
    # body += widgets.add_tab("Prediction Techniques", htmlcode)

    body += widgets.tab_clickable_and_save_evt()

    report = widgets.html_report(title=report_name, stylesheet=stylesheet, body=body)

    # to save the results
    with open(report_name + ".html", "w", encoding="utf-8") as fh:
        fh.write(report)
