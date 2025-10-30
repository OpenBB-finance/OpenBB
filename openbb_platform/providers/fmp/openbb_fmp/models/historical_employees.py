"""FMP Historical Employees Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_employees import (
    HistoricalEmployeesData,
    HistoricalEmployeesQueryParams,
)
from pydantic import ConfigDict, Field


class FMPHistoricalEmployeesQueryParams(HistoricalEmployeesQueryParams):
    """FMP Historical Employees Query.

    Source: https://site.financialmodelingprep.com/developer/docs#historical-employee-count
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    limit: int | None = Field(
        default=None,
        description="Number of records to return. Default is all.",
    )


class FMPHistoricalEmployeesData(HistoricalEmployeesData):
    """FMP Historical Employees Data."""

    model_config = ConfigDict(extra="ignore")

    __alias_dict__ = {
        "company_name": "companyName",
        "employees": "employeeCount",
        "date": "periodOfReport",
        "source": "formType",
        "url": "source",
    }

    company_name: str | None = Field(
        default=None,
        description="Company name associated with the data.",
    )
    source: str | None = Field(
        default=None,
        description="Source reference for the data.",
    )
    url: str | None = Field(
        default=None,
        description="URL link to the source of the data.",
    )


class FMPHistoricalEmployeesFetcher(
    Fetcher[
        FMPHistoricalEmployeesQueryParams,
        list[FMPHistoricalEmployeesData],
    ]
):
    """FMP Historical Employees Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPHistoricalEmployeesQueryParams:
        """Transform the query params."""
        return FMPHistoricalEmployeesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPHistoricalEmployeesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import warnings  # noqa
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        results: list = []
        limit = query.limit if query.limit is not None else 10000

        for symbol in symbols:
            url = f"https://financialmodelingprep.com/stable/historical-employee-count?symbol={symbol}&limit={limit}&apikey={api_key}"
            result = await get_data_many(url, **kwargs)

            if not result:
                warnings.warn(f"No data found for symbol {symbol}")
                continue

            results.extend(result)

        return results

    @staticmethod
    def transform_data(
        query: FMPHistoricalEmployeesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPHistoricalEmployeesData]:
        """Return the transformed data."""
        result: list[FMPHistoricalEmployeesData] = []

        for d in data:
            if query.start_date or query.end_date:
                dt = d.get("periodOfReport")

                if not dt:
                    continue

                if query.start_date and dt < query.start_date.isoformat():
                    continue

                if query.end_date and dt > query.end_date.isoformat():
                    continue

            result.append(FMPHistoricalEmployeesData(**d))

        return sorted(result, key=lambda x: x.date, reverse=True)
