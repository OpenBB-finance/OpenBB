# type: ignore
# pylint: disable=[W0621,R1714]
from typing import Any, Tuple

import pandas as pd
import streamlit as st

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.dashboards.stream import streamlit_helpers as st_helpers
from openbb_terminal.stocks.options.cboe_model import INDEXES, SYMBOLS
from openbb_terminal.stocks.options.options_chains_model import (
    get_nearest_call_strike,
    get_nearest_otm_strike,
    get_nearest_put_strike,
)
from openbb_terminal.stocks.options.options_sdk_helper import (
    OptionsChains,
    load_options_chains,
)

EXCEPTIONS = ["NDX", "RUT"]
analysis_type: str = ""
strike_price: float = 0
moneyness: float = 0
strangle_moneyness: float = 0
price_data = pd.DataFrame()
strategy_data = pd.DataFrame()
title: str = ""
_strikes: Any = None
chart_data_type: str = ""
target_column: dict[str, str] = {
    "Last Price": "lastTradePrice",
    "Bid Price": "bid",
    "Ask Price": "ask",
    "Theoretical Price": "theoretical",
    "Breakeven Price": "Breakeven",
    "Open Interest": "openInterest",
    "Volume": "volume",
    "Implied Volatility": "impliedVolatility",
    "Gamma": "gamma",
    "Theta": "theta",
    "Vega": "vega",
    "Delta Dollars": "DEX",
    "GEX Per 1% Move": "GEX",
}
strategy_target_column_dict = {
    "Cost of Position": "Cost",
    "Cost as % of Underlying": "Cost Percent",
}
surface_choice_dict = {
    "OTM Only": "otm",
    "ITM Only": "itm",
    "Calls Only": "calls",
    "Puts Only": "puts",
}
chains_df = pd.DataFrame()
symbol_choices = SYMBOLS.sort_index().reset_index()
default_symbol = int(symbol_choices.query("`Symbol` == 'SPY'").index[0])
chains_strikes: dict[str, float] = {}

pd.options.plotting.backend = "plotly"
# Suppressing sdk logs
set_system_variable("LOGGING_SUPPRESS", True)

st.set_page_config(
    layout="wide",
    page_title="CBOE Options Dashboard",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://discord.com/invite/Y4HDyB6Ypu",
    },
)

st_helpers.set_current_page("Options")
st_helpers.set_css()


