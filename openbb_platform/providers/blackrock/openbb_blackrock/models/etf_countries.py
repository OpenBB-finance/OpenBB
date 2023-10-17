"""Blackrock ETF Countries fetcher."""

import concurrent.futures
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_blackrock.utils.helpers import COUNTRIES, extract_from_holdings
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_countries import (
    EtfCountriesData,
    EtfCountriesQueryParams,
)
from pydantic import Field


class BlackrockEtfCountriesQueryParams(EtfCountriesQueryParams):
    """Blackrock ETF Countries Query Params"""

    country: Optional[COUNTRIES] = Field(
        description="The country the ETF is registered in.  Symbol suffix with `.TO` can be used as a proxy for Canada.",
        default="america",
    )
    date: Optional[str] = Field(
        description="The as-of date for the data.", default=None
    )


class BlackrockEtfCountriesData(EtfCountriesData):
    """Blackrock ETF Countries Data."""


class BlackrockEtfCountriesFetcher(
    Fetcher[
        BlackrockEtfCountriesQueryParams,
        List[BlackrockEtfCountriesData],
    ]
):
    """Transform the query, extract and transform the data from the Blackrock endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BlackrockEtfCountriesQueryParams:
        """Transform the query."""
        return BlackrockEtfCountriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlackrockEtfCountriesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Blackrock endpoint."""

        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        results = {}

        def get_one(symbol):
            data = {}
            data = extract_from_holdings(
                symbol,
                to_extract="country",
                country=query.country,  # type: ignore
                date=query.date,  # type: ignore
            )
            if data != {}:
                results.update({symbol: data})

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_one, symbols)

        return (
            pd.DataFrame(results)
            .transpose()
            .reset_index()
            .rename(columns={"index": "symbol"})
            .fillna(value=0)
            .to_dict("records")
        )

    @staticmethod
    def transform_data(
        data: List[Dict], **kwargs: Any
    ) -> List[BlackrockEtfCountriesData]:
        """Return the transformed data."""
        return [BlackrockEtfCountriesData(**d) for d in data]
