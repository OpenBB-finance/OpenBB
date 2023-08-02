import logging
import os
from datetime import datetime
from typing import List, Literal, Optional, Union

import numpy as np

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import fedreserve_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


maturities_types = Literal[
    "1m",
    "3m",
    "6m",
    "1y",
    "2y",
    "3y",
    "5y",
    "7y",
    "10y",
    "20y",
    "30y",
]
maturityType = Union[maturities_types, List[maturities_types]]


@log_start_end(log=logger)
def show_treasuries(
    maturities: maturityType = "1y",
    start_date: str = "1900-01-01",
    end_date: Optional[str] = datetime.now().strftime("%Y-%m-%d"),
    raw: bool = False,
    external_axes: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> Union[OpenBBFigure, None]:
    """Display U.S. Treasury rates [Source: EconDB]

    Parameters
    ----------
    maturities : list
        Treasury maturities to display.
    start_date : str
        Starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : Optional[str]
        End date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    raw : bool
        Whether to display the raw output.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file

    Returns
    -------
    Plots the Treasury Series.
    """
    treasury_data = fedreserve_model.get_treasury_rates(
        maturity=maturities, start_date=start_date, end_date=end_date
    )
    if treasury_data.empty:
        console.print("No data found matching the input.\n")
        return None

    # This drops any nan values so that the ful index isn't shown when not all data present
    treasury_data = treasury_data.replace("-", np.nan).dropna(how="all")

    title = (
        "U.S. Treasuries"
        if treasury_data.shape[1] > 1
        else f"{maturities[0].replace('m',' Month').replace('y',' Year')} U.S. Treasury Rate"
    )

    fig = OpenBBFigure(
        yaxis=dict(side="right", title="Yield (%)"),
        title=title,
    )

    for col in treasury_data.columns:
        non_nan = treasury_data[col].notna()
        fig.add_scatter(
            x=treasury_data.index[non_nan],
            y=treasury_data[col][non_nan],
            mode="lines",
            name=col.replace("m", " Month").replace("y", " Year"),
        )

    if raw:
        # was a -iloc so we need to flip the index as we use head
        treasury_data = treasury_data.sort_index(ascending=False)
        print_rich_table(
            treasury_data,
            headers=list(treasury_data.columns),
            show_index=True,
            title="U.S. Treasuries",
            export=bool(export),
        )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "treasuries_data",
            treasury_data,
            sheet_name,
            fig,
        )

    return fig.show(external=raw or external_axes)
