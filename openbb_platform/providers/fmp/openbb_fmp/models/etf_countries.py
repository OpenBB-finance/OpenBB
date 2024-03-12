"""FMP ETF Countries Model."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_countries import (
    EtfCountriesData,
    EtfCountriesQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPEtfCountriesQueryParams(EtfCountriesQueryParams):
    """FMP ETF Countries Query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class FMPEtfCountriesData(EtfCountriesData):
    """FMP ETF Countries Data."""


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
    async def aextract_data(
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
            data = {}
            url = create_url(
                version=3,
                endpoint=f"etf-country-weightings/{symbol}",
                api_key=api_key,
            )
            result = await get_data_many(url, **kwargs)
            df = pd.DataFrame(result).set_index("country")
            if len(df) > 0:
                for i in df.index:
                    data.update(
                        {
                            i: float(df.loc[i]["weightPercentage"].replace("%", ""))
                            * 0.01
                        }
                    )
                results.update({symbol: data})

        output = (
            pd.DataFrame(results)
            .transpose()
            .reset_index()
            .fillna(value=0)
            .replace(0, None)
            .rename(columns={"index": "symbol"})
        ).transpose()
        output.columns = output.loc["symbol"].to_list()
        output = output.drop("symbol", axis=0).sort_values(
            by=output.columns[0], ascending=False
        )

        return (
            output.reset_index().rename(columns={"index": "country"}).to_dict("records")
        )

    @staticmethod
    def transform_data(
        query: FMPEtfCountriesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEtfCountriesData]:
        """Return the transformed data."""
        return [FMPEtfCountriesData.model_validate(d) for d in data]
