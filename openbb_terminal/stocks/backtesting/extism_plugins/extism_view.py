"""extism view module"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import Optional

import argparse

import numpy as np
import pandas as pd
import yfinance as yf
import json


from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, is_intraday
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.backtesting.extism_plugins import extism_model

import extism
from extism import Plugin, Function, ValType, host_fn, set_log_file


logger = logging.getLogger(__name__)

np.seterr(divide="ignore")

@log_start_end(log=logger)
def display_strategy(plugin, name: str, symbol: str, data: pd.DataFrame, **kwargs):

    fig = OpenBBFigure(xaxis_title="Date").set_title(f"Equity")
    res = extism_model.run_strategy(plugin, name, symbol, data, **kwargs)

    df_res = res._get_series(None).rebase()  # pylint: disable=protected-access

    for col in df_res.columns:
        fig.add_scatter(
            x=df_res.index,
            y=df_res[col],
            mode="lines",
            name=col,
        )

    console.print(res.display(), "\n")

    export_data(
        "",
        os.path.dirname(os.path.abspath(__file__)),
        "equity",
        res.stats,
        None,
        fig,
    )

    return fig.show(external=False)