"""FMP ETF Country Weighting fetcher."""

from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_countries import (
    EtfCountriesData,
    EtfCountriesQueryParams,
)


class FMPEtfCountriesQueryParams(EtfCountriesQueryParams):
    """FMP ETF Country Weighting Params."""


class FMPEtfCountriesData(EtfCountriesData):
    """FMP ETF Country Weighting Data."""

    __alias_dict__ = {"weight": "weightPercentage"}


class FMPEtfCountriesFetcher(
    Fetcher[
        FMPEtfCountriesQueryParams,
        List[FMPEtfCountriesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfCountriesQueryParams:
        """Transform the query."""
        return FMPEtfCountriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPEtfCountriesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            version=3,
            endpoint=f"etf-country-weightings/{query.symbol.upper()}",
            api_key=api_key,
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEtfCountriesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEtfCountriesData]:
        """Return the transformed data."""
        for d in data:
            if d["weightPercentage"] is not None and d["weightPercentage"].endswith(
                "%"
            ):
                d["weightPercentage"] = float(d["weightPercentage"][:-1]) / 100
        return [FMPEtfCountriesData.model_validate(d) for d in data]
