"""FMP Cryptos end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, NonNegativeInt, field_validator


class FMPCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    # noqa: E501
    """FMP Crypto end of day Query.

    Source:
    https://site.financialmodelingprep.com/developer/docs/cryptocurrency-historical-data-api/#Historical-Daily-Prices
    """

    timeseries: Optional[NonNegativeInt] = Field(
        default=None, description="Number of days to look back."
    )


class FMPCryptoHistoricalData(CryptoHistoricalData):
    """FMP Crypto end of day Data."""

    adj_close: Optional[float] = Field(
        default=None, description="Adjusted Close Price of the symbol."
    )
    unadjusted_volume: Optional[float] = Field(
        default=None, description="Unadjusted volume of the symbol."
    )
    change: Optional[float] = Field(
        default=None,
        description="Change in the price of the symbol from the previous day.",
    )
    change_percent: Optional[float] = Field(
        default=None, description="Change % in the price of the symbol."
    )

    label: Optional[str] = Field(
        default=None, description="Human readable format of the date."
    )
    change_over_time: Optional[float] = Field(
        default=None,
        description="Change % in the price of the symbol over a period of time.",
    )

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


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

        base_url = "https://financialmodelingprep.com/api/v3/"
        query_str = get_querystring(query.model_dump(), ["symbol"])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}historical-price-full/crypto/{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPCryptoHistoricalData]:
        """Return the transformed data."""
        return [FMPCryptoHistoricalData.model_validate(d) for d in data]
