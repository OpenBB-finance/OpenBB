"""CBOE Major Indices End of Day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.major_indices_eod import (
    MajorIndicesEODData,
    MajorIndicesEODQueryParams,
)
from pydantic import validator

from openbb_cboe.utils.helpers import get_us_eod_prices


class CboeMajorIndicesEODQueryParams(MajorIndicesEODQueryParams):
    """CBOE Stock end of day query.

    Source: https://www.cboe.com/
    """


class CboeMajorIndicesEODData(MajorIndicesEODData):
    """CBOE Stocks End of Day Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string"""

        return datetime.strptime(v, "%Y-%m-%d").date()


class CboeMajorIndicesEODFetcher(
    Fetcher[
        CboeMajorIndicesEODQueryParams,
        CboeMajorIndicesEODData,
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeMajorIndicesEODQueryParams:
        """Transform the query. Setting the start and end dates for a 1 year period."""

        transformed_params = params

        now = datetime.now()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return CboeMajorIndicesEODQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: CboeMajorIndicesEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Return the raw data from the CBOE endpoint"""

        return get_us_eod_prices(
            query.symbol, query.start_date, query.end_date
        ).to_dict("records")

    @staticmethod
    def transform_data(data: List[dict]) -> List[CboeMajorIndicesEODData]:
        """Transform the data to the standard format"""

        return [CboeMajorIndicesEODData.parse_obj(d) for d in data]
