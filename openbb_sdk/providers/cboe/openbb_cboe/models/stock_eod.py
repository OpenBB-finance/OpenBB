"""CBOE Stock EOD fetcher."""

# IMPORT STANDARD
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.stock_eod import StockEODData, StockEODQueryParams
from pydantic import validator

from openbb_cboe.utils.helpers import get_eod_prices


class CboeStockEODQueryParams(StockEODQueryParams):
    """CBOE Stock end of day query.

    Source: https://www.cboe.com/
    """


class CboeStockEODData(StockEODData):
    """CBOE  stocks  end of day Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class CboeStockEODFetcher(
    Fetcher[
        CboeStockEODQueryParams,
        CboeStockEODData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeStockEODQueryParams:
        now = datetime.now()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=50000)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now
        return CboeStockEODQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: CboeStockEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[CboeStockEODData]:
        data = get_eod_prices(query.symbol, query.start_date, query.end_date).to_dict(
            "records"
        )
        data_ = {}
        data_.update({"results": data})
        return [CboeStockEODData.parse_obj(d) for d in data_.get("results", [])]

    @staticmethod
    def transform_data(data: List[CboeStockEODData]) -> List[CboeStockEODData]:
        return data
