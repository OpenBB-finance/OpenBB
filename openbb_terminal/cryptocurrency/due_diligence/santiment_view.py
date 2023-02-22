import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.due_diligence.santiment_model import (
    get_github_activity,
)
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_SANTIMENT_KEY"])
def display_github_activity(
    symbol: str,
    start_date: Optional[str] = None,
    dev_activity: bool = False,
    end_date: Optional[str] = None,
    interval: str = "1d",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Returns a list of github activity for a given coin and time interval.

    [Source: https://santiment.net/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check github activity
    dev_activity: bool
        Whether to filter only for development activity
    start_date : Optional[str]
        Initial date like string (e.g., 2021-10-01)
    end_date : Optional[str]
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (some possible values are: 1h, 1d, 1w)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = get_github_activity(
        symbol=symbol,
        dev_activity=dev_activity,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
    )

    if df.empty:
        return None

    fig = OpenBBFigure(yaxis_title=f"{symbol}'s Activity count")
    fig.set_title(f"{symbol}'s Github activity over time")

    fig.add_scatter(x=df.index, y=df["value"], name=f"{symbol}'s Activity count")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gh",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
