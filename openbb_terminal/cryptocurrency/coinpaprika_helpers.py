"""CoinPaprika helpers"""
__docformat__ = "numpy"

from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter


class PaprikaSession:
    PAPRIKA_BASE_URL = "https://api.coinpaprika.com/v1"

    ENDPOINTS = {
        "global": "/global",
        "coin": "/coins/{}",
        "coins": "/coins",
        "coin_tweeter": "/coins/{}/twitter",
        "coin_events": "/coins/{}/events",
        "coin_exchanges": "/coins/{}/exchanges",
        "coin_markets": "/coins/{}/markets",
        "ohlcv": "/coins/{}/ohlcv/latest",
        "ohlcv_hist": "/coins/{}/ohlcv/historical",
        "people": "/people/{}",
        "tickers": "/tickers",
        "ticker_info": "/tickers/{}",
        "exchanges": "/exchanges",
        "exchange_info": "/exchanges/{}",
        "exchange_markets": "/exchanges/{}/markets",
        "contract_platforms": "/contracts",
        "contract_platform_addresses": "/contracts/{}",
        "search": "/search",
    }

    def __init__(self, max_retries: int = 5):
        self.session = requests.Session()
        self.session.mount(self.PAPRIKA_BASE_URL, HTTPAdapter(max_retries=max_retries))

    def make_request(
        self, endpoint: str, payload: Optional[Any] = None, **kwargs: Any
    ) -> dict:
        """Helper method that handles request for coinpaprika api.
        It prepares URL for given endpoint and payload if it's part of requests

        Parameters
        ----------
        endpoint: str,
            it's an endpoint that we want to query. e.g. to get twitter data for given coin we need to use:
           https://api.coinpaprika.com/v1/coins/{}/twitter
        payload: dict
            the body of your request. Contains the data send to the CoinPaprika API when making an API request
        kwargs:
            additional parameters that will be added to payload
        Returns
        ----------
        dict with response data
        """

        url = f"{self.PAPRIKA_BASE_URL}{endpoint}/"
        if payload is None:
            payload = {}
        if kwargs:
            payload.update(kwargs)
        return self.session.get(url, params=payload).json()
