""" OECD view """
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
import os
from typing import Optional

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.fixedincome import oecd_model
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments, too-many-function-args


@log_start_end(log=logger)
def plot_treasuries(
    short_term: Optional[list] = None,
    long_term: Optional[list] = None,
    forecast: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
    limit: int = 10,
):
    """Gets interest rates data from selected countries (3 month and 10 year)

    Short-term interest rates are the rates at which short-term borrowings are effected between financial
    institutions or the rate at which short-term government paper is issued or traded in the market. Short-term
    interest rates are generally averages of daily rates, measured as a percentage. Short-term interest rates are
    based on three-month money market rates where available. Typical standardised names are "money market rate" and
    "treasury bill rate".

    Long-term interest rates refer to government bonds maturing in ten years. Rates are mainly determined by the
    price charged by the lender, the risk from the borrower and the fall in the capital value. Long-term interest
    rates are generally averages of daily rates, measured as a percentage. These interest rates are implied by the
    prices at which the government bonds are traded on financial markets, not the interest rates at which the loans
    were issued. In all cases, they refer to bonds whose capital repayment is guaranteed by governments. Long-term
    interest rates are one of the determinants of business investment. Low long-term interest rates encourage
    investment in new equipment and high interest rates discourage it. Investment is, in turn, a major source of
    economic growth.

    Parameters
    ----------
    short_term: list
        Countries you wish to plot the 3-month interest rate for
    long_term: list
        Countries you wish to plot the 10-year interest rate for
    forecast: bool
        If True, plot forecasts for short term interest rates
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    raw: bool
        If True, print raw data
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = oecd_model.get_treasury(short_term, long_term, forecast, start_date, end_date)

    fig = OpenBBFigure(yaxis_title="Yield (%)")

    for country in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[country],
            name=country.replace("_", " ").title(),
            mode="lines",
            line_width=2.5,
            showlegend=True,
        )

    term = (
        "Short and Long"
        if short_term and long_term
        else "Long"
        if long_term
        else "Short"
    )
    title = f"{term} Term Interest Rates {' with forecasts' if forecast else ''}"
    fig.set_title(title)

    if raw:
        # was a -iloc so we need to flip the index as we use head
        df = df.sort_index(ascending=False)
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            floatfmt=".3f",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "treasury",
        df / 100,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)
