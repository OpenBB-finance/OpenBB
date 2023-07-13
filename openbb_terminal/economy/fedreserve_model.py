from datetime import datetime
from io import BytesIO
from typing import List, Literal, Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal.helper_funcs import request

maturities = Literal[
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
maturityType = Union[maturities, List[maturities]]
_all = [
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


def get_treasury_rates(
    maturity: maturityType = ["1y"],
    start_date: str = "2005-01-01",
    end_date: Optional[str] = datetime.now().strftime("%Y-%m-%d"),
) -> pd.DataFrame:
    """Get treasury rates from Federal Reserve

    Parameters
    ----------
    maturity : maturityType, optional
        Maturity to get, by default all
    start_date : str, optional
        Start date of data, by default "2005-01-01"
    end_date : str, optional
        End date , by default today

    Returns
    -------
    pd.DataFrame
        Dataframe with date as index and maturity as columns

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> treasury_rates = openbb.economy.treasury()
    """
    url = (
        "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78"
        "&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn"
    )
    r = request(url)
    df = pd.read_csv(BytesIO(r.content), header=5, index_col=None, parse_dates=True)
    df.columns = ["date"] + _all
    df = df.replace("ND", np.nan).fillna("-").dropna(axis=0)
    df = df[
        (pd.to_datetime(df.date) >= pd.to_datetime(start_date))
        & (pd.to_datetime(df.date) <= pd.to_datetime(end_date))
    ]
    df[_all] = df[_all].applymap(lambda x: float(x) if x != "-" else x)
    df["date"] = pd.to_datetime(df["date"])
    df = df.reset_index(drop=True).set_index("date")
    return df[maturity]
