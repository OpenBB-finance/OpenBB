"""TMX Stock Dividends Model"""

import json
from typing import Any, Dict, List, Optional

import requests
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from pydantic import Field

from openbb_tmx.utils.gql import GQL
from openbb_tmx.utils.helpers import get_random_agent


class TmxHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """TMX Historical Dividends Query Params"""


class TmxHistoricalDividendsData(HistoricalDividendsData):
    """TMX Historical Dividends Data"""

    __alias_dict__ = {
        "ex_date": "exDate",
        "dividend": "amount",
        "record_date": "recordDate",
        "payment_date": "payableDate",
        "declaration_date": "declarationDate",
    }
    currency: str = Field(description="The currency the dividend is paid in.")


class TmxHistoricalDividendsFetcher(
    Fetcher[TmxHistoricalDividendsQueryParams, List[TmxHistoricalDividendsData]]
):
    """TMX Historical Dividends Fetcher"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxHistoricalDividendsQueryParams:
        """Transform the query."""
        return TmxHistoricalDividendsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxHistoricalDividendsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        symbol = (
            query.symbol.upper()
            .replace("-", ".")
            .replace(".TO", "")
            .replace(".TSX", "")
        )
        data = []
        payload = GQL.get_dividend_history_payload.copy()
        payload["variables"]["symbol"] = symbol
        payload["variables"]["batch"] = 300
        payload["variables"]["page"] = 1

        url = "https://app-money.tmx.com/graphql"
        r = requests.post(
            url,
            data=json.dumps(payload),
            headers={
                "authority": "app-money.tmx.com",
                "referer": f"https://money.tmx.com/en/quote/{symbol}",
                "locale": "en",
                "Content-Type": "application/json",
                "User-Agent": get_random_agent(),
                "Accept": "*/*",
            },
            timeout=10,
        )
        try:
            if r.status_code == 403:
                raise RuntimeError(f"HTTP error - > {r.text}")
            if "dividends" in r.json()["data"]:
                r_data = r.json()["data"]["dividends"]
                data = sorted(r_data["dividends"], key=lambda d: d["exDate"])

        except Exception as e:
            raise (e)

        return data

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxHistoricalDividendsData]:
        """Return the transformed data."""
        return [TmxHistoricalDividendsData(**d) for d in data]
