"""CBOE Equity Search Model."""

from typing import Any, Dict, List, Optional

from openbb_cboe.utils.helpers import get_cboe_directory
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from pydantic import Field


class CboeEquitySearchQueryParams(EquitySearchQueryParams):
    """CBOE Equity Search Query.

    Source: https://www.cboe.com/
    """


class CboeEquitySearchData(EquitySearchData):
    """CBOE Equity Search Data."""

    __alias_dict__ = {"name": "Company Name"}

    dpm_name: Optional[str] = Field(
        default=None,
        description="Name of the primary market maker.",
        alias="DPM Name",
    )
    post_station: Optional[str] = Field(
        default=None, description="Post and station location on the CBOE trading floor."
    )


class CboeEquitySearchFetcher(
    Fetcher[
        CboeEquitySearchQueryParams,
        List[CboeEquitySearchData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeEquitySearchQueryParams:
        """Transform the query."""
        return CboeEquitySearchQueryParams(**params)

    @staticmethod
    def extract_data(  # pylint: disable=unused-argument
        query: CboeEquitySearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the CBOE endpoint."""
        data = {}
        symbols = get_cboe_directory().reset_index().replace("nan", None)
        target = "name" if query.is_symbol is False else "symbol"
        idx = symbols[target].str.contains(query.query, case=False)
        result = symbols[idx].to_dict("records")
        data.update({"results": result})

        return data

    @staticmethod
    def transform_data(
        query: CboeEquitySearchQueryParams, data: Dict, **kwargs: Any
    ) -> List[CboeEquitySearchData]:
        """Transform the data to the standard format."""
        return [CboeEquitySearchData.model_validate(d) for d in data["results"]]
