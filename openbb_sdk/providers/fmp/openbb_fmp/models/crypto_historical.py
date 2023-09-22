"""FMP Cryptos end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, NonNegativeInt


class FMPCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    # noqa: E501
    """FMP Crypto end of day Query.

    Source:
    https://site.financialmodelingprep.com/developer/docs/cryptocurrency-historical-data-api/#Historical-Daily-Prices
    """

    timeseries: Optional[NonNegativeInt] = Field(
        default=None, description="Number of days to look back."
    )
    interval: Literal[
        "1min", "5min", "15min", "30min", "1hour", "4hour", "1day"
    ] = Field(default="1day", description="Data granularity.")


class FMPCryptoHistoricalData(CryptoHistoricalData):
    """FMP Crypto end of day Data."""

    adjClose: Optional[float] = Field(description="Adjusted Close Price of the symbol.")
    unadjustedVolume: Optional[float] = Field(
        description="Unadjusted volume of the symbol."
    )
    change: Optional[float] = Field(
        description="Change in the price of the symbol from the previous day."
    )
    changePercent: Optional[float] = Field(
        description=r"Change % in the price of the symbol."
    )
    vwap: Optional[float] = Field(
        description="Volume Weighted Average Price of the symbol."
    )
    label: Optional[str] = Field(description="Human readable format of the date.")
    changeOverTime: Optional[float] = Field(
        description=r"Change % in the price of the symbol over a period of time."
    )


class FMPCryptoHistoricalFetcher(
    Fetcher[
        FMPCryptoHistoricalQueryParams,
        List[FMPCryptoHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCryptoHistoricalQueryParams:
        """Transform the query params. Start and end dates are set to 1 year interval."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPCryptoHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: FMPCryptoHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = (
            get_querystring(query.dict(), ["symbol"])
            .replace("start_date", "from")
            .replace("end_date", "to")
        )

        url_params = f"{query.symbol}?{query_str}&apikey={api_key}"
        url = f"{base_url}/historical-chart/{query.interval}/{url_params}"

        if query.interval == "1day":
            url = f"{base_url}/historical-price-full/crypto/{url_params}"

        return get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPCryptoHistoricalData]:
        """Return the transformed data."""
        return [FMPCryptoHistoricalData.parse_obj(d) for d in data]
