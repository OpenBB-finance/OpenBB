"""FRED Regional Data Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional, Union

import json
import warnings

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
    }
    symbol: str = Field(
        description="For this function, it is the series_group ID found by searching by series ID."
    )
    start_date: Optional[dateType] = Field(
        default="1900-01-01",
        description="The start date for the data."
        + " This is required for the FRED API, so a default start date is generously set.",
    )
    region_type: Literal[
        "bea",
        "msa",
        "frb",
        "necta",
        "state",
        "country",
        "county",
        "censusregion",
    ] = Field(
        description="The type of regional data."
        + " This must match the value returned from searching by series ID."
    )
    season: Literal[
        "SA",
        "NSA",
        "SSA",
    ] = Field(
        description="The seasonal adjustments to the data."
        + " This must match the value returned from searching by series ID."
    )
    units: str = Field(
        description="The units of the data."
        + " This should match the units returned when searching by series ID,"
        + " but an incorrect field will not necessarily return an error."
    )
    frequency: Union[
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
        None,
    ] = Field(
        default="a",
        description="""
        Frequency aggregation to convert high frequency data to lower frequency.
        The frequency of the series can be determined by searching by series ID.
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
    aggregation_method: Literal[None, "avg", "sum", "eop"] = Field(
        default="avg",
        description="""
        A key that indicates the aggregation method used for frequency aggregation.
        This parameter has no affect if the frequency parameter is not set.
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
        Transformation type
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
        if values.get("start_date") is None:
            values["start_date"] = "1900-01-01"
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
        base_url = "https://api.stlouisfed.org/geofred/regional/data?"
        url = (
            base_url
            + get_querystring(query.model_dump(), ["limit"])
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
                results.append(FredRegionalData.model_validate(item))
        return results
