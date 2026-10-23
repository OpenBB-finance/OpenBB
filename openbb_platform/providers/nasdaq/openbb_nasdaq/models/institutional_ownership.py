"""Nasdaq Institutional Ownership Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.institutional_ownership import (
    InstitutionalOwnershipData,
    InstitutionalOwnershipQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import (
    HOLDER_SORT_COLUMNS,
    HOLDER_SORT_KEYS,
    HOLDER_TYPE_KEYS,
    HOLDER_TYPES,
    SYMBOL_CHOICES_ENDPOINT,
)


class NasdaqInstitutionalOwnershipQueryParams(InstitutionalOwnershipQueryParams):
    """Nasdaq Institutional Ownership Query.

    Source: https://www.nasdaq.com/market-activity/stocks
    """

    __json_schema_extra__ = {
        "symbol": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
        "holder_type": {"choices": list(HOLDER_TYPE_KEYS)},
        "sort_by": {"choices": list(HOLDER_SORT_KEYS)},
    }

    limit: int = Field(
        default=50, description="The number of institutional holders to return."
    )
    holder_type: HOLDER_TYPES = Field(
        default="all",
        description="Restrict the holders to those that changed the position"
        + " in the reported quarter.",
    )
    sort_by: HOLDER_SORT_COLUMNS = Field(
        default="market_value", description="The column the holders are ranked by."
    )


class NasdaqInstitutionalOwnershipData(InstitutionalOwnershipData):
    """Nasdaq Institutional Ownership Data."""

    owner_name: str | None = Field(
        default=None, description="The name of the institutional holder."
    )
    shares_held: float | None = Field(
        default=None, description="The number of shares held."
    )
    shares_change: float | None = Field(
        default=None, description="The change in shares held since the prior filing."
    )
    shares_change_percent: float | None = Field(
        default=None,
        description="The change in shares held, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    market_value: float | None = Field(
        default=None, description="The value of the position, in thousands."
    )
    url: str | None = Field(
        default=None, description="The Nasdaq portfolio page for the holder."
    )


class NasdaqInstitutionalOwnershipFetcher(
    Fetcher[
        NasdaqInstitutionalOwnershipQueryParams,
        list[NasdaqInstitutionalOwnershipData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> NasdaqInstitutionalOwnershipQueryParams:
        """Transform the query."""
        return NasdaqInstitutionalOwnershipQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqInstitutionalOwnershipQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data, rows_from_table

        symbol = query.symbol.upper()
        data = await get_nasdaq_data(
            f"company/{symbol}/institutional-holdings?limit={query.limit}"
            f"&type={HOLDER_TYPE_KEYS[query.holder_type]}"
            f"&sortColumn={HOLDER_SORT_KEYS[query.sort_by]}&sortOrder=DESC"
        )
        rows = rows_from_table((data or {}).get("holdingsTransactions"))

        if not rows:
            raise EmptyDataError(
                f"No '{query.holder_type}' institutional holders were found"
                f" for {symbol}."
            )

        return [{**row, "symbol": symbol} for row in rows]

    @staticmethod
    def transform_data(
        query: NasdaqInstitutionalOwnershipQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[NasdaqInstitutionalOwnershipData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_date, to_number, to_percent

        results: list[NasdaqInstitutionalOwnershipData] = []

        for row in data[: query.limit]:
            url = row.get("url")
            results.append(
                NasdaqInstitutionalOwnershipData.model_validate(
                    {
                        "symbol": row["symbol"],
                        "date": to_date(row.get("date")),
                        "owner_name": row.get("ownerName"),
                        "shares_held": to_number(row.get("sharesHeld")),
                        "shares_change": to_number(row.get("sharesChange")),
                        "shares_change_percent": to_percent(row.get("sharesChangePCT")),
                        "market_value": to_number(row.get("marketValue")),
                        "url": f"https://www.nasdaq.com{url}" if url else None,
                    }
                )
            )

        return results
