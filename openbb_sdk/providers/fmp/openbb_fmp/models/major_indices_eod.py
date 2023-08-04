"""FMP Major Indices end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.major_indices_eod import (
    MajorIndicesEODData,
    MajorIndicesEODQueryParams,
)
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, NonNegativeFloat, NonNegativeInt, validator

from openbb_fmp.utils.helpers import get_data_many, get_querystring


class FMPMajorIndicesEODQueryParams(MajorIndicesEODQueryParams):
    """FMP Major Indices end of day Query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-index-price-api/
    """

    timeseries: Optional[NonNegativeInt] = Field(
        default=None, description="Number of days to look back."
    )


class FMPMajorIndicesEODData(MajorIndicesEODData):
    """FMP Major Indices end of day Data."""

    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    adjClose: float = Field(
        description="Adjusted Close Price of the symbol.", alias="adj_close"
    )
    unadjustedVolume: float = Field(
        description="Unadjusted volume of the symbol.", alias="unadjusted_volume"
    )
    change: float = Field(
        description="Change in the price of the symbol from the previous day.",
        alias="change",
    )
    changePercent: float = Field(
        description=r"Change \% in the price of the symbol.", alias="change_percent"
    )
    vwap: NonNegativeFloat = Field(
        description="Volume Weighted Average Price of the symbol."
    )
    label: str = Field(description="Human readable format of the date.")
    changeOverTime: float = Field(
        description=r"Change \% in the price of the symbol over a period of time.",
        alias="change_over_time",
    )

    @validator("date", pre=True)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPMajorIndicesEODFetcher(
    Fetcher[
        MajorIndicesEODQueryParams,
        MajorIndicesEODData,
        FMPMajorIndicesEODQueryParams,
        FMPMajorIndicesEODData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPMajorIndicesEODQueryParams:
        return FMPMajorIndicesEODQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPMajorIndicesEODQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPMajorIndicesEODData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.dict(by_alias=True), ["symbol"])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}/historical-price-full/index/%5E{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, FMPMajorIndicesEODData, "historical")

    @staticmethod
    def transform_data(
        data: List[FMPMajorIndicesEODData],
    ) -> List[FMPMajorIndicesEODData]:
        return data
