"""Intrinio Zack Sales Estimates Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.sales_estimates import (
    SalesEstimatesData,
    SalesEstimatesQueryParams,
)
from openbb_fmp.utils.helpers import get_data_many


class IntrinioZackSalesEstimatesQueryParams(SalesEstimatesQueryParams):
    """Intrinio Zack Sales Estimates Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_zacks_sales_estimates_v2
    """


class IntrinioZackSalesEstimatesData(SalesEstimatesData):
    """Intrinio Zack Sales Estimates Data."""


class IntrinioZackSalesEstimatesFetcher(
    Fetcher[
        IntrinioZackSalesEstimatesQueryParams,
        List[IntrinioZackSalesEstimatesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioZackSalesEstimatesQueryParams:
        """Transform the query params."""
        return IntrinioZackSalesEstimatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioZackSalesEstimatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        sales_estimates_url = f"https://api-v2.intrinio.com/zacks/sales_estimates?identifier={query.symbol}"

        if query.start_date is not None:
            sales_estimates_url = sales_estimates_url + f"&start_date={query.start_date}"
        if query.end_date is not None:
            sales_estimates_url = sales_estimates_url + f"&end_date={query.end_date}"
        if query.fiscal_year is not None:
            sales_estimates_url = sales_estimates_url + f"&fiscal_year={query.fiscal_year}"
        if query.fiscal_period is not None:
            sales_estimates_url = sales_estimates_url + f"&fiscal_period={query.fiscal_period}"
        if query.calendar_year is not None:
            sales_estimates_url = sales_estimates_url + f"&calendar_year={query.calendar_year}"
        if query.calendar_period is not None:
            sales_estimates_url = sales_estimates_url + f"&calendar_period={query.calendar_period}"
        if query.next_page is not None:
            sales_estimates_url = sales_estimates_url + f"&next_page={query.next_page}"
        if query.page_size is not None:
            sales_estimates_url = sales_estimates_url + f"&page_size={query.page_size}"
        sales_estimates_url = sales_estimates_url + f"&api_key={api_key}"

        return await get_data_many(sales_estimates_url, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioZackSalesEstimatesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioZackSalesEstimatesData]:
        """Return the transformed data."""
        return [IntrinioZackSalesEstimatesData.model_validate(d) for d in data]
