import os
import configparser
import pandas as pd
from finvizfinance.screener import (
    technical,
    overview,
    valuation,
    financial,
    ownership,
    performance,
)

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")

d_signals = {
    "top_gainers": "Top Gainers",
    "top_losers": "Top Losers",
    "new_high": "New High",
    "new_low": "New Low",
    "most_volatile": "Most Volatile",
    "most_active": "Most Active",
    "unusual_volume": "Unusual Volume",
    "overbought": "Overbought",
    "oversold": "Oversold",
    "downgrades": "Downgrades",
    "upgrades": "Upgrades",
    "earnings_before": "Earnings Before",
    "earnings_after": "Earnings After",
    "recent_insider_buying": "Recent Insider Buying",
    "recent_insider_selling": "Recent Insider Selling",
    "major_news": "Major News",
    "horizontal_sr": "Horizontal S/R",
    "tl_resistance": "TL Resistance",
    "tl_support": "TL Support",
    "wedge_up": "Wedge Up",
    "wedge_down": "Wedge Down",
    "wedge": "Wedge",
    "triangle_ascending": "Triangle Ascending",
    "triangle_descending": "Triangle Descending",
    "channel_up": "Channel Up",
    "channel_down": "Channel Down",
    "channel": "Channel",
    "double_top": "Double Top",
    "double_bottom": "Double Bottom",
    "multiple_top": "Multiple Top",
    "multiple_bottom": "Multiple Bottom",
    "head_shoulders": "Head & Shoulders",
    "head_shoulders_inverse": "Head & Shoulders Inverse",
}


def get_screener_data(
    preset_loaded: str, data_type: str, signal: str, limit: int, ascend: bool
):
    """Screener Overview

    Parameters
    ----------
    preset_loaded : str
        Loaded preset filter
    data_type : str
        Data type between: overview, valuation, financial, ownership, performance, technical
    signal : str
        Signal to use to filter data
    limit : int
        Limit of stocks filtered with presets to print
    ascend : bool
        Ascended order of stocks filtered to print

    Returns
    ----------
    pd.DataFrame
        Dataframe with loaded filtered stocks
    """
    preset_filter = configparser.RawConfigParser()
    preset_filter.optionxform = str  # type: ignore
    preset_filter.read(presets_path + preset_loaded + ".ini")

    d_general = preset_filter["General"]
    d_filters = {
        **preset_filter["Descriptive"],
        **preset_filter["Fundamental"],
        **preset_filter["Technical"],
    }

    d_filters = {k: v for k, v in d_filters.items() if v}

    if data_type == "overview":
        screen = overview.Overview()
    elif data_type == "valuation":
        screen = valuation.Valuation()
    elif data_type == "financial":
        screen = financial.Financial()
    elif data_type == "ownership":
        screen = ownership.Ownership()
    elif data_type == "performance":
        screen = performance.Performance()
    elif data_type == "technical":
        screen = technical.Technical()
    else:
        print("Invalid selected screener type")
        return pd.DataFrame()

    if signal:
        screen.set_filter(signal=d_signals[signal])
    else:
        if "Signal" in d_general:
            screen.set_filter(filters_dict=d_filters, signal=d_general["Signal"])
        else:
            screen.set_filter(filters_dict=d_filters)

    if "Order" in d_general:
        if limit > 0:
            df_screen = screen.ScreenerView(
                order=d_general["Order"],
                limit=limit,
                ascend=ascend,
            )
        else:
            df_screen = screen.ScreenerView(order=d_general["Order"], ascend=ascend)

    else:
        if limit > 0:
            df_screen = screen.ScreenerView(limit=limit, ascend=ascend)
        else:
            df_screen = screen.ScreenerView(ascend=ascend)

    return df_screen
