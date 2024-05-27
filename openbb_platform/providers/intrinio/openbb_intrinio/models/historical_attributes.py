"""Intrinio Historical Attributes Model."""

# pylint: disable = unused-argument

import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_attributes import (
    HistoricalAttributesData,
    HistoricalAttributesQueryParams,
)
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_requests,
    get_querystring,
)


class IntrinioHistoricalAttributesQueryParams(HistoricalAttributesQueryParams):
    """Intrinio Historical Attributes Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_historical_data_v2
    """

    __alias_dict__ = {"sort": "sort_order", "limit": "page_size", "tag_type": "type"}
    __json_schema_extra__ = {
        "tag": {"multiple_items_allowed": True},
        "symbol": {"multiple_items_allowed": True},
    }


class IntrinioHistoricalAttributesData(HistoricalAttributesData):
    """Intrinio Historical Attributes Data."""


class IntrinioHistoricalAttributesFetcher(
    Fetcher[
        IntrinioHistoricalAttributesQueryParams,
        List[IntrinioHistoricalAttributesData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioHistoricalAttributesQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=5)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioHistoricalAttributesQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioHistoricalAttributesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        query_str = get_querystring(query.model_dump(by_alias=True), ["symbol", "tag"])

        def generate_url(symbol: str, tag: str) -> str:
            """Return the url for the given symbol and tag."""
            url_params = f"{symbol}/{tag}?{query_str}&api_key={api_key}"
            url = f"{base_url}/historical_data/{url_params}"
            return url

        async def callback(
            response: ClientResponse, session: ClientSession
        ) -> List[Dict]:
            """Return the response."""
            init_response = await response.json()

            if message := init_response.get(  # type: ignore
                "error"
            ) or init_response.get(  # type: ignore
                "message"
            ):
                warnings.warn(message=str(message), category=OpenBBWarning)
                return []

            symbol = response.url.parts[-2]  # type: ignore
            tag = response.url.parts[-1]  # type: ignore

            all_data: List = init_response.get("historical_data", [])  # type: ignore
            all_data = [{**item, "symbol": symbol, "tag": tag} for item in all_data]

            next_page = init_response.get("next_page", None)  # type: ignore
            while next_page:
                url = response.url.update_query(  # type: ignore
                    next_page=next_page
                ).human_repr()
                response_data = await session.get_json(url)

                if message := response_data.get("error") or response_data.get(  # type: ignore
                    "message"
                ):
                    warnings.warn(message=message, category=OpenBBWarning)
                    return []

                symbol = response.url.parts[-2]  # type: ignore
                tag = response_data.url.parts[-1]  # type: ignore

                response_data = response_data.get("historical_data", [])  # type: ignore
                response_data = [
                    {**item, "symbol": symbol, "tag": tag} for item in response_data
                ]

                all_data.extend(response_data)
                next_page = response_data.get("next_page", None)  # type: ignore

            return all_data

        urls = [
            generate_url(symbol, tag)
            for symbol in query.symbol.split(",")
            for tag in query.tag.split(",")
        ]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioHistoricalAttributesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioHistoricalAttributesData]:
        """Return the transformed data."""
        return [IntrinioHistoricalAttributesData.model_validate(d) for d in data]
