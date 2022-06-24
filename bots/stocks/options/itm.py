import logging

import pandas as pd

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.options import yfinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def itm_command(
    ticker: str = None,
):
    """Options ITM"""

    # Check for argument
    if ticker is None:
        raise Exception("Stock ticker is required")

    dates = yfinance_model.option_expirations(ticker)

    if not dates:
        raise Exception("Stock ticker is invalid")

    current_price = yfinance_model.get_price(ticker)

    df_date, df_cotm, df_citm, df_potm, df_pitm = [], [], [], [], []
    for date in dates:
        df_date.append(date)
        options = yfinance_model.get_option_chain(ticker, date)
        call_oi = options.calls.set_index("strike")["openInterest"].fillna(0)
        put_oi = options.puts.set_index("strike")["openInterest"].fillna(0)
        df_cotm.append(int(call_oi[call_oi.index >= current_price].sum()))
        df_citm.append(int(call_oi[call_oi.index <= current_price].sum()))
        df_pitm.append(int(put_oi[put_oi.index >= current_price].sum()))
        df_potm.append(int(put_oi[put_oi.index <= current_price].sum()))

    # Calculate the total per column
    df_date.append("<b>Total</b>")
    total = [df_citm, df_cotm, df_pitm, df_potm]
    for x in total:
        x.append(sum(x))

    # Create the DataFrame
    df = pd.DataFrame(
        {
            "Expiry": df_date,
            "Calls ITM": df_citm,
            "Calls OTM": df_cotm,
            "Puts ITM": df_pitm,
            "Puts OTM": df_potm,
        }
    )
    formats = {
        "Calls ITM": "{:,}",
        "Calls OTM": "{:,}",
        "Puts ITM": "{:,}",
        "Puts OTM": "{:,}",
    }
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df.set_index("Expiry", inplace=True)
    fig = imps.plot_df(
        df,
        fig_size=(600, (35 * len(df.index))),
        col_width=[3, 2.5],
        tbl_header=imps.PLT_TBL_HEADER,
        tbl_cells=imps.PLT_TBL_CELLS,
        font=imps.PLT_TBL_FONT,
        row_fill_color=imps.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    fig.update_traces(
        cells=dict(
            align=["center", "right"],
            font=dict(
                color=["white"]
                + [imps.PLT_TBL_INCREASING] * 2
                + [imps.PLT_TBL_DECREASING] * 2
            ),
        ),
    )
    imagefile = imps.save_image("opt-itm.png", fig)

    return {
        "title": f"{ticker.upper()} Options: In The Money",
        "imagefile": imagefile,
    }
