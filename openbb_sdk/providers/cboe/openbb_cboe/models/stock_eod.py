"""CBOE Stock Historical fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_eod import (
    StockHistoricalData,
    StockHistoricalQueryParams,
)
from pydantic import validator

from openbb_cboe.utils.helpers import get_eod_prices


class CboeStockHistoricalQueryParams(StockHistoricalQueryParams):
    """CBOE Stock end of day query.

    Source: https://www.cboe.com/
    """


class CboeStockHistoricalData(StockHistoricalData):
    """CBOE Stocks End of Day Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string"""

        return datetime.strptime(v, "%Y-%m-%d")


class CboeStockHistoricalFetcher(
    Fetcher[
        CboeStockHistoricalQueryParams,
        List[CboeStockHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeStockHistoricalQueryParams:
        """Transform the query. Setting the start and end dates for a 1 year period."""
        transformed_params = params

        now = datetime.now()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return CboeStockHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: CboeStockHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the CBOE endpoint"""
        return get_eod_prices(query.symbol, query.start_date, query.end_date).to_dict(
            "records"
        )

    @staticmethod
    def transform_data(data: dict) -> List[CboeStockHistoricalData]:
        """Transform the data to the standard format"""
        return [CboeStockHistoricalData.parse_obj(d) for d in data]
