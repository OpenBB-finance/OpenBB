"""yfinance Crypto End of Day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.crypto_historical import (
    CryptoHistoricalData,
    CryptoHistoricalQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, validator

from openbb_yfinance.utils.helpers import yf_download
from openbb_yfinance.utils.references import INTERVALS, PERIODS


class YFinanceCryptoHistoricalQueryParams(CryptoHistoricalQueryParams):
    """YFinance Crypto End of Day Query.

    Source: https://finance.yahoo.com/crypto/
    """

    interval: INTERVALS = Field(default="1d", description="Data granularity.")
    period: PERIODS = Field(
        default="max", description=QUERY_DESCRIPTIONS.get("period", "")
    )


class YFinanceCryptoHistoricalData(CryptoHistoricalData):
    """YFinance Crypto End of Day Data."""

    @validator("Date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")


class YFinanceCryptoHistoricalFetcher(
    Fetcher[
        YFinanceCryptoHistoricalQueryParams,
        List[YFinanceCryptoHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the yfinance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceCryptoHistoricalQueryParams:
        """Transform the query."""

        return YFinanceCryptoHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceCryptoHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Return the raw data from the yfinance endpoint."""

        if "-" not in query.symbol:
            position = len(query.symbol) - 3
            query.symbol = query.symbol[:position] + "-" + query.symbol[position:]

        data = yf_download(
            query.symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            interval=query.interval,
            period=query.period,
            prepost=True,
        )
        return data.to_dict("records")

    @staticmethod
    def transform_data(
        data: List[Dict],
    ) -> List[YFinanceCryptoHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceCryptoHistoricalData.parse_obj(d) for d in data]
