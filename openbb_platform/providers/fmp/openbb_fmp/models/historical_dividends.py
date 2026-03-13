"""FMP Historical Dividends Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from pydantic import Field, field_validator


class FMPHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """FMP Historical Dividends Query.

    Source: https://site.financialmodelingprep.com/developer/docs#dividends-company
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    limit: int | None = Field(
        default=None, description="Return N most recent payments."
    )


class FMPHistoricalDividendsData(HistoricalDividendsData):
    """FMP Historical Dividends Data."""

    __alias_dict__ = {
        "ex_dividend_date": "date",
        "amount": "dividend",
        "adjusted_amount": "adjDividend",
        "dividend_yield": "yield",
        "record_date": "recordDate",
        "payment_date": "paymentDate",
        "declaration_date": "declarationDate",
    }
    declaration_date: dateType | None = Field(
        default=None,
        description="Declaration date of the historical dividends.",
    )
    record_date: dateType | None = Field(
        default=None,
        description="Record date of the historical dividends.",
    )
    payment_date: dateType | None = Field(
        default=None,
        description="Payment date of the historical dividends.",
    )
    adjusted_amount: float = Field(description="Split-adjusted dividend amount.")
    dividend_yield: float | None = Field(
        default=None,
        description="Dividend yield represented by the payment.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    frequency: str | None = Field(default=None, description="Frequency of the payment.")

    @field_validator(
        "dividend_yield",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def _normalize_percent(cls, v):
        """Validate dates."""
        return v / 100 if v else None


class FMPHistoricalDividendsFetcher(
    Fetcher[
        FMPHistoricalDividendsQueryParams,
        list[FMPHistoricalDividendsData],
    ]
):
    """FMP Historical Dividend Yield Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPHistoricalDividendsQueryParams:
        """Transform the query params."""
        return FMPHistoricalDividendsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPHistoricalDividendsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import warnings  # noqa
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        limit = query.limit or 1000
        symbols = query.symbol.split(",")  # type: ignore
        results: list = []

        for symbol in symbols:
            url = f"https://financialmodelingprep.com/stable/dividends?symbol={symbol}&limit={limit}&apikey={api_key}"
            result = await get_data_many(url, "historical", **kwargs)

            if not result:
                warnings.warn(f"No data found for symbol {symbol}")
                continue

            results.extend(result)

        return sorted(results, key=lambda x: x.get("date"), reverse=True)

    @staticmethod
    def transform_data(
        query: FMPHistoricalDividendsQueryParams, data: list, **kwargs: Any
    ) -> list[FMPHistoricalDividendsData]:
        """Return the transformed data."""
        result: list[FMPHistoricalDividendsData] = []

        for d in data:
            d["declarationDate"] = d.get("declarationDate") or None

            if query.start_date or query.end_date:
                dt = d.get("date")

                if not dt:
                    continue

                if query.start_date and dt < query.start_date.isoformat():
                    continue

                if query.end_date and dt > query.end_date.isoformat():
                    continue

            result.append(FMPHistoricalDividendsData(**d))

        return result
