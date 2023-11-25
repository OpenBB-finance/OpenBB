"""FRED Releases Search Model."""

from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_releases_search import (
    EconomicReleasesSearchData,
    EconomicReleasesSearchQueryParams,
)


class FredReleasesSearchQueryParams(EconomicReleasesSearchQueryParams):
    """FRED Releases Search Query Params."""


class FredReleasesSearchData(EconomicReleasesSearchData):
    """FRED Releases SearchData."""

    __alias_dict__ = {"url": "link"}


class FredEconomicReleasesSearchFetcher(
    Fetcher[
        FredReleasesSearchQueryParams,
        List[FredReleasesSearchData],
    ]
):
    """FRED Economic Releases Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredReleasesSearchQueryParams:
        """Transform query."""
        return FredReleasesSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FredReleasesSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data."""

        api_key = credentials.get("fred_api_key") if credentials else ""
        url = (
            f"https://api.stlouisfed.org/fred/releases?api_key={api_key}&file_type=json"
        )

        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            raise RuntimeError(f"Error with the FRED request: {response.status_code}")

        return response.json().get("releases")

    @staticmethod
    def transform_data(
        query: FredReleasesSearchQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FredReleasesSearchData]:
        """Transform data."""

        [d.pop("realtime_start") for d in data]
        [d.pop("realtime_end") for d in data]
        df = pd.DataFrame.from_records(data).fillna("N/A").replace("N/A", None)
        if query.query is not None:
            df = df[
                df["name"].str.contains(query.query, case=False)
                | df["notes"].str.contains(query.query, case=False)
            ]

        return [FredReleasesSearchData.model_validate(d) for d in df.to_dict("records")]
