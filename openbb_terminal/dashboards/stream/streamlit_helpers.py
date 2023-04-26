import re
from datetime import datetime
from inspect import signature
from typing import Any, Callable

import pandas as pd
import streamlit as st
from rich.table import Table

from openbb_terminal.dashboards.stream.common_vars import STOCKS_VIEWS

REGEX_RICH = re.compile(r"\[\/{0,1}[a-zA-Z0-9#]+\]|\[\/\]")

STOCKS_CLEAN_DATA = {
    "sector": lambda x: "N/A" if x is None else x,
    "market_cap": lambda x: "N/A" if x is None else big_num(x),
    "beta": lambda x: "N/A" if x is None else f"{round(x,2)}",
    "year_high": lambda x: "N/A" if x is None else f"${round(x,2)}",
    "year_low": lambda x: "N/A" if x is None else f"${round(x,2)}",
    "floatShares": lambda x: "N/A" if x is None else big_num(x),
    "sharesShort": lambda x: "N/A" if x is None else big_num(x),
    "exDividendDate": lambda x: "N/A"
    if x is None
    else datetime.fromtimestamp(x).strftime("%Y/%m/%d"),
}


def update_current_page() -> None:
    """Updates the current page to the set page"""
    st.session_state["set_page"] = st.session_state["current_page"]


def set_current_page(page: str) -> None:
    """Sets the current page to the given page"""
    st.session_state["current_page"] = page


def get_calc(item, df, rolling) -> pd.DataFrame:
    return STOCKS_VIEWS[item](df, rolling)


def big_num(num):
    if num > 1_000_000_000_000:
        return f"{round(num/1_000_000_000_000,2)}T"
    if num > 1_000_000_000:
        return f"{round(num/1_000_000_000,2)}B"
    if num > 1_000_000:
        return f"{round(num/1_000_000,2)}M"
    if num > 1_000:
        return f"{num/round(1_000,2)}K"
    return f"{round(num,2)}"


def clean_str(string):
    new_str = ""
    for letter in string:
        if letter.isupper():
            new_str += " "
        new_str += letter
    return new_str.title()


def format_df(df: pd.DataFrame) -> pd.DataFrame:
    if len(df.columns) != 6:
        df.columns = ["_".join(col).strip() for col in df.columns.values]
    df.reset_index(inplace=True)
    df.columns = [x.lower() for x in df.columns]
    return df


def has_parameter(func: Callable[..., Any], parameter: str) -> bool:
    params = signature(func).parameters
    parameters = params.keys()
    return parameter in parameters


def load_state(name: str, default: Any) -> Any:
    if name not in st.session_state:
        st.session_state[name] = default
    elif st.session_state.get("current_page", None) != st.session_state.get(
        "set_page", None
    ):
        update_current_page()
        st.session_state[name] = default

    return st.session_state[name]


def load_widget_options(default: Any) -> Any:
    name = "widget_options"
    if name not in st.session_state:
        st.session_state[name] = default
    elif st.session_state.get("current_page", None) != st.session_state.get(
        "set_page", None
    ):
        update_current_page()
        st.session_state[name] = default

    return st.session_state[name]


def get_widget_options(default: dict, key: str) -> Any:
    options = load_widget_options(default)
    if key not in options:
        options[key] = default.get(key, None)

    return options[key]


def save_state(name: str, value: Any):
    st.session_state[name] = value


def rich_to_dataframe(table: Table) -> pd.DataFrame:
    columns = [column.header for column in table.columns]
    rows: dict = {column: [] for column in columns}
    for column in table.columns:
        for cell in column.cells:
            text: str = re.sub(REGEX_RICH, "", cell)  # type: ignore
            rows[column.header].append(text)

    df = pd.DataFrame(rows, columns=columns)
    if "Datetime" in df.columns:
        df.index = pd.to_datetime(df["Datetime"]).dt.date
        df.drop("Datetime", axis=1, inplace=True)

    return df


def set_css():
    """Set the CSS for the app."""
    css_container_style = """
    <style>
        .css-a8w3f8.e1fqkh3o9 {
            margin-top: -65px;
        }
        .css-mcjgwn.e1fqkh3o9 {
            margin-top: -65px;
        }
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 14rem;}}
        .main .block-container {
            padding-top: 3rem;
            padding-bottom: 0rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }
        .table_container {
            position: relative;
            text-align: center;
            align-items: center;
            margin-right: 20px;
            top: 20px;
            font-size: 14px;
            color: white;
        }
        .cov-legend {
            position: relative;
            text-align: center;
            align-items: center;
            top: 20px;
            left: 40px;
            font-size: 16px;
            color: green;
        }
    </style>
    """
    st.markdown(css_container_style, unsafe_allow_html=True)
