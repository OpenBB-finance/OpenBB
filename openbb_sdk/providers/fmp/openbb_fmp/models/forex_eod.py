"""FMP Forex end of day fetcher."""


from datetime import datetime
from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.metadata import DATA_DESCRIPTIONS
from openbb_provider.models.forex_eod import ForexEODData, ForexEODQueryParams
from pydantic import Field, validator

from openbb_fmp.utils.helpers import get_data_many, get_querystring


class FMPForexEODQueryParams(ForexEODQueryParams):
    """FMP Forex end of day Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price
    """


class FMPForexEODData(ForexEODData):
    """FMP Forex end of day Data."""

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
    vwap: Optional[float] = Field(
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


class FMPForexEODFetcher(
    Fetcher[
        ForexEODQueryParams,
        ForexEODData,
        FMPForexEODQueryParams,
        FMPForexEODData,
    ]
):
    @staticmethod
    def transform_query(
        query: ForexEODQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPForexEODQueryParams:
        return FMPForexEODQueryParams(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            **extra_params or {},
        )

    @staticmethod
    def extract_data(
        query: FMPForexEODQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPForexEODData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.dict(), ["symbol"])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}/historical-price-full/forex/{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, FMPForexEODData, "historical")

    @staticmethod
    def transform_data(data: List[FMPForexEODData]) -> List[ForexEODData]:
        return data_transformer(data, ForexEODData)
