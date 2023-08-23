"""FMP Major Indices end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.major_indices_eod import (
    MajorIndicesEODData,
    MajorIndicesEODQueryParams,
)
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, NonNegativeInt, validator

from openbb_fmp.utils.helpers import get_data_many


class FMPMajorIndicesEODQueryParams(MajorIndicesEODQueryParams):
    """FMP Major Indices end of day Query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-index-price-api/
    """

    timeseries: Optional[NonNegativeInt] = Field(
        default=None, description="Number of days to look back."
    )
    interval: Literal[
        "1min", "5min", "15min", "30min", "1hour", "4hour", "1day"
    ] = Field(default="1day", description="Interval of the data to fetch.")


class FMPMajorIndicesEODData(MajorIndicesEODData):
    """FMP Major Indices end of day Data."""

    adjClose: Optional[float] = Field(
        description="Adjusted Close Price of the symbol.",
        alias="adj_close",
        default=None,
    )
    unadjustedVolume: Optional[float] = Field(
        description="Unadjusted volume of the symbol.",
        alias="unadjusted_volume",
        default=None,
    )
    change: Optional[float] = Field(
        description="Change in the price of the symbol from the previous day.",
        alias="change",
        default=None,
    )
    changePercent: Optional[float] = Field(
        description=r"Change \% in the price of the symbol.",
        alias="change_percent",
        default=None,
    )
    label: Optional[str] = Field(
        description="Human readable format of the date.", default=None
    )
    changeOverTime: Optional[float] = Field(
        description=r"Change \% in the price of the symbol over a period of time.",
        alias="change_over_time",
        default=None,
    )

    @validator("date", pre=True)
    def date_validate(  # pylint: disable=E0213
        cls, v, values: Dict[str, Any]
    ) -> datetime:
        """Return the date as a datetime object."""
        if values.get("changeOverTime", None) is not None:
            return datetime.strptime(v, "%Y-%m-%d")
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPMajorIndicesEODFetcher(
    Fetcher[
        FMPMajorIndicesEODQueryParams,
        List[FMPMajorIndicesEODData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPMajorIndicesEODQueryParams:
        """Transform the query params."""
        return FMPMajorIndicesEODQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPMajorIndicesEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/historical-chart/{query.interval}/%5E{query.symbol}?&apikey={api_key}"

        if query.interval == "1day":
            query_str = get_querystring(query.dict(by_alias=True), ["symbol"])
            query_str = query_str.replace("start_date", "from").replace(
                "end_date", "to"
            )
            url = f"{base_url}/historical-price-full/index/%5E{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPMajorIndicesEODData]:
        """Return the transformed data."""
        return [FMPMajorIndicesEODData(**d) for d in data]
