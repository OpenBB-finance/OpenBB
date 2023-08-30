"""yfinance Major Indices End of Day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.major_indices_eod import (
    MajorIndicesEODData,
    MajorIndicesEODQueryParams,
)
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, validator

from openbb_yfinance.utils.helpers import yf_download
from openbb_yfinance.utils.references import INDICES, INTERVALS, PERIODS


class YFinanceMajorIndicesEODQueryParams(MajorIndicesEODQueryParams):
    """YFinance Major Indices End of Day Query.

    Source: https://finance.yahoo.com/world-indices
    """

    interval: INTERVALS = Field(default="1d", description="Data granularity.")
    period: PERIODS = Field(
        default="max", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    prepost: bool = Field(
        default=False, description="Include Pre and Post market data."
    )
    rounding: bool = Field(
        default=True, description="Round values to two decimal places."
    )


class YFinanceMajorIndicesEODData(MajorIndicesEODData):
    """YFinance Major Indices End of Day Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(v, "%Y-%m-%d").date()


class YFinanceMajorIndicesEODFetcher(
    Fetcher[
        YFinanceMajorIndicesEODQueryParams,
        List[YFinanceMajorIndicesEODData],
    ]
):
    """Transform the query, extract and transform the data from the yfinance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceMajorIndicesEODQueryParams:
        """Transform the query."""
        return YFinanceMajorIndicesEODQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceMajorIndicesEODQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Return the raw data from the yfinance endpoint."""

        symbol = query.symbol
        indices = pd.DataFrame(INDICES).transpose().reset_index()
        indices.columns = ["code", "name", "ticker"]
        indices["symbol"] = indices["ticker"].str.replace("^", "")
        indices["code"] = indices["code"].str.upper()

        symbol = query.symbol
        if query.symbol in indices["symbol"].to_list():
            symbol = indices[indices["symbol"] == query.symbol]["ticker"].iloc[0]
        if query.symbol in indices["code"].to_list():
            symbol = indices[indices["code"] == query.symbol]["ticker"].iloc[0]

        data = yf_download(
            symbol=symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            interval=query.interval,
            period=query.period,
            prepost=query.prepost,
            rounding=query.rounding,
            **kwargs,
        )
        data.date = data.date.astype(str)
        return data.to_dict("records")

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[YFinanceMajorIndicesEODData]:
        """Transform the data to the standard format."""
        return [YFinanceMajorIndicesEODData.parse_obj(d) for d in data]
