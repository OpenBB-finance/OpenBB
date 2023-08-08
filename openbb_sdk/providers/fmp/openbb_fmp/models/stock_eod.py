"""FMP Stocks end of day fetcher."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.stock_eod import StockEODData, StockEODQueryParams
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, NonNegativeInt, validator

from openbb_fmp.utils.helpers import get_data_many


class FMPStockEODQueryParams(StockEODQueryParams):
    """FMP Stock end of day Query.

    Source: https://financialmodelingprep.com/developer/docs/#Stock-Historical-Price
    """

    timeseries: Optional[NonNegativeInt] = Field(
        default=None, description="Number of days to look back."
    )
    interval: Literal[
        "1min", "5min", "15min", "30min", "1hour", "4hour", "1day"
    ] = Field(default="1day", description="Interval of the data to fetch.")


class FMPStockEODData(StockEODData):
    """FMP Stock end of day Data."""

    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    adjClose: Optional[float] = Field(
        description="Adjusted Close Price of the symbol.", alias="adj_close"
    )
    unadjustedVolume: Optional[float] = Field(
        description="Unadjusted volume of the symbol.", alias="unadjusted_volume"
    )
    change: Optional[float] = Field(
        description="Change in the price of the symbol from the previous day.",
        alias="change",
    )
    changePercent: Optional[float] = Field(
        description=r"Change \% in the price of the symbol.", alias="change_percent"
    )
    vwap: Optional[float] = Field(
        description="Volume Weighted Average Price of the symbol."
    )
    label: Optional[str] = Field(description="Human readable format of the date.")
    changeOverTime: Optional[float] = Field(
        description=r"Change \% in the price of the symbol over a period of time.",
        alias="change_over_time",
    )

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(v, "%Y-%m-%d")


class FMPStockEODFetcher(
    Fetcher[
        FMPStockEODQueryParams,
        List[FMPStockEODData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockEODQueryParams:
        now = datetime.now().date()
        transformed_params = params
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(days=7)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPStockEODQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: FMPStockEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPStockEODData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.dict(by_alias=True), ["symbol"])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}/historical-chart/{query.interval}/{query.symbol}?&apikey={api_key}"

        if query.interval == "1day":
            query_str = get_querystring(query.dict(by_alias=True), ["symbol"])
            query_str = query_str.replace("start_date", "from").replace(
                "end_date", "to"
            )
            url = f"{base_url}/historical-price-full/{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, FMPStockEODData, "historical", **kwargs)

    @staticmethod
    def transform_data(data: List[FMPStockEODData]) -> List[FMPStockEODData]:
        return data
