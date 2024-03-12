"""FRED Regional Data Model."""

# pylint: disable=unused-argument
import json
import warnings
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fred_series import (
    SeriesData,
    SeriesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import (
    amake_request,
    get_querystring,
)
from pydantic import Field, model_validator

_warn = warnings.warn


class FredRegionalQueryParams(SeriesQueryParams):
    """FRED Regional Data Query Params."""

    __alias_dict__ = {
        "symbol": "series_group",
        "transform": "transformation",
    }
    symbol: str = Field(
        description="For this function, it is the series_group ID or series ID."
        + " If the symbol provided is for a series_group, set the `is_series_group` parameter to True."
        + " Not all series that are in FRED have geographical data."
    )
    is_series_group: bool = Field(
        default=False,
        description="When True, the symbol provided is for a series_group, else it is for a series ID.",
    )
    region_type: Union[
        None,
        Literal[
            "bea",
            "msa",
            "frb",
            "necta",
            "state",
            "country",
            "county",
            "censusregion",
        ],
    ] = Field(
        default=None,
        description="The type of regional data."
        + " Parameter is only valid when `is_series_group` is True.",
    )
    season: Union[
        None,
        Literal[
            "SA",
            "NSA",
            "SSA",
        ],
    ] = Field(
        default="NSA",
        description="The seasonal adjustments to the data."
        + " Parameter is only valid when `is_series_group` is True.",
    )
    units: Optional[str] = Field(
        default=None,
        description="The units of the data."
        + " This should match the units returned from searching by series ID."
        + " An incorrect field will not necessarily return an error."
        + " Parameter is only valid when `is_series_group` is True.",
    )
    frequency: Union[
        None,
        Literal[
            "d",
            "w",
            "bw",
            "m",
            "q",
            "sa",
            "a",
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
    ] = Field(
        default=None,
        description="""
        Frequency aggregation to convert high frequency data to lower frequency.
        Parameter is only valid when `is_series_group` is True.
            a = Annual
            sa= Semiannual
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
    aggregation_method: Literal["avg", "sum", "eop"] = Field(
        default="avg",
        description="""
        A key that indicates the aggregation method used for frequency aggregation.
        This parameter has no affect if the frequency parameter is not set.
        Only valid when `is_series_group` is True.
            avg = Average
            sum = Sum
            eop = End of Period
        """,
    )
    transform: Literal[
        "lin", "chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"
    ] = Field(
        default="lin",
        description="""
        Transformation type. Only valid when `is_series_group` is True.
            lin = Levels (No transformation)
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

    @model_validator(mode="before")
    @classmethod
    def transform_validate(cls, values):
        """Add default start date."""
        if values.get("is_series_group") is True:
            required = ["frequency", "region_type", "units"]
            for key in required:
                if values.get(key) is None:
                    raise ValueError(
                        f"{key} is a required field missing for series_group."
                    )

            values["start_date"] = (
                "1900-01-01"
                if values.get("start_date") is None
                else values.get("start_date")
            )
        if values.get("is_series_group") is False:
            values["start_date"] = (
                None if values.get("start_date") is None else values.get("start_date")
            )
        return values


class FredRegionalData(SeriesData):
    """FRED Regional Data."""

    __alias_dict__ = {
        "date": "observation_date",
    }
    region: str = Field(
        description="The name of the region.",
    )
    code: Union[str, int] = Field(
        description="The code of the region.",
    )
    value: Optional[Union[int, float]] = Field(
        default=None,
        description="The obersvation value. The units are defined in the search results by series ID.",
    )
    series_id: str = Field(
        description="The individual series ID for the region.",
    )


class FredRegionalDataFetcher(
    Fetcher[
        FredRegionalQueryParams,
        List[FredRegionalData],
    ]
):
    """FRED Regional Data Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredRegionalQueryParams:
        """Transform query."""
        return FredRegionalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredRegionalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract the raw data."""
        api_key = credentials.get("fred_api_key") if credentials else ""
        if query.is_series_group is True:
            base_url = "https://api.stlouisfed.org/geofred/regional/data?"
            url = (
                base_url
                + get_querystring(
                    query.model_dump(), ["limit", "end_date", "is_series_group"]
                )
                + f"&file_type=json&api_key={api_key}"
            )
        if query.is_series_group is False:
            base_url = "https://api.stlouisfed.org/geofred/series/data?"
            url = (
                base_url
                + f"series_id={query.symbol}&"
                + get_querystring(
                    query.model_dump(),
                    [
                        "limit",
                        "end_date",
                        "region_type",
                        "season",
                        "units",
                        "is_series_group",
                    ],
                )
                + f"&file_type=json&api_key={api_key}"
            )
        return await amake_request(url)  # type: ignore

    @staticmethod
    def transform_data(
        query: FredRegionalQueryParams,
        data: Dict,
        **kwargs,
    ) -> List[FredRegionalData]:
        """Flatten the response object and validate the model."""

        results: List[FredRegionalData] = []
        if data.get("meta") is None:
            raise EmptyDataError()
        meta = {k: v for k, v in data.get("meta").items() if k not in ["data"]}  # type: ignore
        if meta:
            _warn(json.dumps(meta))
        _data = data["meta"]["data"]
        keys = list(_data.keys())
        units = data["meta"].get("units")
        for key in keys:
            _row = _data[key]
            for item in _row:
                item["date"] = key
                item["units"] = units
                if (
                    query.end_date is None
                    or datetime.strptime(key, "%Y-%m-%d").date() <= query.end_date
                ):
                    results.append(FredRegionalData.model_validate(item))
        return results
