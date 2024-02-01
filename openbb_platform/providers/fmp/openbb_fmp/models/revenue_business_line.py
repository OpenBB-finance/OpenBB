"""FMP Revenue by Business Line Model."""

# pylint: disable=unused-argument
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.revenue_business_line import (
    RevenueBusinessLineData,
    RevenueBusinessLineQueryParams,
)
from openbb_fmp.models.cash_flow import FMPCashFlowStatementFetcher
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import field_validator


class FMPRevenueBusinessLineQueryParams(RevenueBusinessLineQueryParams):
    """FMP Revenue by Business Line Query.

    Source: https://site.financialmodelingprep.com/developer/docs/sales-revenue-by-segments-api/
    """


class FMPRevenueBusinessLineData(RevenueBusinessLineData):
    """FMP Revenue by Business Line Data."""

    @field_validator("period_ending", "filing_date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None


class FMPRevenueBusinessLineFetcher(
    Fetcher[  # type: ignore
        FMPRevenueBusinessLineQueryParams,
        List[FMPRevenueBusinessLineData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPRevenueBusinessLineQueryParams:
        """Transform the query params."""
        return FMPRevenueBusinessLineQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPRevenueBusinessLineQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "revenue-product-segmentation", api_key, query)

        cf_fetcher = FMPCashFlowStatementFetcher()
        cf_query = cf_fetcher.transform_query(
            {"symbol": query.symbol, "period": query.period, "limit": 200}
        )
        cf_data = await cf_fetcher.aextract_data(cf_query, {"fmp_api_key": api_key})
        filing_dates = sorted(
            [
                {
                    "period_ending": d["date"],
                    "fiscal_year": d["calendarYear"],
                    "fiscal_period": d["period"],
                    "filing_date": d["fillingDate"],
                }
                for d in cf_data
            ],
            key=lambda d: d["period_ending"],
        )
        rev_data = await get_data_many(url, **kwargs)
        rev_data_dict = {list(d.keys())[0]: list(d.values())[0] for d in rev_data}
        combined_data = [
            {**d, "business_line": rev_data_dict[d["period_ending"]]}
            for d in filing_dates
            if d["period_ending"] in rev_data_dict
        ]
        return combined_data

    @staticmethod
    def transform_data(
        query: FMPRevenueBusinessLineQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPRevenueBusinessLineData]:
        """Return the transformed data."""
        return [FMPRevenueBusinessLineData.model_validate(d) for d in data]
