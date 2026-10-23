"""TMX Company Filings Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_filings import (
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from pydantic import Field, field_validator


class TmxCompanyFilingsQueryParams(CompanyFilingsQueryParams):
    """TMX Company Filings Query Parameters."""

    start_date: dateType | None = Field(
        description="The start date to fetch.",
        default=None,
    )
    end_date: dateType | None = Field(
        description="The end date to fetch.",
        default=None,
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v: str):
        """Validate the symbol."""
        if not v:
            raise ValueError("Symbol is required for TMX.")
        return v


class TmxCompanyFilingsData(CompanyFilingsData):
    """TMX Sedar Filings Data."""

    __alias_dict__ = {
        "filing_date": "filingDate",
        "report_type": "name",
        "report_url": "urlToPdf",
    }

    description: str = Field(description="The description of the filing.")
    size: str | None = Field(
        description="The file size of the PDF document.", default=None
    )


class TmxCompanyFilingsFetcher(
    Fetcher[TmxCompanyFilingsQueryParams, list[TmxCompanyFilingsData]]
):
    """TMX Company Filings Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxCompanyFilingsQueryParams:
        """Transform the query."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta

        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                datetime.now() - timedelta(weeks=16)
            ).strftime("%Y-%m-%d")
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = datetime.now().date().strftime("%Y-%m-%d")
        transformed_params["symbol"] = (
            params.get("symbol", "")
            .upper()
            .replace("-", ".")
            .replace(".TO", "")
            .replace(".TSX", "")
        )
        return TmxCompanyFilingsQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: TmxCompanyFilingsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        import asyncio
        from datetime import timedelta

        from dateutil import rrule

        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import normalize_symbol

        symbol = normalize_symbol(str(query.symbol))
        results: list[dict] = []

        dates = list(
            rrule.rrule(
                rrule.WEEKLY, interval=1, dtstart=query.start_date, until=query.end_date
            )
        )

        if dates[-1] != query.end_date:
            dates.append(query.end_date)  # type: ignore

        chunks = [
            (dates[i], dates[i + 1] - timedelta(days=1)) for i in range(len(dates) - 1)
        ]

        chunks[-1] = (chunks[-1][0], query.end_date)  # type: ignore

        async def create_task(start, end, results):
            """Fetch one date chunk of filings."""
            data = await amake_gql_request(
                "getCompanyFilings",
                gql.COMPANY_FILINGS,
                {
                    "symbol": symbol,
                    "fromDate": start.strftime("%Y-%m-%d"),
                    "toDate": end.strftime("%Y-%m-%d"),
                    "limit": 1000,
                },
                symbol=symbol,
            )

            if data and data.get("filings"):
                results.extend(data["filings"])

            return results

        tasks = [create_task(chunk[0], chunk[1], results) for chunk in chunks]

        await asyncio.gather(*tasks)

        return sorted(results, key=lambda x: x["filingDate"], reverse=True)

    @staticmethod
    def transform_data(
        query: TmxCompanyFilingsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxCompanyFilingsData]:
        """Return the transformed data."""
        return [TmxCompanyFilingsData.model_validate(d) for d in data]
