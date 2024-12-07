"""FMP Government Trades Model."""

# pylint: disable=unused-argument,too-many-locals

from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.government_trades import (
    GovernmentTradesData,
    GovernmentTradesQueryParams,
)
from pydantic import Field, model_validator


class FMPGovernmentTradesQueryParams(GovernmentTradesQueryParams):
    """Government Trades Query Parameters.

    Source: https://site.financialmodelingprep.com/developer/docs#senate-trading
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class FMPGovernmentTradesData(GovernmentTradesData):
    """Government Trades Data Model."""

    __alias_dict__ = {
        "symbol": "ticker",
        "transaction_date": "transactionDate",
        "representative": "office",
        "url": "link",
        "transaction_type": "type",
    }
    chamber: Literal["house", "senate"] = Field(
        description="Government Chamber - House or Senate."
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
    transaction_type: Optional[str] = Field(
        default=None, description="Type of transaction (e.g., Sale, Purchase)."
    )
    amount: Optional[str] = Field(default=None, description="Transaction amount range.")
    comment: Optional[str] = Field(
        default=None, description="Additional comments on the transaction."
    )
    url: Optional[str] = Field(
        default=None, description="Link to the transaction document."
    )

    @model_validator(mode="before")
    @classmethod
    def _fill_missing(cls, values):
        """Fill missing information that can be identified."""
        description = values.get("assetDescription", "").lower()
        if not values.get("owner"):
            values["owner"] = "Self"
        if (values.get("ticker") or values.get("symbol")) and not values.get(
            "assetType"
        ):
            values["asset_type"] = "ETF" if "etf" in description else "Stock"
        elif (
            not values.get("ticker")
            and not values.get("symbol")
            and not values.get("assetType")
        ):
            values["asset_type"] = (
                "Treasury"
                if "treasury" in description or "bill" in description
                else (
                    "Bond"
                    if "%" in description
                    or "due" in description
                    or "pct" in description
                    else (
                        "Fund"
                        if "fund" in description
                        else ("ETF" if "etf" in description else None)
                    )
                )
            )
        return values


class FMPGovernmentTradesFetcher(
    Fetcher[
        FMPGovernmentTradesQueryParams,
        list[FMPGovernmentTradesData],
    ]
):
    """FMP Government Trades Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPGovernmentTradesQueryParams:
        """Transform the query params."""
        return FMPGovernmentTradesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPGovernmentTradesQueryParams,
        credentials: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Government Trades endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import math
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_fmp.utils.helpers import create_url, response_callback
        from warnings import warn

        symbols: list = []

        if query.symbol:
            symbols = query.symbol.split(",")

        results: list[dict] = []
        chamber_url_dict = {
            "house": ["senate-disclosure"],
            "senate": ["senate-trading"],
            "all": ["senate-disclosure", "senate-trading"],
        }
        api_key = credentials.get("fmp_api_key") if credentials else ""
        keys_to_remove = {
            "district",
            "capitalGainsOver200USD",
            "disclosureYear",
            "firstName",
            "lastName",
        }
        keys_to_rename = {"dateRecieved": "date", "disclosureDate": "date"}

        async def get_one(url):
            """Get data for one URL."""
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            processed_list: list = []

            for entry in result:
                new_entry = {
                    keys_to_rename.get(k, k): v
                    for k, v in entry.items()
                    if k not in keys_to_remove
                }
                new_entry["chamber"] = "senate" if "senate-trading" in url else "house"
                processed_list.append(new_entry)

            if not processed_list or len(processed_list) == 0:
                warn(f"No data found for {url.replace(api_key, 'API_KEY')}")

            if processed_list:
                results.extend(processed_list)

        urls_list: list = []

        try:
            if symbols:
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
                pages = math.ceil(query.limit / 100)

                if pages > 30:
                    warn(
                        f"Limit value - {query.limit} exceeds the available data for {query.chamber},"
                        " returning all available data."
                    )
                    pages = 31
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
        except OpenBBError as e:
            raise e from e

    @staticmethod
    def transform_data(
        query: FMPGovernmentTradesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPGovernmentTradesData]:
        """Return the transformed data."""
        return sorted(
            [
                FMPGovernmentTradesData(
                    **{k: v for k, v in d.items() if v and v != "--"}
                )
                for d in data
            ],
            key=lambda x: x.date,
            reverse=True,
        )[: query.limit or len(data)]
