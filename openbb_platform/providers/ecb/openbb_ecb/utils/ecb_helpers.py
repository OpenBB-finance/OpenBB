""" ECB helpers"""

import time
from urllib.error import HTTPError

import requests


def get_series_data(series_id: str, start_date: str = "", end_date: str = ""):
    """Get ECB data

    Parameters
    ----------
    series_id: str
        ECB ID of data
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    start_date = start_date.replace("-", "")
    end_date = end_date.replace("-", "")
    url = f"https://data.ecb.europa.eu/data-detail-api/{series_id}"

    def _get_data(max_retries: int = 5):
        try:
            data = requests.get(
                url=url,
                params={"startPeriod": start_date, "endPeriod": end_date},
                timeout=10,
            ).json()

            return data

        except KeyboardInterrupt as interrupt:
            raise interrupt
        except (HTTPError, Exception):
            max_retries -= 1
            if max_retries == 0:
                return None
            time.sleep(0.5)
            return _get_data(max_retries=max_retries)

    data = _get_data()

    # filter by start and end date

    if start_date:
        data = [item for item in data if item["PERIOD"][0] >= start_date]
    if end_date:
        data = [item for item in data if item["PERIOD"][0] <= end_date]

    return _get_data()
