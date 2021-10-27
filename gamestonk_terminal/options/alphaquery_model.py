"""AlphaQuery Model"""
__docformat__ = "numpy"

from datetime import datetime, timedelta
import requests
import pandas as pd


def get_put_call_ratio(
    ticker: str,
    window: int = 30,
    start_date: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
) -> pd.DataFrame:
    """Gets put call ratio over last time window [Source: AlphaQuery.com]

    Parameters
    ----------
    ticker : str
        Ticker to look for
    window : int, optional
        Window to consider, by default 30
    start_date : str, optional
        Start date to plot, by default last 366 days
    """
    url = f"https://www.alphaquery.com/data/option-statistic-chart?ticker={ticker}\
        &perType={window}-Day&identifier=put-call-ratio-volume"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/70.0.3538.77 Safari/537.36"
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return pd.DataFrame()

    pcr = pd.DataFrame.from_dict(r.json())
    pcr.rename(columns={"x": "Date", "value": "PCR"}, inplace=True)
    pcr.set_index("Date", inplace=True)
    pcr.index = pd.to_datetime(pcr.index).tz_localize(None)

    return pcr[pcr.index > start_date]
