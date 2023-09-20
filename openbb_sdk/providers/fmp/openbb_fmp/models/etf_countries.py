"""FMP ETF Countries fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_countries import (
    EtfCountriesData,
    EtfCountriesQueryParams,
)
from openbb_provider.utils.helpers import make_request


class FMPEtfCountriesQueryParams(EtfCountriesQueryParams):
    """FMP ETF Countries Query Params"""


class FMPEtfCountriesData(EtfCountriesData):
    """FMP ETF Countries Data."""

    class Config:
        fields = {
            "weight": "weightPercentage",
        }


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
    def get_countries(symbol: str, api_key: str) -> Dict:
        """Get countries."""
        url = f"https://financialmodelingprep.com/api/v3/etf-country-weightings/{symbol}?apikey={api_key}"
        r = make_request(url)
        data = {}
        if len(r.json()) > 0:
            df = pd.DataFrame(r.json()).set_index("country")
            for i in df.index:
                data.update({i: df.loc[i]["weightPercentage"].replace("%", "")})
        return data

    @staticmethod
    def extract_data(
        query: FMPEtfCountriesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        results = {}
        for symbol in symbols:
            result = FMPEtfCountriesFetcher.get_countries(symbol, api_key)  # type: ignore
            if result != {}:
                results.update({symbol: result})

        return (
            pd.DataFrame(results)
            .transpose()
            .reset_index()
            .rename(columns={"index": "symbol"})
            .to_dict("records")
        )

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPEtfCountriesData]:
        """Return the transformed data."""
        return [FMPEtfCountriesData(**d) for d in data]
