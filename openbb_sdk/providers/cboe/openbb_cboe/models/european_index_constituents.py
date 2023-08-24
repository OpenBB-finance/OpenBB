"""CBOE European Index Constituents fetcher."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.european_index_constituents import (
    EuropeanIndexConstituentsData,
    EuropeanIndexConstituentsQueryParams,
)
from pydantic import Field, validator

from openbb_cboe.utils.helpers import Europe


class CboeEuropeanIndexConstituentsQueryParams(EuropeanIndexConstituentsQueryParams):
    """CBOE Stock end of day query.

    Source: https://www.cboe.com/

    Gets the current price data for all constituents of the CBOE European Index.
    """


class CboeEuropeanIndexConstituentsData(EuropeanIndexConstituentsData):
    """CBOE European Index Constituents Data.

    Current trading day price data for all constituents of the CBOE European Index.
    """

    prev_close: Optional[float] = Field(description="Previous closing  price.")
    change: Optional[float] = Field(description="Change in price.")
    change_percent: Optional[float] = Field(
        description="Change in price as a percentage."
    )
    tick: Optional[str] = Field(
        description="Whether the last sale was an up or down tick."
    )
    last_trade_timestamp: Optional[datetime] = Field(
        description="Last trade timestamp for the symbol."
    )
    exchange_id: Optional[int] = Field(description="The Exchange ID number.")
    seqno: Optional[int] = Field(
        description="Sequence number of the last trade on the tape."
    )
    type: Optional[str] = Field(description="Type of asset.")

    @validator("last_trade_timestamp", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string"""

        return datetime.strftime(v, "%Y-%m-%d %H:%M:%S")


class CboeEuropeanIndexConstituentsFetcher(
    Fetcher[
        CboeEuropeanIndexConstituentsQueryParams,
        List[CboeEuropeanIndexConstituentsData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints"""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> CboeEuropeanIndexConstituentsQueryParams:
        """Transform the query."""

        return CboeEuropeanIndexConstituentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeEuropeanIndexConstituentsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint"""

        return Europe.get_index_constituents_quotes(query.symbol).to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict]) -> List[CboeEuropeanIndexConstituentsData]:
        """Transform the data to the standard format"""

        return [CboeEuropeanIndexConstituentsData.parse_obj(d) for d in data]
