"""FMP Forex end of day fetcher."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.forex_eod import ForexEODData, ForexEODQueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, PositiveFloat, validator

from openbb_fmp.utils.helpers import get_data_many, get_querystring


class FMPForexEODQueryParams(ForexEODQueryParams):
    """FMP Forex end of day Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price
    """


class FMPForexEODData(ForexEODData):
    """FMP Forex end of day Data."""

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
    vwap: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("vwap", ""))
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
        FMPForexEODQueryParams,
        FMPForexEODData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPForexEODQueryParams:
        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=7)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now
        return FMPForexEODQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: FMPForexEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPForexEODData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.dict(by_alias=True), ["symbol"])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}/historical-price-full/forex/{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, FMPForexEODData, "historical", **kwargs)

    @staticmethod
    def transform_data(data: List[FMPForexEODData]) -> List[FMPForexEODData]:
        return data
