"""yfinance Major Indices End of Day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.major_indices_historical import (
    MajorIndicesHistoricalData,
    MajorIndicesHistoricalQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, validator

from openbb_yfinance.utils.helpers import yf_download
from openbb_yfinance.utils.references import INDICES, INTERVALS, PERIODS


class YFinanceMajorIndicesHistoricalQueryParams(MajorIndicesHistoricalQueryParams):
    """YFinance Major Indices End of Day Query.

    Source: https://finance.yahoo.com/world-indices
    """

    interval: INTERVALS = Field(default="1d", description="Data granularity.")
    period: PERIODS = Field(
        default="max", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    prepost: bool = Field(default=True, description="Include Pre and Post market data.")
    rounding: bool = Field(default=True, description="Round prices to two decimals?")


class YFinanceMajorIndicesHistoricalData(MajorIndicesHistoricalData):
    """YFinance Major Indices End of Day Data."""

    @validator("Date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(v, "%Y-%m-%d").date()


class YFinanceMajorIndicesHistoricalFetcher(
    Fetcher[
        YFinanceMajorIndicesHistoricalQueryParams,
        List[YFinanceMajorIndicesHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the yfinance endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> YFinanceMajorIndicesHistoricalQueryParams:
        """Transform the query."""

        return YFinanceMajorIndicesHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceMajorIndicesHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Return the raw data from the yfinance endpoint."""

        symbol = query.symbol.lower()
        indices = pd.DataFrame(INDICES).transpose().reset_index()
        indices.columns = ["code", "name", "symbol"]

        if symbol in indices["code"].to_list():
            symbol = indices[indices["code"] == symbol]["symbol"].values[0]

        if symbol.title() in indices["name"].to_list():
            symbol = indices[indices["name"] == symbol.title()]["symbol"].values[0]

        if "^" + symbol.upper() in indices["symbol"].to_list():
            symbol = "^" + symbol.upper()

        data = yf_download(
            symbol=symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            interval=query.interval,
            period=query.period,
            prepost=query.prepost,
            rounding=query.rounding,
        )
        return data.to_dict("records")

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[YFinanceMajorIndicesHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceMajorIndicesHistoricalData.parse_obj(d) for d in data]
