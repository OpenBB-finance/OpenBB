"""Base class for Fred API."""

from datetime import date
from typing import Any, Optional
from urllib.parse import urlencode

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider import helpers

ROOT_URL = "https://api.stlouisfed.org/fred"


class Fred:
    """Base class for Fred API."""

    def __init__(self, api_key: Optional[str]):
        """Initialize Fred class.

        Parameters
        ----------
        api_key : str
            API key for FRED
        """
        self.api_key = api_key

    def __fetch_data(self, url: str, **kwargs: Any):
        full_url = f"{url}&api_key={self.api_key}&file_type=json"
        response = helpers.make_request(full_url, **kwargs)
        return response.json()

    def get_series(
        self,
        series_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs,
    ) -> dict:
        """Get data for a Fred series id.

        This fetches the latest known data.
        Code copied from: https://github.com/mortada/fredapi/blob/master/fredapi/fred.py

        Parameters
        ----------
        series_id : str
            Fred series id such as 'CPIAUCSL'
        start_date : date
            earliest observation date
        end_date : date
            latest observation date
        kwargs : additional parameters
            Any additional parameters supported by FRED. You can see the full list here:
            https://api.stlouisfed.org/docs/fred/series_observations.html

        Returns
        -------
        data : Series
            a Series where each index is the observation date and the value is the data
            for the Fred series
        """
        url = f"{ROOT_URL}/series/observations?series_id={series_id}"
        if start_date:
            url += "&observation_start=" + start_date.strftime("%Y-%m-%d")
        if end_date:
            url += "&observation_end=" + end_date.strftime("%Y-%m-%d")
        if kwargs.keys():
            url += "&" + urlencode(
                {k: v for k, v in kwargs.items() if k != "preferences"}
            )
        root = self.__fetch_data(url, **kwargs)
        if root is None:
            raise OpenBBError("No data exists for series id: " + series_id)
        if "error_code" in root and "error_message" in root and root["error_message"]:
            raise OpenBBError(root["error_message"])
        return root["observations"]
