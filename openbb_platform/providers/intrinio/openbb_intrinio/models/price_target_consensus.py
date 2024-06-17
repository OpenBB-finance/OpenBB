"""Intrinio Price Target Consensus  Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import date as dateType
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import (
    amake_request,
    get_querystring,
)
from openbb_intrinio.utils.helpers import response_callback
from pydantic import Field


class IntrinioPriceTargetConsensusQueryParams(PriceTargetConsensusQueryParams):
    """Intrinio Price Target Consensus  Query.

    https://docs.intrinio.com/documentation/web_api/get_zacks_sales__v2
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    industry_group_number: Optional[int] = Field(
        default=None,
        description="The Zacks industry group number.",
    )


class IntrinioPriceTargetConsensusData(PriceTargetConsensusData):
    """Intrinio Price Target Consensus  Data."""

    __alias_dict__ = {
        "symbol": "ticker",
        "name": "company_name",
        "target_high": "high",
        "target_low": "low",
        "target_consensus": "mean",
        "target_median": "median",
    }
    standard_deviation: Optional[float] = Field(
        default=None,
        description="The standard deviation of target price estimates.",
    )
    total_anaylsts: Optional[int] = Field(
        default=None,
        description="The total number of target price estimates in consensus.",
    )
    raised: Optional[int] = Field(
        default=None,
        description="The number of analysts that have raised their target price estimates.",
    )
    lowered: Optional[int] = Field(
        default=None,
        description="The number of analysts that have lowered their target price estimates.",
    )
    most_recent_date: Optional[dateType] = Field(
        default=None,
        description="The date of the most recent estimate.",
    )
    industry_group_number: Optional[int] = Field(
        default=None,
        description="The Zacks industry group number.",
    )


class IntrinioPriceTargetConsensusFetcher(
    Fetcher[
        IntrinioPriceTargetConsensusQueryParams, List[IntrinioPriceTargetConsensusData]
    ]
):
    """Intrinio Price Target Consensus  Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioPriceTargetConsensusQueryParams:
        """Transform the query params."""
        return IntrinioPriceTargetConsensusQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioPriceTargetConsensusQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        BASE_URL = (
            "https://api-v2.intrinio.com/zacks/target_price_consensuses?page_size=10000"
        )

        symbols = query.symbol.split(",") if query.symbol else None

        query_str = get_querystring(query.model_dump(by_alias=True), ["symbol"])

        results: List[Dict] = []

        async def get_one(symbol):
            """Get the data for one symbol."""
            url = f"{BASE_URL}&identifier={symbol}&{query_str}&api_key={api_key}"
            new_data: List[Dict] = []
            data = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if (
                not data
                or not isinstance(data, dict)
                or not data.get("target_price_consensuses")
            ):
                warn(f"Symbol Error: No data found for {symbol}")
            if isinstance(data, dict) and data.get("target_price_consensuses"):
                new_data = data.get("target_price_consensuses")  # type: ignore
                if new_data:
                    results.extend(new_data)

        if symbols:
            await asyncio.gather(*[get_one(symbol) for symbol in symbols])
            return results

        async def fetch_callback(response, session):
            """Use callback for pagination."""
            data = await response.json()
            messages = data.get("messages")
            if messages:
                raise OpenBBError(str(messages))
            _data = data.get("target_price_consensuses")
            if _data and len(_data) > 0:
                results.extend(_data)  # type: ignore
                while data.get("next_page"):  # type: ignore
                    next_page = data["next_page"]  # type: ignore
                    next_url = f"{url}&next_page={next_page}"
                    data = await amake_request(next_url, session=session, **kwargs)
                    if (
                        "" in data
                        and len(data.get("target_price_consensuses")) > 0  # type: ignore
                    ):
                        results.extend(data.get("target_price_consensuses"))  # type: ignore
            return results

        url = f"{BASE_URL}&{query_str}&api_key={api_key}"
        results = await amake_request(url, response_callback=fetch_callback, **kwargs)  # type: ignore

        if not results:
            raise EmptyDataError("The request was successful but was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: IntrinioPriceTargetConsensusQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioPriceTargetConsensusData]:
        """Transform the raw data into the standard format."""
        symbols = query.symbol.split(",") if query.symbol else []
        results: List[IntrinioPriceTargetConsensusData] = []
        for item in sorted(  # type: ignore
            sorted(  # type: ignore
                data,
                key=lambda item: item.get("most_recent_date"),  # type: ignore
                reverse=True,
            ),
            key=lambda item: (
                symbols.index(item.get("symbol"))  # type: ignore
                if item.get("symbol") in symbols
                else len(symbols)
            ),
        ):
            _ = item.pop("company")
            results.append(IntrinioPriceTargetConsensusData.model_validate(item))

        return results
