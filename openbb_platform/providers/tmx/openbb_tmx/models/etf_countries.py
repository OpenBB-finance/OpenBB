"""TMX ETF Countries fetcher."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_countries import (
    EtfCountriesData,
    EtfCountriesQueryParams,
)
from pydantic import Field


class TmxEtfCountriesQueryParams(EtfCountriesQueryParams):
    """TMX ETF Countries Query Params"""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily."
        + " To bypass, set to False. If True, the data will be cached for 4 hours.",
    )


class TmxEtfCountriesData(EtfCountriesData):
    """TMX ETF Countries Data."""


class TmxEtfCountriesFetcher(
    Fetcher[
        TmxEtfCountriesQueryParams,
        List[TmxEtfCountriesData],
    ]
):
    """TMX ETF Countries Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEtfCountriesQueryParams:
        """Transform the query."""
        return TmxEtfCountriesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEtfCountriesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.errors import EmptyDataError  # noqa
        from openbb_tmx.utils.helpers import get_all_etfs
        from pandas import DataFrame

        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )

        _data = DataFrame(await get_all_etfs(use_cache=query.use_cache))
        results = {}
        for symbol in symbols:
            data = {}
            if ".TO" in symbol:
                symbol = symbol.replace(".TO", "")  # noqa
            _target = _data[_data["symbol"] == symbol]["regions"]
            target = DataFrame()
            if len(_target) > 0:
                target = DataFrame.from_records(_target.iloc[0]).rename(
                    columns={"name": "country", "percent": "weight"}
                )
                if not target.empty:
                    target = target.set_index("country")
                for i in target.index:
                    data.update({i: target.loc[i]["weight"]})
                if data:
                    results.update({symbol: data})
            else:
                warn(f"No data found for {symbol}")

        if not results:
            raise EmptyDataError("No countries info found for the given symbol(s).")

        output = (
            DataFrame(results)
            .transpose()
            .reset_index()
            .rename(columns={"index": "symbol"})
        ).transpose()
        output.columns = output.loc["symbol"].to_list()
        output.drop("symbol", axis=0, inplace=True)
        return (
            output.reset_index().rename(columns={"index": "country"}).to_dict("records")
        )

    @staticmethod
    def transform_data(
        query: TmxEtfCountriesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TmxEtfCountriesData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import DataFrame

        output = DataFrame(data)
        for col in output.columns.to_list():
            if col != "country":
                output[col] = output[col].astype(float) / 100
        output = output.replace({nan: None})

        return [
            TmxEtfCountriesData.model_validate(d) for d in output.to_dict("records")
        ]
