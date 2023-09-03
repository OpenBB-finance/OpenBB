"""yfinance Forex End of Day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.forex_historical import (
    ForexHistoricalData,
    ForexHistoricalQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, validator

from openbb_yfinance.utils.helpers import yf_download
from openbb_yfinance.utils.references import INTERVALS, PERIODS


class YFinanceForexHistoricalQueryParams(ForexHistoricalQueryParams):
    """YFinance Forex End of Day Query.

    Source: https://finance.yahoo.com/currencies/
    """

    interval: INTERVALS = Field(default="1d", description="Data granularity.")
    period: PERIODS = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("period", "")
    )


class YFinanceForexHistoricalData(ForexHistoricalData):
    """YFinance Forex End of Day Data."""

    @validator("Date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(v, "%Y-%m-%d").date()


class YFinanceForexHistoricalFetcher(
    Fetcher[
        YFinanceForexHistoricalQueryParams,
        List[YFinanceForexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the yfinance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceForexHistoricalQueryParams:
        """Transform the query."""

        return YFinanceForexHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceForexHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the yfinance endpoint."""
        query.symbol = f"{query.symbol.upper()}=X"

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
    ) -> List[YFinanceForexHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceForexHistoricalData.parse_obj(d) for d in data]
