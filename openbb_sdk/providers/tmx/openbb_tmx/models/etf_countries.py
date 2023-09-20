"""TMX ETF Countries fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_countries import (
    EtfCountriesData,
    EtfCountriesQueryParams,
)

from openbb_tmx.utils.helpers import get_all_etfs


class TmxEtfCountriesQueryParams(EtfCountriesQueryParams):
    """TMX ETF Countries Query Params"""


class TmxEtfCountriesData(EtfCountriesData):
    """TMX ETF Countries Data."""


class TmxEtfCountriesFetcher(
    Fetcher[
        TmxEtfCountriesQueryParams,
        List[TmxEtfCountriesData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEtfCountriesQueryParams:
        """Transform the query."""
        return TmxEtfCountriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxEtfCountriesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )

        _data = get_all_etfs()
        results = {}
        for symbol in symbols:
            data = {}
            if ".TO" in symbol:
                symbol = symbol.replace(".TO", "")  # noqa
            _target = _data[_data["symbol"] == symbol]["regions"]
            target = pd.DataFrame()
            if len(_target) > 0:
                target = pd.DataFrame.from_records(_target.iloc[0]).rename(
                    columns={"name": "country", "percent": "weight"}
                )
                if not target.empty:
                    target = target.set_index("country")
                for i in target.index:
                    data.update({i: target.loc[i]["weight"]})
                if data != {}:
                    results.update({symbol: data})

        return (
            pd.DataFrame(results)
            .transpose()
            .reset_index()
            .rename(columns={"index": "symbol"})
            .to_dict("records")
        )

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxEtfCountriesData]:
        """Return the transformed data."""
        return [TmxEtfCountriesData(**d) for d in data]
