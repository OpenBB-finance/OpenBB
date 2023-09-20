"""FMP Balance Sheet Growth Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.balance_sheet_growth import (
    BalanceSheetGrowthData,
    BalanceSheetGrowthQueryParams,
)
from pydantic import validator


class FMPBalanceSheetGrowthQueryParams(BalanceSheetGrowthQueryParams):
    """FMP Balance Sheet Growth QueryParams.

    Source:  https://site.financialmodelingprep.com/developer/docs/#Financial-Statements-Growth
    """


class FMPBalanceSheetGrowthData(BalanceSheetGrowthData):
    """FMP Balance Sheet Growth Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FMPBalanceSheetGrowthFetcher(
    Fetcher[
        FMPBalanceSheetGrowthQueryParams,
        List[FMPBalanceSheetGrowthData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPBalanceSheetGrowthQueryParams:
        """Transform the query params."""
        return FMPBalanceSheetGrowthQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPBalanceSheetGrowthQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3,
            f"balance-sheet-statement-growth/{query.symbol}",
            api_key,
            query,
            ["symbol"],
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPBalanceSheetGrowthData]:
        """Return the transformed data."""
        return [FMPBalanceSheetGrowthData.parse_obj(d) for d in data]
