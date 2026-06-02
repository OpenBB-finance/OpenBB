"""FRED Series Model."""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fred_series import (
    SeriesData,
    SeriesQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class FredSeriesQueryParams(SeriesQueryParams):
    """FRED Series Query Params."""

    __alias_dict__ = {
        "symbol": "series_id",
        "start_date": "observation_start",
        "end_date": "observation_end",
        "transform": "units",
    }
    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
    }

    frequency: (
        Literal[
            "a",
            "q",
            "m",
            "w",
            "d",
            "wef",
            "weth",
            "wew",
            "wetu",
            "wem",
            "wesu",
            "wesa",
            "bwew",
            "bwem",
        ]
        | None
    ) = Field(
        default=None,
        description="""Frequency aggregation to convert high frequency data to lower frequency.
    None = No change
    a = Annual
    q = Quarterly
    m = Monthly
    w = Weekly
    d = Daily
    wef = Weekly, Ending Friday
    weth = Weekly, Ending Thursday
    wew = Weekly, Ending Wednesday
    wetu = Weekly, Ending Tuesday
    wem = Weekly, Ending Monday
    wesu = Weekly, Ending Sunday
    wesa = Weekly, Ending Saturday
    bwew = Biweekly, Ending Wednesday
    bwem = Biweekly, Ending Monday""",
    )
    aggregation_method: Literal["avg", "sum", "eop"] | None = Field(
        default="eop",
        description="""A key that indicates the aggregation method used for frequency aggregation.
        This parameter has no affect if the frequency parameter is not set.
        avg = Average
        sum = Sum
        eop = End of Period
        """,
    )
    transform: (
        Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"] | None
    ) = Field(
        default=None,
        description="""Transformation type
    None = No transformation
    chg = Change
    ch1 = Change from Year Ago
    pch = Percent Change
    pc1 = Percent Change from Year Ago
    pca = Compounded Annual Rate of Change
    cch = Continuously Compounded Rate of Change
    cca = Continuously Compounded Annual Rate of Change
    log = Natural Log""",
    )
    limit: int = Field(description=QUERY_DESCRIPTIONS.get("limit", ""), default=100000)


class FredSeriesData(SeriesData):
    """FRED Series Data."""


class FredSeriesFetcher(
    Fetcher[
        FredSeriesQueryParams,
        list[FredSeriesData],
    ]
):
    """FRED Series Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FredSeriesQueryParams:
        """Transform query."""
        return FredSeriesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        from openbb_core.provider.utils.helpers import get_querystring
        from openbb_fred.utils.rate_limiter import fred_get
        from pandas import DataFrame

        api_key = credentials.get("fred_api_key") if credentials else ""

        base_url = "https://api.stlouisfed.org/fred/series/observations"
        metadata_url = "https://api.stlouisfed.org/fred/series"

        querystring = get_querystring(query.model_dump(), ["series_id"])
        series_ids = query.symbol.split(",") if "," in query.symbol else [query.symbol]

        async def fetch_one(series_id: str) -> dict:
            obs_url = f"{base_url}?series_id={series_id}&{querystring}&file_type=json&api_key={api_key}"
            meta_url = (
                f"{metadata_url}?series_id={series_id}&file_type=json&api_key={api_key}"
            )

            observations_response = await fred_get(obs_url, timeout=5, **kwargs)
            metadata_response = await fred_get(meta_url, timeout=5, **kwargs)

            _metadata = (
                metadata_response.get("seriess", [{}])[0]
                if isinstance(metadata_response, dict)
                else {}
            ) or {}
            observations = (
                observations_response.get("observations")
                if isinstance(observations_response, dict)
                else []
            ) or []

            try:
                for d in observations:
                    d.pop("realtime_start")
                    d.pop("realtime_end")

                data = (
                    DataFrame(observations)
                    .replace(".", None)
                    .set_index("date")["value"]
                    .astype(float)
                    .dropna()
                    .to_dict()
                )
            except (KeyError, TypeError):
                return {}

            return {
                series_id: {
                    "title": _metadata.get("title"),
                    "units": _metadata.get("units"),
                    "frequency": _metadata.get("frequency"),
                    "seasonal_adjustment": _metadata.get("seasonal_adjustment"),
                    "notes": _metadata.get("notes"),
                    "data": data,
                }
            }

        try:
            results: list[dict] = []
            for result in await asyncio.gather(
                *[fetch_one(sid) for sid in series_ids], return_exceptions=True
            ):
                if isinstance(result, Exception):
                    raise result
                if result:
                    results.append(result)  # type: ignore
            return results
        except OpenBBError:
            raise
        except Exception as e:
            message = str(e) or f"FRED request failed ({type(e).__name__})."
            raise OpenBBError(message) from e

    @staticmethod
    def transform_data(
        query: FredSeriesQueryParams, data: list[dict], **kwargs: Any
    ) -> AnnotatedResult[list[FredSeriesData]]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame  # noqa
        from numpy import nan

        series = {_id: s.pop("data", {}) for d in data for _id, s in d.items()}
        metadata = {_id: m for d in data for _id, m in d.items()}
        records = (
            DataFrame(series)
            .filter(items=query.symbol.split(","), axis=1)
            .sort_index()
            .reset_index()
            .rename(columns={"index": "date"})
            .replace({nan: None})
            .to_dict("records")
        )
        validated = [FredSeriesData.model_validate(r) for r in records]
        return AnnotatedResult(result=validated, metadata=metadata)
