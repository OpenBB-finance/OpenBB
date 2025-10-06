"""TMX ETF Countries fetcher."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_countries import (
    EtfCountriesData,
    EtfCountriesQueryParams,
)
from pydantic import Field, field_validator


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

    @field_validator("weight", mode="before", check_fields=False)
    @classmethod
    def _normalize_percent(cls, v):
        """Normalize percent values."""
        return v / 100 if v else None


class TmxEtfCountriesFetcher(
    Fetcher[
        TmxEtfCountriesQueryParams,
        list[TmxEtfCountriesData],
    ]
):
    """TMX ETF Countries Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEtfCountriesQueryParams:
        """Transform the query."""
        return TmxEtfCountriesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEtfCountriesQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        # pylint: disable=import-outside-toplevel
        import warnings  # noqa
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_tmx.utils.helpers import get_all_etfs
        from pandas import DataFrame

        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        _data = DataFrame(await get_all_etfs(use_cache=query.use_cache))
        results: list = []

        for symbol in symbols:
            if ".TO" in symbol:
                symbol = symbol.replace(".TO", "")  # noqa

            _target = _data[_data["symbol"] == symbol]["regions"]
            target = DataFrame()

            if len(_target) > 0:
                target = DataFrame.from_records(_target.iloc[0]).rename(
                    columns={"name": "country", "percent": "weight"}
                )
                if not target.empty:
                    target.loc[:, "symbol"] = symbol
                    result = (
                        target[["symbol", "country", "weight"]]
                        .reset_index(drop=True)
                        .to_dict("records")
                    )
                    results.extend(result)
            else:
                warnings.warn(f"No data found for {symbol}")

        if not results:
            raise EmptyDataError("No countries info found for the given symbol(s).")

        return results

    @staticmethod
    def transform_data(
        query: TmxEtfCountriesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[TmxEtfCountriesData]:
        """Return the transformed data."""
        return [TmxEtfCountriesData.model_validate(d) for d in data]
