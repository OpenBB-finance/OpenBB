"""FMP Executive Compensation Model."""

import asyncio
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.executive_compensation import (
    ExecutiveCompensationData,
    ExecutiveCompensationQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import response_callback
from pydantic import Field, field_validator


class FMPExecutiveCompensationQueryParams(ExecutiveCompensationQueryParams):
    """FMP Executive Compensation Query.

    Source: https://site.financialmodelingprep.com/developer/docs/executive-compensation-api/
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    year: Optional[int] = Field(default=None, description="Year of the compensation.")


class FMPExecutiveCompensationData(ExecutiveCompensationData):
    """FMP Executive Compensation Data."""

    __alias_dict__ = {
        "company_name": "companyName",
        "industry": "industryTitle",
    }

    filing_date: Optional[dateType] = Field(
        default=None, description="Date of the filing."
    )
    accepted_date: Optional[datetime] = Field(
        default=None, description="Date the filing was accepted."
    )
    url: Optional[str] = Field(default=None, description="URL to the filing data.")

    @field_validator("filingDate", mode="before", check_fields=False)
    @classmethod
    def filing_date_validate(cls, v):  # pylint: disable=E0213
        """Return the filing date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")

    @field_validator("acceptedDate", mode="before", check_fields=False)
    @classmethod
    def accepted_date_validate(cls, v):  # pylint: disable=E0213
        """Return the accepted date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPExecutiveCompensationFetcher(
    Fetcher[
        FMPExecutiveCompensationQueryParams,
        List[FMPExecutiveCompensationData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPExecutiveCompensationQueryParams:
        """Transform the query params."""
        return FMPExecutiveCompensationQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPExecutiveCompensationQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""

        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v4/"

        symbols = query.symbol.split(",")

        results: List[dict] = []

        async def get_one(symbol):
            """Get data for one symbol."""

            url = f"{base_url}/governance/executive_compensation?symbol={symbol}&apikey={api_key}"
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result:
                warn(f"Symbol Error: No data found for {symbol}.")

            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data found for given symbols.")

        return sorted(results, key=lambda x: (x["year"]), reverse=True)

    @staticmethod
    def transform_data(
        query: FMPExecutiveCompensationQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPExecutiveCompensationData]:
        """Return the transformed data."""
        results: List[FMPExecutiveCompensationData] = []
        for d in data:
            if "year" in d and query.year is not None:
                if d["year"] >= query.year and d["year"] <= query.year:
                    results.append(FMPExecutiveCompensationData.model_validate(d))
            else:
                results.append(FMPExecutiveCompensationData.model_validate(d))
        return results
