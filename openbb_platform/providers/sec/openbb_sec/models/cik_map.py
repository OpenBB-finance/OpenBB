"""SEC CIK Mapping Tool."""

from typing import Any, Dict, Optional, Union

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.equity_info import EquityInfoQueryParams
from openbb_sec.utils.helpers import symbol_map
from pydantic import Field


class SecCikMapQueryParams(EquityInfoQueryParams):
    """SEC Company or Institutions Search query.  This function assists with mapping the CIK number to a company."""


class SecCikMapData(Data):
    """SEC Company Search Data."""

    cik: Optional[Union[str, int]] = Field(
        default=None, description="Central Index Key"
    )


class SecCikMapFetcher(
    Fetcher[
        SecCikMapQueryParams,
        SecCikMapData,
    ]
):
    """Transform the query, extract and transform the data from the SEC."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecCikMapQueryParams:
        """Transform the query."""
        return SecCikMapQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecCikMapQueryParams,  # pylint: disable=W0613:unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the SEC endpoint."""
        results = {"cik": symbol_map(query.symbol)}
        if not results:
            return {"Error": "Symbol not found."}
        return results

    @staticmethod
    def transform_data(
        query: SecCikMapQueryParams, data: Dict, **kwargs: Any
    ) -> SecCikMapData:
        """Transform the data to the standard format."""
        return SecCikMapData.model_validate(data)
