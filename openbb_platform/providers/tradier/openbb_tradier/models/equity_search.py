"""Tradier Equity Search Model"""

# pylint: disable = unused-argument

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_tradier.utils.constants import OPTIONS_EXCHANGES, STOCK_EXCHANGES
from pydantic import Field, field_validator


class TradierEquitySearchQueryParams(EquitySearchQueryParams):
    """
    Tradier Equity Search Query.

    The search query string should be the beginning of the name or symbol.
    """

    is_symbol: bool = Field(
        description="Whether the query is a symbol. Defaults to False.",
        default=False,
    )


class TradierEquitySearchData(EquitySearchData):
    """Tradier Equity Search Data."""

    __alias_dict__ = {
        "name": "description",
        "security_type": "type",
    }

    exchange: str = Field(description="Exchange where the security is listed.")
    security_type: Literal["stock", "option", "etf", "index", "mutual_fund"] = Field(
        description="Type of security."
    )

    @field_validator("name", "exchange", mode="before", check_fields=False)
    @classmethod
    def name_validator(cls, v: str) -> str:
        """Validate the name."""
        if v is None:
            return "N/A"
        return v


class TradierEquitySearchFetcher(
    Fetcher[TradierEquitySearchQueryParams, List[TradierEquitySearchData]]
):
    """Tradier Equity Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TradierEquitySearchQueryParams:
        """Transform the query."""
        return TradierEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TradierEquitySearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tradier endpoint."""

        api_key = credentials.get("tradier_api_key") if credentials else ""
        sandbox = True

        if api_key and credentials.get("tradier_account_type") not in ["sandbox", "live"]:  # type: ignore
            raise ValueError(
                "Invalid account type for Tradier. Must be either 'sandbox' or 'live'."
            )

        if api_key:
            sandbox = (
                credentials.get("tradier_account_type") == "sandbox"
                if credentials
                else False
            )

        BASE_URL = (
            "https://api.tradier.com/"
            if sandbox is False
            else "https://sandbox.tradier.com/"
        )
        HEADERS = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        is_symbol = "lookup" if query.is_symbol else "search"
        url = f"{BASE_URL}v1/markets/{is_symbol}?q={query.query}"
        if is_symbol == "lookup":
            url += "&types=stock, option, etf, index"
        if is_symbol == "search":
            url += "&indexes=true"

        response = await amake_request(url, headers=HEADERS)

        if response.get("securities"):  # type: ignore
            data = response["securities"].get("security")  # type: ignore
            if len(data) > 0:
                return data if isinstance(data, list) else [data]

        raise EmptyDataError("No results found.")

    @staticmethod
    def transform_data(
        query: TradierEquitySearchQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TradierEquitySearchData]:
        """Transform and validate the data."""

        results: List[TradierEquitySearchData] = []

        for d in data:
            d["exchange"] = (
                OPTIONS_EXCHANGES.get(d["exchange"])
                if d.get("type") in ["option", "index"]
                else STOCK_EXCHANGES.get(d["exchange"])
            )
            results.append(TradierEquitySearchData.model_validate(d))

        return results
