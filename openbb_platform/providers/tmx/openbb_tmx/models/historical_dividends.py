"""TMX Stock Dividends Model"""

# pylint: disable=unused-argument
import json
from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from openbb_tmx.utils import gql
from openbb_tmx.utils.helpers import get_data_from_gql, get_random_agent
from pydantic import Field


class TmxHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """TMX Historical Dividends Query Params"""


class TmxHistoricalDividendsData(HistoricalDividendsData):
    """TMX Historical Dividends Data"""

    __alias_dict__ = {
        "ex_dividend_date": "exDate",
        "record_date": "recordDate",
        "payment_date": "payableDate",
        "declaration_date": "declarationDate",
    }
    currency: Optional[str] = Field(
        default=None, description="The currency the dividend is paid in."
    )
    decalaration_date: Optional[dateType] = Field(
        default=None, description="The date of the announcement."
    )
    record_date: Optional[dateType] = Field(
        default=None,
        description="The record date of ownership for rights to the dividend.",
    )
    payment_date: Optional[dateType] = Field(
        default=None, description="The date the dividend is paid."
    )


class TmxHistoricalDividendsFetcher(
    Fetcher[TmxHistoricalDividendsQueryParams, List[TmxHistoricalDividendsData]]
):
    """TMX Historical Dividends Fetcher"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxHistoricalDividendsQueryParams:
        """Transform the query."""
        return TmxHistoricalDividendsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxHistoricalDividendsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""
        user_agent = get_random_agent()
        symbol = (
            query.symbol.upper()
            .replace("-", ".")
            .replace(".TO", "")
            .replace(".TSX", "")
        )
        data = []
        payload = gql.historical_dividends_payload.copy()
        payload["variables"]["symbol"] = symbol
        payload["variables"]["batch"] = 500
        payload["variables"]["page"] = 1

        url = "https://app-money.tmx.com/graphql"
        response = await get_data_from_gql(
            method="POST",
            url=url,
            data=json.dumps(payload),
            headers={
                "authority": "app-money.tmx.com",
                "referer": f"https://money.tmx.com/en/quote/{symbol}",
                "locale": "en",
                "Content-Type": "application/json",
                "User-Agent": user_agent,
                "Accept": "*/*",
            },
            timeout=5,
        )
        try:
            if "data" in response and "dividends" in response["data"]:
                data = response["data"].get("dividends")
                data = sorted(data["dividends"], key=lambda d: d["exDate"])

        except Exception as e:
            raise RuntimeError(e) from e

        return data

    @staticmethod
    def transform_data(
        query: TmxHistoricalDividendsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TmxHistoricalDividendsData]:
        """Return the transformed data."""
        return [TmxHistoricalDividendsData.model_validate(d) for d in data]