def format_plotly(fig: OpenBBFigure):
    fig.update_layout(
        margin=dict(t=40),
        autosize=False,
        width=1050,
        height=700,
        title=dict(y=0.99, x=0.5, xanchor="center", yanchor="top", automargin=True),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


@st.cache_data(show_spinner=False, experimental_allow_widgets=True)
def load_data(ticker):
    df = load_options_chains(ticker)

    _calls = df.chains[df.chains["optionType"] == "call"].copy()
    _puts = df.chains[df.chains["optionType"] == "put"].copy()

    _calls.loc[:, ("$ To Spot")] = (
        (_calls.loc[:, ("strike")]) + (_calls.loc[:, ("ask")]) - (df.last_price)
    )
    _calls.loc[:, ("% To Spot")] = (_calls.loc[:, ("$ To Spot")] / df.last_price) * 100
    _calls.loc[:, ("Breakeven")] = _calls.loc[:, ("strike")] + _calls.loc[:, ("ask")]
    _calls.loc[:, ("DEX")] = (
        (_calls.loc[:, ("delta")] * 100)
        * (_calls.loc[:, ("openInterest")])
        * df.last_price
    )
    _calls["DEX"] = _calls["DEX"].convert_dtypes(convert_floating=True)
    _calls.loc[:, ("GEX")] = (
        _calls.loc[:, ("gamma")]
        * 100
        * _calls.loc[:, ("openInterest")]
        * (df.last_price * df.last_price)
        * 0.01
    )
    _calls.GEX = _calls.GEX.convert_dtypes(convert_floating=True)
    _calls.set_index(keys=["expiration", "strike", "optionType"], inplace=True)

    _puts.loc[:, ("$ To Spot")] = (
        (_puts.loc[:, ("strike")]) - (_puts.loc[:, ("ask")]) - (df.last_price)
    )
    _puts.loc[:, ("% To Spot")] = (_puts.loc[:, ("$ To Spot")] / df.last_price) * 100
    _puts.loc[:, ("Breakeven")] = _puts.loc[:, ("strike")] - _puts.loc[:, ("ask")]
    _puts.loc[:, ("DEX")] = (
        (_puts.loc[:, ("delta")] * 100)
        * (_puts.loc[:, ("openInterest")])
        * df.last_price
    )
    _puts.loc[:, ("GEX")] = (
        _puts.loc[:, ("gamma")]
        * 100
        * _puts.loc[:, ("openInterest")]
        * (df.last_price * df.last_price)
        * 0.01
        * (-1)
    )
    _puts.GEX = _puts.GEX.convert_dtypes(convert_floating=True)
    _puts["DEX"] = _puts["DEX"].convert_dtypes(convert_floating=True)
    _puts.set_index(keys=["expiration", "strike", "optionType"], inplace=True)

    _calls.GEX = round(_calls.GEX, ndigits=2)
    _calls["DEX"] = round(_calls["DEX"], ndigits=2)
    _puts.GEX = round(_puts.GEX, ndigits=2)
    _puts["DEX"] = round(_puts["DEX"], ndigits=2)

    df.chains = pd.concat([_puts, _calls])
    df.chains.sort_index(inplace=True)
    df.chains.reset_index(inplace=True)

    return df


def get_exposure(df: OptionsChains) -> Tuple[pd.DataFrame, pd.DataFrame]:
    by_strike = pd.DataFrame()
    by_expiration = pd.DataFrame()
    puts_by_strike = (
        df.chains.query("`optionType` == 'put'").groupby("strike")[["DEX", "GEX"]].sum()
    )
    puts_by_strike.columns = ["Put DEX", "Put GEX"]
    calls_by_strike = (
        df.chains.query("`optionType` == 'call'")
        .groupby("strike")[["DEX", "GEX"]]
        .sum()
    )
    calls_by_strike.columns = ["Call DEX", "Call GEX"]
    by_strike = pd.concat([calls_by_strike, puts_by_strike], axis=1)
    puts_by_expiration = (
        df.chains.query("`optionType` == 'put'")
        .groupby("expiration")[["DEX", "GEX"]]
        .sum()
    )
    puts_by_expiration.columns = ["Put DEX", "Put GEX"]
    calls_by_expiration = (
        df.chains.query("`optionType` == 'call'")
        .groupby("expiration")[["DEX", "GEX"]]
        .sum()
    )
    calls_by_expiration.columns = ["Call DEX", "Call GEX"]
    by_expiration = pd.concat([calls_by_expiration, puts_by_expiration], axis=1)
    return by_strike.astype("int64"), by_expiration.astype("int64")


def get_highest_oi(df: OptionsChains) -> pd.DataFrame:
    highest_oi = df.chains[df.chains["openInterest"] == max(df.chains["openInterest"])][
        [
            "optionType",
            "strike",
            "dte",
            "openInterest",
            "volume",
            "impliedVolatility",
            "bid",
            "ask",
            "Breakeven",
        ]
    ]
    highest_oi.columns = [
        "Type",
        "Strike",
        "DTE",
        "OI",
        "Volume",
        "IV",
        "Bid",
        "Ask",
        "Breakeven",
    ]
    return highest_oi


def get_highest_volume(df: OptionsChains) -> pd.DataFrame:
    highest_volume = df.chains[df.chains["volume"] == max(df.chains["volume"])][
        [
            "optionType",
            "strike",
            "dte",
            "openInterest",
            "volume",
            "impliedVolatility",
            "bid",
            "ask",
            "Breakeven",
        ]
    ]
    highest_volume.columns = [
        "Type",
        "Strike",
        "DTE",
        "OI",
        "Volume",
        "IV",
        "Bid",
        "Ask",
        "Breakeven",
    ]
    return highest_volume


with st.sidebar:
    ticker = st.selectbox(
        label="Ticker",
        options=symbol_choices["Symbol"].tolist(),
        index=default_symbol,
        key="ticker",
    )
    df = load_data(ticker)
    chains_df = df.chains
    if ticker == "":
        st.write("Please enter a symbol")
    if hasattr(df, "underlying_name"):
        ticker_good = True
        stats = df.get_stats()
        net_calls = stats.sum()["Calls OI"].astype(int)
        net_puts = stats.sum()["Puts OI"].astype(int)
        pcr_ratio = round((net_puts / net_calls), 4)
        net_calls_vol = stats.sum()["Calls Volume"].astype(int)
        net_puts_vol = stats.sum()["Puts Volume"].astype(int)
        straddle_30d = df.get_straddle()
        st.write(df.underlying_name)
        st.write("Last Price: ", f"${df.last_price:0,.2f}")
        _change = round(df.underlying_price["changePercent"], 2)
        st.write("Change: ", f"{_change:0,.2f}%")
        st.write(
            f"Cost of {straddle_30d.loc['DTE']['Long Straddle']} DTE Straddle: ",
            f"${round(straddle_30d.loc['Cost']['Long Straddle'], 2)}",
        )
        if df.underlying_price["ivThirty"] != 0:
            st.write("IV 30: ", str(df.underlying_price["ivThirty"]))
        if ticker.upper() not in INDEXES and ticker.upper() not in EXCEPTIONS:
            st.write("Stock Volume :", format(df.underlying_price["volume"], ","))
        st.write("Call Volume: ", format(net_calls_vol, ","))
        st.write("Put Volume: ", format(net_puts_vol, ","))
        st.write("Put/Call Ratio: ", str(pcr_ratio))
        analysis_type = st.selectbox(
            "Analysis Type", options=["Charts", "Tables"], key="analysis_type"
        )
        if analysis_type == "Tables":
            table_choices = ["Chains", "Stats"]
            table_choice = st.selectbox("Table Type", options=table_choices)
            if table_choice == "Chains":
                chains_selections = ["% OTM", "Delta", "None"]
                chains_select = st.selectbox(
                    "Limit Range of Results",
                    options=chains_selections,
                    key="chains_select",
                )
                if chains_select == "% OTM":
                    chains_moneyness: float = st.number_input(
                        label="% OTM Range",
                        min_value=0.01,
                        max_value=99.99,
                        value=2.0,
                        step=0.25,
                    )
                    chains_strikes = get_nearest_otm_strike(df, chains_moneyness)
                if chains_select == "Delta":
                    delta_choice: float = st.number_input(
                        label="Delta Value",
                        min_value=0.01,
                        max_value=1.0,
                        value=0.5,
                        step=0.05,
                    )
                chains_choice = st.selectbox(
                    "Chain Type", options=["Calls", "Puts", "Both"], key="chains_choice"
                )
                expiration_choices = ["All"]
                expiration_choices.extend(df.expirations)
                expiration_choice = st.selectbox(
                    "Expiration Date",
                    options=expiration_choices,
                    key="expiration_choice",
                )
        if analysis_type == "Charts":
            stats_type: str = ""
            chart_data_type = st.selectbox(
                "Chart Data Type",
                options=["Stats", "Strikes", "Strategies", "Volatility"],
                key="chart_data_type",
            )
            expiry = "All"
            if chart_data_type == "Stats":
                stats_type = st.selectbox(
                    "Stat Type",
                    options=["Open Interest", "Volume", "Ratios"],
                    key="stats_type",
                )
            if stats_type in ("Open Interest", "Volume"):
                is_percent = st.checkbox(
                    "Percent of Total", value=False, key="is_percent"
                )
                if is_percent is False and stats_type == "Open Interest":
                    expiries = ["All"]
                    expiries.extend(df.expirations)
                    expiry = st.selectbox("Expiry", options=expiries, key="expiry")
            if chart_data_type == "Strikes":
                strike_choice = st.selectbox(
                    "Strike Selection Type",
                    options=(["Single Strike", "Separate Calls and Puts", "% OTM"]),
                    key="strike_choice",
                )
                if strike_choice == "Separate Calls and Puts":
                    _default_call = get_nearest_call_strike(
                        df, strike_price=df.last_price
                    )
                    _default_put = get_nearest_put_strike(
                        df, strike_price=df.last_price
                    )
                    _default_strikes = pd.Series(df.strikes)
                    default_call = int(
                        _default_strikes[_default_strikes == _default_call].index[0]
                    )
                    default_put = int(
                        _default_strikes[_default_strikes == _default_put].index[0]
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        _call = st.selectbox(
                            "Call Strike",
                            options=df.strikes,
                            index=default_call,
                            key="call_strike",
                        )
                    with col2:
                        _put = st.selectbox(
                            "Put Strike",
                            options=df.strikes,
                            index=default_put,
                            key="put_strike",
                        )
                    _strikes = {"call": _call, "put": _put}
                if strike_choice == "% OTM":
                    moneyness: float = st.number_input(
                        label="% OTM Moneyness",
                        min_value=0.01,
                        max_value=99.99,
                        value=2.0,
                        step=0.25,
                        key="moneyness",
                    )
                    _strikes = get_nearest_otm_strike(df, moneyness)
                if strike_choice == "Single Strike":
                    default_strike_price = get_nearest_call_strike(
                        df, strike_price=df.last_price
                    )
                    _strikes = pd.Series(df.strikes)
                    default_strike = int(
                        _strikes[_strikes == default_strike_price].index[0]
                    )
                    strike_price = st.selectbox(
                        "Strike Price",
                        options=df.strikes,
                        index=default_strike,
                        key="strike_price",
                    )
                strike_data_point = st.selectbox(
                    "Data Point",
                    options=list(target_column.keys()),
                    key="strike_data_point",
                )

            if chart_data_type == "Strategies":
                _strikes = pd.Series(df.strikes)
                strategy_choice = st.selectbox(
                    "Strategy Type",
                    options=(
                        [
                            "Straddle",
                            "Strangle",
                            "Synthetic Long",
                            "Synthetic Short",
                            "Vertical Call",
                            "Vertical Put",
                        ]
                    ),
                    key="strategy_choice",
                )
                if strategy_choice == "Strangle":
                    strangle_moneyness: float = st.number_input(
                        label="% OTM Moneyness",
                        min_value=0.01,
                        max_value=99.99,
                        value=2.0,
                        step=0.25,
                        key="strangle_moneyness",
                    )
                if strategy_choice == "Straddle":
                    default_strike_price = get_nearest_call_strike(
                        df, strike_price=df.last_price
                    )
                    default_strike = int(
                        _strikes[_strikes == default_strike_price].index[0]
                    )
                    straddle_strike: float = st.selectbox(
                        "Strike Price",
                        options=df.strikes,
                        index=default_strike,
                        key="straddle_strike",
                    )
                if strategy_choice in ("Synthetic Long", "Synthetic Short"):
                    default_strike_price = get_nearest_call_strike(
                        df, strike_price=df.last_price
                    )
                    default_strike = int(
                        _strikes[_strikes == default_strike_price].index[0]
                    )
                    synthetic_strike = st.selectbox(
                        "Strike Price",
                        options=df.strikes,
                        index=default_strike,
                        key="synthetic_strike",
                    )
                if strategy_choice in ("Vertical Call", "Vertical Put"):
                    default_strike_price1 = get_nearest_call_strike(
                        df,
                        strike_price=df.last_price + 5
                        if strategy_choice == "Vertical Call"
                        else df.last_price - 5,
                    )
                    default_strike_price2 = get_nearest_call_strike(
                        df, strike_price=df.last_price
                    )
                    default_strike1 = int(
                        _strikes[_strikes == default_strike_price1].index[0]
                    )
                    default_strike2 = int(
                        _strikes[_strikes == default_strike_price2].index[0]
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        strike1 = st.selectbox(
                            "Sold Strike Price",
                            options=df.strikes,
                            index=default_strike1,
                            key="strike1",
                        )
                    with col2:
                        strike2 = st.selectbox(
                            "Bought Strike Price",
                            options=df.strikes,
                            index=default_strike2,
                            key="strike2",
                        )

                strategy_target_column = st.selectbox(
                    "Data Type",
                    options=list(strategy_target_column_dict.keys()),
                    key="strategy_target_column",
                )

            if chart_data_type == "Volatility":
                vol_choices = ["Smile", "Skew", "Surface"]
                vol_choice = st.selectbox(
                    "Volatility Type", options=vol_choices, index=0, key="vol_choice"
                )
                if vol_choice in ("Smile", "Skew"):
                    if vol_choice == "Smile":
                        col1, col2 = st.columns(2)
                        with col1:
                            with_volume = st.checkbox(
                                "With Volume", value=False, key="with_volume"
                            )
                        with col2:
                            with_oi = st.checkbox("With OI", value=False, key="with_oi")
                    if vol_choice == "Skew":
                        otm_only = st.checkbox("OTM Only", value=False, key="otm_only")
                    with st.expander("Select Expiration Dates"):
                        expiration_choice = st.multiselect(
                            "Expiration Date",
                            options=df.expirations,
                            default=df.expirations[2],
                            key="expiration_choice",
                        )
                if vol_choice == "Surface":
                    surface_choices = [
                        "Calls Only",
                        "Puts Only",
                        "OTM Only",
                        "ITM Only",
                    ]
                    surface_choice = st.selectbox(
                        "Surface Type",
                        options=surface_choices,
                        index=2,
                        key="surface_choice",
                    )
    else:
        st.write("Please enter a valid symbol.")
        ticker_good = False


if analysis_type == "Tables" and table_choice == "Chains" and ticker_good is True:
    if chains_select == "% OTM":
        upper = chains_strikes["call"]
        lower = chains_strikes["put"]
        chains_df = df.chains.query("@lower <= `strike` <= @upper")
    if chains_select == "Delta":
        upper_call = delta_choice + 0.01
        lower_call = delta_choice - 0.01
        upper_put = (delta_choice + 0.01) * (-1)
        lower_put = (delta_choice - 0.01) * (-1)
        chains_df = df.chains.query(
            "@lower_call <= `delta` <= @upper_call or @lower_put >= `delta` >= @upper_put"
        )
    if chains_select == "None":
        chains_df = df.chains
    if expiration_choice != "All":
        chains_df = chains_df[chains_df["expiration"] == expiration_choice]
    if expiration_choice == "All":
        chains_df = chains_df[chains_df["dte"] >= 0]
    chains_df = chains_df[
        [
            "strike",
            "dte",
            "optionType",
            "theoretical",
            "bidSize",
            "bid",
            "ask",
            "askSize",
            "lastTradePrice",
            "openInterest",
            "volume",
            "impliedVolatility",
            "delta",
            "gamma",
            "theta",
            "rho",
            "vega",
            "open",
            "high",
            "low",
            "previousClose",
            "DEX",
            "GEX",
            "Breakeven",
            "$ To Spot",
            "% To Spot",
        ]
    ]
    chains_df = chains_df.rename(
        columns={
            "strike": "Strike",
            "dte": "DTE",
            "optionType": "Type",
            "theoretical": "Theoretical",
            "bidSize": "Bid Size",
            "bid": "Bid",
            "ask": "Ask",
            "askSize": "Ask Size",
            "lastTradePrice": "Last",
            "openInterest": "OI",
            "volume": "Volume",
            "impliedVolatility": "IV",
            "delta": "Delta",
            "gamma": "Gamma",
            "theta": "Theta",
            "rho": "Rho",
            "vega": "Vega",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "previousClose": "Prev Close",
        }
    )
    chains_df.Theoretical = round(chains_df.Theoretical, 2)
    chains_df = chains_df.set_index("Strike")
    chains_df = chains_df[chains_df["Last"] > 0]
    if chains_choice == "Calls":
        chains_df = chains_df[chains_df["Type"] == "call"]
    if chains_choice == "Puts":
        chains_df = chains_df[chains_df["Type"] == "put"]
    st.dataframe(chains_df, use_container_width=True, height=700)

if analysis_type == "Tables" and table_choice == "Stats" and ticker_good is True:
    exposure_by_strike, exposure_by_expiration = get_exposure(df)
    stats_df_expiration = df.get_stats()
    stats_df_strike = df.get_stats("strike")
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    with sc1:
        st.write("Total OI: ", format(stats_df_expiration["Total OI"].sum(), ","))
    with sc2:
        st.write("Call OI: ", format(stats_df_expiration["Calls OI"].sum(), ","))
    with sc3:
        st.write("Put OI: ", format(stats_df_expiration["Puts OI"].sum(), ","))
    with sc4:
        st.write("Call DEX: $", format(exposure_by_expiration["Call DEX"].sum(), ","))
    with sc5:
        st.write(
            "Put DEX: $", format(abs(exposure_by_expiration["Put DEX"]).sum(), ",")
        )

    with st.expander("Stats by Expiration", expanded=True):
        st.dataframe(stats_df_expiration, use_container_width=True)
    with st.expander("Stats by Strike", expanded=False):
        st.dataframe(stats_df_strike, use_container_width=True)
    with st.expander("Delta Dollars and GEX per 1% Move", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(exposure_by_expiration.abs(), use_container_width=True)
        with col2:
            st.dataframe(exposure_by_strike.abs(), use_container_width=True)

if analysis_type == "Charts" and ticker_good is True and chart_data_type == "Stats":
    if stats_type == "Open Interest" and expiry != "All":
        fig_oi_exp = df.chart_stats(
            "strike", expiry=expiry, external_axes=True, oi=True, percent=False
        )
        fig_oi_exp = format_plotly(fig_oi_exp)
        st.plotly_chart(
            fig_oi_exp,
            use_container_width=True,
        )

    elif stats_type in ("Open Interest", "Volume"):
        tab1, tab2 = st.tabs(["By Expiration", "By Strike"])
        with tab1:
            if stats_type == "Open Interest":
                fig_oi_exp = df.chart_stats(
                    percent=bool(is_percent), oi=True, external_axes=True
                )
                fig_oi_exp = format_plotly(fig_oi_exp)
                st.plotly_chart(fig_oi_exp, use_container_width=True)
            if stats_type == "Volume":
                fig_vol_exp = df.chart_stats(
                    percent=bool(is_percent), oi=False, external_axes=True
                )
                fig_vol_exp = format_plotly(fig_vol_exp)
                st.plotly_chart(fig_vol_exp, use_container_width=True)
        with tab2:
            if stats_type == "Open Interest":
                fig_oi_strike = df.chart_stats(
                    "strike", percent=bool(is_percent), oi=True, external_axes=True
                )
                fig_oi_strike = format_plotly(fig_oi_strike)
                st.plotly_chart(fig_oi_strike, use_container_width=True)
            if stats_type == "Volume":
                fig_vol_exp = df.chart_stats(
                    "strike", percent=bool(is_percent), oi=False, external_axes=True
                )
                fig_vol_exp = format_plotly(fig_vol_exp)
                st.plotly_chart(fig_vol_exp, use_container_width=True)

    elif stats_type == "Ratios":
        ratios_fig = df.chart_stats(ratios=True, external_axes=True)
        ratios_fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1,
                xanchor="left",
                x=0.01,
            )
        )
        ratios_fig = format_plotly(ratios_fig)
        st.plotly_chart(
            ratios_fig,
            use_container_width=True,
            config=dict(
                scrollZoom=True,
                displaylogo=False,
            ),
        )

if analysis_type == "Charts" and chart_data_type == "Strikes" and ticker_good is True:
    title = f"{strike_data_point} of {df.symbol} Options @ ${strike_price} Strike Price"
    title = (
        f"{strike_data_point} of {df.symbol} Options @ {moneyness}% OTM"
        if strike_choice == "% OTM"
        else title
    )
    title = (
        f"{strike_data_point} of {df.symbol} Options"
        if strike_choice == "Separate Calls and Puts"
        else title
    )
    title = (
        f"Gamma Exposure per 1% Move of {df.symbol}"
        if strike_data_point == "GEX Per 1% Move"
        else title
    )
    if strike_choice == "Single Strike":
        _price_data = df.chains[df.chains["strike"] == strike_price]
        call_price_data = _price_data[_price_data["optionType"] == "call"]
        put_price_data = _price_data[_price_data["optionType"] == "put"]
        call_price_data = call_price_data.drop_duplicates("expiration").set_index(
            "expiration"
        )
        put_price_data = put_price_data.drop_duplicates("expiration").set_index(
            "expiration"
        )
        price_data["Call"] = call_price_data[target_column[strike_data_point]]
        price_data["Put"] = put_price_data[target_column[strike_data_point]]
    if strike_choice in ("Separate Calls and Puts", "% OTM"):
        call_price_data = (
            df.chains[df.chains["strike"] == _strikes["call"]]
            .query("`optionType` == 'call'")
            .drop_duplicates("expiration")
            .set_index("expiration")
        )
        put_price_data = (
            df.chains[df.chains["strike"] == _strikes["put"]]
            .query("`optionType` == 'put'")
            .drop_duplicates("expiration")
            .set_index("expiration")
        )
        price_data["Call"] = call_price_data[target_column[strike_data_point]]
        price_data["Put"] = put_price_data[target_column[strike_data_point]]
    fig_price_data = OpenBBFigure()
    fig_price_data.add_scatter(
        x=price_data.index,
        y=price_data["Call"],
        mode="lines+markers",
        name="Calls"
        if strike_choice == "Single Strike"
        else f"Calls @ ${_strikes['call']}",
        marker=dict(color="blue"),
    )
    fig_price_data.add_scatter(
        x=price_data.index,
        y=price_data["Put"],
        mode="lines+markers",
        name="Puts"
        if strike_choice == "Single Strike"
        else f"Puts @ {_strikes['put']}",
        marker=dict(color="red"),
    )
    fig_price_data.update_xaxes(type="category")
    fig_price_data.update_layout(
        title=dict(text=title, x=0.5, y=0.97),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.125,
            xanchor="left",
            x=0.01,
        ),
    )
    fig_price_data = format_plotly(fig_price_data)
    st.plotly_chart(
        fig_price_data,
        use_container_width=True,
        config=dict(
            scrollZoom=True,
            displaylogo=False,
        ),
    )

if (
    analysis_type == "Charts"
    and chart_data_type == "Strategies"
    and ticker_good is True
):
    if strategy_choice == "Strangle":
        title = f"Cost of {df.symbol} Strangle  @ {strangle_moneyness}% OTM"
        strategy_data = df.get_strategies(strangle_moneyness=strangle_moneyness)

    if strategy_choice == "Straddle":
        title = f"Cost of {df.symbol} Straddle  @ ${straddle_strike} Strike"
        strategy_data = df.get_strategies(straddle_strike=straddle_strike)

    if strategy_choice == "Synthetic Long":
        title = f"Cost of {df.symbol} Synthetic Long  @ ${synthetic_strike} Strike"
        strategy_data = df.get_strategies(synthetic_longs=synthetic_strike)

    if strategy_choice == "Synthetic Short":
        title = f"Cost of {df.symbol} Synthetic Short  @ ${synthetic_strike} Strike"
        strategy_data = df.get_strategies(synthetic_shorts=synthetic_strike)

    if strategy_choice == "Vertical Call":
        strategy_data = df.get_strategies(vertical_calls=[strike1, strike2])
        strategy_name = strategy_data.iloc[0]["Strategy"]
        title = f"Cost of {df.symbol} {strategy_name} @ ${strike1} & ${strike2} Strikes"

    if strategy_choice == "Vertical Put":
        strategy_data = df.get_strategies(vertical_puts=[strike1, strike2])
        strategy_name = strategy_data.iloc[0]["Strategy"]
        title = f"Cost of {df.symbol} {strategy_name} @ ${strike1} & ${strike2} Strikes"

    title = (
        title + " As % of Underlying Price"
        if strategy_target_column == "Cost as % of Underlying"
        else title
    )

    fig_strategy = OpenBBFigure()
    fig_strategy.add_scatter(
        x=strategy_data.Expiration,
        y=strategy_data[strategy_target_column_dict[strategy_target_column]],
        mode="lines+markers",
        name="Cost of Long Strangle",
        marker=dict(color="red"),
    )
    fig_strategy.update_xaxes(type="category")
    fig_strategy.update_layout(title=dict(text=title, x=0.5, y=0.97))
    fig_strategy = format_plotly(fig_strategy)
    st.plotly_chart(
        fig_strategy,
        use_container_width=True,
        config=dict(
            scrollZoom=True,
            displaylogo=False,
        ),
    )

if (
    analysis_type == "Charts"
    and chart_data_type == "Volatility"
    and ticker_good is True
):
    if vol_choice == "Smile":
        if len(expiration_choice) == 0:
            expiration_choice = df.expirations[2]
        if len(expiration_choice) > 5:
            expiration_choice = expiration_choice[0:5]
        smile_fig = df.chart_volatility(
            expirations=expiration_choice,
            oi=with_oi,
            volume=with_volume,
            external_axes=True,
        )
        smile_fig = format_plotly(smile_fig)
        smile_fig.update_layout(
            legend=dict(
                orientation="h", yanchor="top", y=1.025, xanchor="center", x=0.5
            )
        )
        st.plotly_chart(
            smile_fig,
            use_container_width=True,
            config=dict(
                scrollZoom=True,
                displaylogo=False,
            ),
        )
    if vol_choice == "Skew":
        if len(expiration_choice) == 0:
            expiration_choice = df.expirations[2]
        if otm_only is False and len(expiration_choice) > 5:
            expiration_choice = expiration_choice[0:5]
        if otm_only is True and len(expiration_choice) > 10:
            expiration_choice = expiration_choice[0:10]
        skew_fig = df.chart_skew(
            expirations=expiration_choice, otm_only=otm_only, external_axes=True
        )
        skew_fig = format_plotly(skew_fig)
        skew_fig.update_layout(
            legend=dict(
                orientation="h", yanchor="top", y=1.025, xanchor="center", x=0.5
            )
        )
        st.plotly_chart(
            skew_fig,
            use_container_width=True,
            config=dict(
                scrollZoom=True,
                displaylogo=False,
            ),
        )
    if vol_choice == "Surface":
        dte_ranges = df.chains.dte.unique().tolist()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            near_dte_limit = int(
                st.select_slider(
                    "Near DTE Boundary",
                    options=dte_ranges,
                    value=dte_ranges[0],
                    key="near_dte_limit",
                )
            )
        with col2:
            far_dte_limit = int(
                st.select_slider(
                    "Far DTE Boundary",
                    options=dte_ranges,
                    value=dte_ranges[-1],
                    key="far_dte_limit",
                )
            )
        near = near_dte_limit if near_dte_limit < far_dte_limit else far_dte_limit
        far = far_dte_limit if near_dte_limit < far_dte_limit else near_dte_limit
        if near == far:
            far += 1
        dte_range = [far, near]
        with col3:
            lower_strike = float(
                st.select_slider(
                    "Lower Strike",
                    options=df.strikes,
                    value=df.strikes[0],
                    key="lower_strike",
                )
            )
        with col4:
            upper_strike = float(
                st.select_slider(
                    "Upper Strike",
                    options=df.strikes,
                    value=df.strikes[-1],
                    key="upper_strike",
                )
            )
        lower = lower_strike if lower_strike < upper_strike else upper_strike
        upper = upper_strike if lower_strike < upper_strike else lower_strike
        strike_range = [lower, upper]
        surface_fig = df.chart_surface(
            surface_choice_dict[surface_choice],
            dte_range,
            strike_range,
            external_axes=True,
        )
        surface_fig = format_plotly(surface_fig)
        st.plotly_chart(surface_fig, use_container_width=True)
