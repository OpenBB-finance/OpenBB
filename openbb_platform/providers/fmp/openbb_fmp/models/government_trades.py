"""Government Trades Model."""

import asyncio
import math
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.government_trades import (
    GovernmentTradesData,
    GovernmentTradesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback
from pydantic import Field


class FMPGovernmentTradesQueryParams(GovernmentTradesQueryParams):
    """Government Trades Query Parameters.

    Source: https://financialmodelingprep.com/api/v4/senate-trading?symbol=AAPL
    Source: https://financialmodelingprep.com/api/v4/senate-trading-rss-feed?page=0
    Source: https://financialmodelingprep.com/api/v4/senate-disclosure?symbol=AAPL
    Source: https://financialmodelingprep.com/api/v4/senate-disclosure-rss-feed?page=0
    """


class FMPGovernmentTradesData(GovernmentTradesData):
    """Government Trades Data Model."""

    __alias_dict__ = {
        "symbol": "ticker",
        "transaction_date": "transactionDate",
        "representative": "office",
    }
    link: Optional[str] = Field(
        default=None, description="Link to the transaction document."
    )
    transaction_date: Optional[str] = Field(
        default=None, description="Date of the transaction."
    )
    owner: Optional[str] = Field(
        default=None, description="Ownership status (e.g., Spouse, Joint)."
    )
    asset_type: Optional[str] = Field(
        default=None, description="Type of asset involved in the transaction."
    )
    asset_description: Optional[str] = Field(
        default=None, description="Description of the asset."
    )
    type: Optional[str] = Field(
        default=None, description="Type of transaction (e.g., Sale, Purchase)."
    )
    amount: Optional[str] = Field(default=None, description="Transaction amount range.")
    comment: Optional[str] = Field(
        default=None, description="Additional comments on the transaction."
    )


class FMPGovernmentTradesFetcher(
    Fetcher[
        FMPGovernmentTradesQueryParams,
        List[FMPGovernmentTradesData],
    ]
):
    """Fetches and transforms data from the Government Trades endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPGovernmentTradesQueryParams:
        """Transform the query params."""
        return FMPGovernmentTradesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPGovernmentTradesQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Government Trades endpoint."""
        symbols = []
        if query.symbol:
            symbols = query.symbol.split(",")
        results: List[Dict] = []
        chamber_url_dict = {
            "house": ["senate-disclosure"],
            "senate": ["senate-trading"],
            "all": ["senate-disclosure", "senate-trading"],
        }
        api_key = credentials.get("fmp_api_key") if credentials else ""

        async def get_one(url):
            # 指定要移除的键
            keys_to_remove = [
                "comment",
                "district",
                "capitalGainsOver200USD",
                "disclosureYear",
            ]
            # 指定要重命名的键，格式为 {原键: 新键}
            keys_to_rename = {"dateRecieved": "date", "disclosureDate": "date"}
            """Get data for the given symbol."""

            result = await amake_request(url, response_callback=response_callback, **kwargs)
            # 处理数据
            processed_list = []
            for entry in result:
                # 创建新的字典用于存储处理后的数据
                new_entry = {k: v for k, v in entry.items() if k not in keys_to_remove}
                # 重命名指定的键
                for old_key, new_key in keys_to_rename.items():
                    if old_key in new_entry:
                        new_entry[new_key] = new_entry.pop(old_key)
                processed_list.append(new_entry)
            if not processed_list or len(processed_list) == 0:
                warn(f"Symbol Error: No data found for {url}")
            if processed_list:
                results.extend(processed_list)

        if symbols:
            urls_list = []
            for symbol in symbols:
                query.symbol = symbol
                url = [
                    create_url(
                        4,
                        f"{i}",
                        api_key=api_key,
                        query=query,
                        exclude=["chamber", "limit"],
                    )
                    for i in chamber_url_dict[query.chamber]
                ]
                urls_list.extend(url)
            await asyncio.gather(*[get_one(url) for url in urls_list])
        else:
            urls_list = []
            pages = math.ceil(query.limit / 100)
            for page in range(pages):
                query.page = page
                url = [
                    create_url(
                        4,
                        f"{i}-rss-feed",
                        api_key=api_key,
                        query=query,
                        exclude=["chamber", "limit"],
                    )
                    for i in chamber_url_dict[query.chamber]
                ]
                urls_list.extend(url)
            await asyncio.gather(*[get_one(url) for url in urls_list])
        if not results:
            raise EmptyDataError("No data returned for the given symbol.")

        return results

    @staticmethod
    def transform_data(
        query: FMPGovernmentTradesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPGovernmentTradesData]:
        """Return the transformed data."""
        return [FMPGovernmentTradesData(**d) for d in data]
