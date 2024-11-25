"""FRED Series Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

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
        "frequency": {
            "multiple_items_allowed": False,
            "choices": [
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
            ],
        },
        "aggregation_method": {
            "multiple_items_allowed": False,
            "choices": ["avg", "sum", "eop"],
        },
        "transform": {
            "multiple_items_allowed": False,
            "choices": [
                "chg",
                "ch1",
                "pch",
                "pc1",
                "pca",
                "cch",
                "cca",
                "log",
            ],
        },
    }

    frequency: Optional[
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
    ] = Field(
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
        bwem = Biweekly, Ending Monday
        """,
    )
    aggregation_method: Optional[Literal["avg", "sum", "eop"]] = Field(
        default="eop",
        description="""A key that indicates the aggregation method used for frequency aggregation.
        This parameter has no affect if the frequency parameter is not set.
        avg = Average
        sum = Sum
        eop = End of Period
        """,
    )
    transform: Optional[
        Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
    ] = Field(
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
        log = Natural Log
        """,
    )
    limit: int = Field(description=QUERY_DESCRIPTIONS.get("limit", ""), default=100000)


class FredSeriesData(SeriesData):
    """FRED Series Data."""


class FredSeriesFetcher(
    Fetcher[
        FredSeriesQueryParams,
        List[FredSeriesData],
    ]
):
    """FRED Series Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredSeriesQueryParams:
        """Transform query."""
        return FredSeriesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredSeriesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import (
            ClientResponse,
            ClientSession,
            amake_requests,
            get_querystring,
        )
        from pandas import DataFrame

        api_key = credentials.get("fred_api_key") if credentials else ""

        base_url = "https://api.stlouisfed.org/fred/series/observations"
        metadata_url = "https://api.stlouisfed.org/fred/series"

        querystring = get_querystring(query.model_dump(), ["series_id"])
        series_ids = query.symbol.split(",") if "," in query.symbol else [query.symbol]

        urls = [
            f"{base_url}?series_id={series_id}&{querystring}&file_type=json&api_key={api_key}"
            for series_id in series_ids
        ]

        async def callback(response: ClientResponse, session: ClientSession) -> Dict:
            observations_response = await response.json()
            series_id = response.url.query.get("series_id")

            metadata_response = await session.get_json(
                f"{metadata_url}?series_id={series_id}&file_type=json&api_key={api_key}",
                timeout=5,
            )

            # seriess is not a typo, it's the actual key in the response
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
            results = await amake_requests(urls, callback, timeout=5, **kwargs)
            return results
        except Exception as e:
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: FredSeriesQueryParams, data: List[Dict], **kwargs: Any
    ) -> AnnotatedResult[List[FredSeriesData]]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        series = {_id: s.pop("data", {}) for d in data for _id, s in d.items()}
        metadata = {_id: m for d in data for _id, m in d.items()}
        records = (
            DataFrame(series)
            .filter(items=query.symbol.split(","), axis=1)
            .reset_index()
            .rename(columns={"index": "date"})
            .fillna("N/A")
            .replace("N/A", None)
            .to_dict("records")
        )
        validated = [FredSeriesData.model_validate(r) for r in records]
        return AnnotatedResult(result=validated, metadata=metadata)
