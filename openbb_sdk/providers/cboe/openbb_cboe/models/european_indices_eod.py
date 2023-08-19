"""European Indices End of Day fetcher for CBOE."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.european_indices_eod import (
    EuropeanIndicesEODData,
    EuropeanIndicesEODQueryParams,
)
from pydantic import validator

from openbb_cboe.utils.helpers import Europe


class CboeEuropeanIndicesEODQueryParams(EuropeanIndicesEODQueryParams):
    """CBOE European Indices End of Day query.

    Source: https://www.cboe.com/europe/indices/
    """


class CboeEuropeanIndicesEODData(EuropeanIndicesEODData):
    """CBOE Stocks End of Day Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string"""

        return dateType.strftime(v, "%Y-%m-%d")


class CboeEuropeanIndicesEODFetcher(
    Fetcher[
        CboeEuropeanIndicesEODQueryParams,
        List[CboeEuropeanIndicesEODData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeEuropeanIndicesEODQueryParams:
        """Transform the query."""

        return CboeEuropeanIndicesEODQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeEuropeanIndicesEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict[dateType, float]]:
        """Return the raw data from the CBOE endpoint"""

        return Europe.get_index_eod(query.symbol, query.start_date, query.end_date)

    @staticmethod
    def transform_data(
        data: List[dict[dateType, float]]
    ) -> List[CboeEuropeanIndicesEODData]:
        """Transform the data to the standard format"""

        return [CboeEuropeanIndicesEODData.parse_obj(d) for d in data]
