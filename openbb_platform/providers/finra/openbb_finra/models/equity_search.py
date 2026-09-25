"""FINRA Equity Search Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FinraEquitySearchQueryParams(EquitySearchQueryParams):
    """FINRA Equity Search Query."""

    security_type: Literal["all", "stock", "etf", "closed_end_fund", "mutual_fund"] = (
        Field(
            default="all",
            description="The type of security to search for.",
        )
    )


class FinraEquitySearchData(EquitySearchData):
    """FINRA Equity Search Data."""

    security_type: str | None = Field(
        default=None,
        description="The Morningstar security type - Stock, ETF, Closed-End Fund,"
        + " or Open-End Fund.",
    )
    security_description: str | None = Field(
        default=None,
        description="The share class, or the Morningstar category of a fund.",
    )
    country: str | None = Field(
        default=None, description="The ISO 3166 alpha-3 code of the listing country."
    )
    currency: str | None = Field(default=None, description="The trading currency.")
    isin: str | None = Field(
        default=None, description="The International Securities Identification Number."
    )
    security_id: str | None = Field(
        default=None, description="The Morningstar security id."
    )
    performance_id: str | None = Field(
        default=None, description="The Morningstar performance id."
    )
    exchange: str | None = Field(
        default=None, description="The Market Identifier Code of the listing venue."
    )
    listing_market: str | None = Field(
        default=None, description="The Market Data Center name of the listing exchange."
    )
    composite_market: str | None = Field(
        default=None, description="The Market Data Center name of the composite market."
    )
    quote_symbol: str | None = Field(
        default=None,
        description="The real-time quote key - composite market, type, and symbol.",
    )
    url: str | None = Field(
        default=None, description="The security's page on the FINRA Market Data Center."
    )


def search_record(record: dict) -> dict:
    """Return one Market Data Center search record keyed by the model fields.

    Parameters
    ----------
    record : dict
        The raw search record.

    Returns
    -------
    dict
        The record's identifiers and descriptors.
    """
    from openbb_finra.utils.constants import MARKET_DATA_DETAIL_URL, SECURITY_TYPES
    from openbb_finra.utils.helpers import clean, decode, first, market_names

    performance_id = clean(record.get("OS06Y"))
    listing_market_id = clean(record.get("AC018"))

    return {
        "symbol": clean(first(record.get("OS001"), record.get("AC001"))),
        "name": clean(first(record.get("OS01W"), record.get("Name"))),
        "security_type": decode(SECURITY_TYPES, record.get("OS010")),
        "security_description": clean(record.get("AC021")),
        "country": clean(record.get("OS01V")),
        "currency": clean(first(record.get("Currency"), record.get("AC019"))),
        "isin": clean(first(record.get("ISIN"), record.get("OS05J"))),
        "security_id": clean(record.get("SecId")),
        "performance_id": performance_id,
        "exchange": (clean(record.get("LS01Z")) or "").replace("EX$$$$", "") or None,
        "listing_market": decode(market_names(), listing_market_id),
        "composite_market": decode(
            market_names(),
            first(record.get("CompositeExchangeID"), record.get("AC005")),
        ),
        "quote_symbol": clean(record.get("Ticker")),
        "url": (
            f"{MARKET_DATA_DETAIL_URL}?query={listing_market_id}:{performance_id}"
            if listing_market_id and performance_id
            else None
        ),
    }


class FinraEquitySearchFetcher(
    Fetcher[FinraEquitySearchQueryParams, list[FinraEquitySearchData]]
):
    """Transform the query, extract and transform the data from the FINRA Market Data Center."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinraEquitySearchQueryParams:
        """Transform the query."""
        return FinraEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FinraEquitySearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the search records from the FINRA Market Data Center.

        Raises
        ------
        OpenBBError
            If no search text was given.
        EmptyDataError
            If nothing matched the search.
        """
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_finra.utils.client import market_data_session
        from openbb_finra.utils.constants import SECURITY_TYPE_CONDITIONS

        text = query.query.strip()

        if not text:
            raise OpenBBError("Enter a symbol, name, or ISIN to search for.")

        async with market_data_session() as market_data:
            records = await market_data.search(
                text, SECURITY_TYPE_CONDITIONS[query.security_type]
            )

        if not records:
            raise EmptyDataError(f"No security matched {text!r}.")

        return records

    @staticmethod
    def transform_data(
        query: FinraEquitySearchQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FinraEquitySearchData]:
        """Transform the data to the model."""
        target = query.query.strip().upper()
        results: list[FinraEquitySearchData] = []
        seen: set = set()

        for record in data:
            row = search_record(record)
            key = row["quote_symbol"] or row["security_id"] or row["symbol"]

            if key in seen or (
                query.is_symbol and (row["symbol"] or "").upper() != target
            ):
                continue

            seen.add(key)
            results.append(FinraEquitySearchData.model_validate(row))

        return results
