"""FMP Historical EPS Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_eps import (
    HistoricalEpsData,
    HistoricalEpsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class FMPHistoricalEpsQueryParams(HistoricalEpsQueryParams):
    """FMP Historical EPS Query.

    Source: https://site.financialmodelingprep.com/developer/docs#earnings-company
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    limit: int | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", "") + " Default is all.",
    )


class FMPHistoricalEpsData(HistoricalEpsData):
    """FMP Historical EPS Data."""

    __alias_dict__ = {
        "eps_actual": "epsActual",
        "eps_estimated": "epsEstimated",
        "revenue_estimated": "revenueEstimated",
        "revenue_actual": "revenueActual",
        "updated": "lastUpdated",
    }

    revenue_estimated: int | float | None = Field(
        default=None,
        description="Estimated consensus revenue for the reporting period.",
    )
    revenue_actual: int | float | None = Field(
        default=None,
        description="The actual reported revenue.",
    )
    updated: dateType | None = Field(
        default=None,
        description="The date when the data was last updated.",
    )


class FMPHistoricalEpsFetcher(
    Fetcher[
        FMPHistoricalEpsQueryParams,
        list[FMPHistoricalEpsData],
    ]
):
    """FMP Historical EPS Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPHistoricalEpsQueryParams:
        """Transform the query params."""
        return FMPHistoricalEpsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPHistoricalEpsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import warnings  # noqa
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        limit = query.limit + 5 if query.limit is not None else 1000
        results: list = []
        symbols = query.symbol.split(",")

        for symbol in symbols:
            url = f"https://financialmodelingprep.com/stable/earnings?symbol={symbol}&limit={limit}&apikey={api_key}"
            result: list = await get_data_many(url, **kwargs)

            if not result:
                warnings.warn(f"No data found for symbol: {symbol}")
                continue

            results.extend(
                [
                    d
                    for d in sorted(result, key=lambda x: x.get("date"), reverse=True)
                    if d.get("epsActual")
                    or d.get("revenueActual")
                    and d.get("date") <= str(dateType.today())
                ][: query.limit if query.limit is not None else None]
            )

        return results

    @staticmethod
    def transform_data(
        query: FMPHistoricalEpsQueryParams, data: list, **kwargs: Any
    ) -> list[FMPHistoricalEpsData]:
        """Return the transformed data."""
        return [FMPHistoricalEpsData.model_validate(d) for d in data]
