"""FMP Insider Trading Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.insider_trading import (
    InsiderTradingData,
    InsiderTradingQueryParams,
)
from openbb_fmp.utils.definitions import TRANSACTION_TYPES, TRANSACTION_TYPES_DICT
from pydantic import Field, field_validator


class FMPInsiderTradingQueryParams(InsiderTradingQueryParams):
    """FMP Insider Trading Query.

    Source: https://site.financialmodelingprep.com/developer/docs#search-insider-trades
    """

    __alias_dict__ = {
        "transaction_type": "transactionType",
    }
    __json_schema_extra__ = {
        "transaction_type": {
            "x-widget_config": {
                "options": [
                    {"label": v, "value": k} for k, v in TRANSACTION_TYPES_DICT.items()
                ],
            }
        }
    }

    transaction_type: TRANSACTION_TYPES | None = Field(
        default=None,
        description="Type of the transaction.",
    )

    statistics: bool = Field(
        default=False,
        description="Flag to return summary statistics for the given symbol."
        + " Setting as True will ignore other parameters except symbol.",
    )

    @field_validator("transaction_type", mode="before", check_fields=False)
    @classmethod
    def validate_transaction_type(cls, v):
        """Validate the transaction type."""
        if isinstance(v, list):
            return ",".join(v)
        return v


class FMPInsiderTradingData(InsiderTradingData):
    """FMP Insider Trading Data."""

    __alias_dict__ = {
        "owner_cik": "reportingCik",
        "owner_name": "reportingName",
        "owner_title": "typeOfOwner",
        "ownership_type": "directOrIndirect",
        "security_type": "securityName",
        "transaction_price": "price",
        "acquisition_or_disposition": "acquistionOrDisposition",
        "filing_url": "link",
        "transactions_ratio": "acquiredDisposedRatio",
        "company_cik": "cik",
    }

    form_type: str | None = Field(default=None, description="The SEC form type.")
    year: int | None = Field(
        default=None, description="The calendar year for the statistics."
    )
    quarter: int | None = Field(
        default=None, description="The calendar quarter for the statistics."
    )
    acquired_transactions: int | None = Field(
        default=None, description="Number of acquired transactions (statistics only)."
    )
    disposed_transactions: int | None = Field(
        default=None, description="Number of disposed transactions (statistics only)."
    )
    transactions_ratio: float | None = Field(
        default=None,
        description="Ratio of acquired to disposed transactions (statistics only).",
    )
    total_acquired: int | float | None = Field(
        default=None, description="Total number of shares acquired (statistics only)."
    )
    total_disposed: int | float | None = Field(
        default=None, description="Total number of shares disposed (statistics only)."
    )
    average_acquired: float | None = Field(
        default=None,
        description="Average number of shares acquired per transaction (statistics only).",
    )
    average_disposed: float | None = Field(
        default=None,
        description="Average number of shares disposed per transaction (statistics only).",
    )
    total_purchases: int | None = Field(
        default=None,
        description="Total number of purchase transactions (statistics only).",
    )
    total_sales: int | None = Field(
        default=None, description="Total number of sale transactions (statistics only)."
    )


class FMPInsiderTradingFetcher(
    Fetcher[
        FMPInsiderTradingQueryParams,
        list[FMPInsiderTradingData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPInsiderTradingQueryParams:
        """Transform the query params."""
        return FMPInsiderTradingQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPInsiderTradingQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import math  # noqa
        from openbb_core.provider.utils.helpers import get_querystring
        from openbb_fmp.utils.helpers import get_data_urls, get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""

        if query.statistics is True:
            url = (
                "https://financialmodelingprep.com/stable/insider-trading/statistics"
                + f"?symbol={query.symbol}&apikey={api_key}"
            )
            return await get_data_many(url, **kwargs)

        transaction_type = (
            TRANSACTION_TYPES_DICT.get(query.transaction_type)
            if query.transaction_type
            else None
        )
        limit = query.limit if query.limit and query.limit <= 1000 else 1000
        query = query.model_copy(update={"transaction_type": transaction_type})
        base_url = "https://financialmodelingprep.com/stable/insider-trading/search"
        query_str = get_querystring(query.model_dump(by_alias=True), ["page", "limit"])

        pages = math.ceil(limit / 1000)
        urls = [
            f"{base_url}?{query_str}&page={page}&limit={limit}&apikey={api_key}"
            for page in range(pages)
        ]

        return await get_data_urls(urls, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: FMPInsiderTradingQueryParams, data: list, **kwargs: Any
    ) -> list[FMPInsiderTradingData]:
        """Return the transformed data."""
        return (
            [
                FMPInsiderTradingData.model_validate(d)
                for d in sorted(data, key=lambda x: x["filingDate"], reverse=True)
            ]
            if query.statistics is False
            else [
                FMPInsiderTradingData.model_validate(d)
                for d in sorted(
                    data, key=lambda x: (x["year"], x["quarter"]), reverse=True
                )
            ]
        )
