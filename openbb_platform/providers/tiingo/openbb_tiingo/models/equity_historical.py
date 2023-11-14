"""Tiingo Equity end of day fetcher."""

from datetime import datetime, time
from typing import Any, Dict, List, Literal, Optional
from dateutil.relativedelta import relativedelta
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_provider.utils.helpers import make_request

from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, PrivateAttr, model_validator


class TiingoEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Tiingo Equity end of day Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """

    symbol: str = Field(description="Symbol related to the asset")
    interval: Literal["1d", "1W", "1M", "1Y"] = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )
    _frequency: Literal[
        "daily", "weekly", "monthly", "quarterly", "yearly"
    ] = PrivateAttr(default=None)

    # pylint: disable=protected-access
    @model_validator(mode="after")
    @classmethod
    def set_time_params(cls, values: "TiingoEquityHistoricalQueryParams"):
        """Set the default start & end date and time params for Tiingo API."""
        frequency_dict = {
            "1d": "daily",
            "1W": "weekly",
            "1M": "monthly",
            "1Q": "quarterly",
            "1Y": "yearly",
        }

        values._frequency = frequency_dict[values.interval]

        return values


class TiingoEquityHistoricalData(EquityHistoricalData):
    """Tiingo Equity end of day Data."""

    __alias_dict__ = {
        "adj_open": "adjOpen",
        "adj_high": "adjHigh",
        "adj_low": "adjLow",
        "adj_close": "adjClose",
        "adj_volume": "adjVolume",
        "dividend": "divCash",
        "split_ratio": "splitFactor",
    }

    adj_open: Optional[float] = Field(
        default=None,
        description="Adjusted open price during the period.",
    )
    adj_high: Optional[float] = Field(
        default=None,
        description="Adjusted high price during the period.",
    )
    adj_low: Optional[float] = Field(
        default=None,
        description="Adjusted low price during the period.",
    )
    adj_close: Optional[float] = Field(
        default=None,
        description="Adjusted closing price during the period.",
    )
    adj_volume: Optional[float] = Field(
        default=None,
        description="Adjusted volume during the period.",
    )
    split_ratio: Optional[float] = Field(
        default=None,
        description="Ratio of the equity split, if a equity split occurred.",
    )
    dividend: Optional[float] = Field(
        default=None,
        description="Dividend amount, if a dividend was paid.",
    )


class TiingoEquityHistoricalFetcher(
    Fetcher[
        TiingoEquityHistoricalQueryParams,
        List[TiingoEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Tiingo endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TiingoEquityHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return TiingoEquityHistoricalQueryParams(**transformed_params)

    # pylint: disable=protected-access
    @staticmethod
    def extract_data(
        query: TiingoEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = (
            f"https://api.tiingo.com/tiingo/daily/{query.symbol}/prices"
            f"?startDate={query.start_date}"
            f"&endDate={query.end_date}"
            f"&resampleFreq={query._frequency}"
            f"&token={api_key}"
        )

        data = make_request(base_url).json()

        return data

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: TiingoEquityHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TiingoEquityHistoricalData]:
        """Return the transformed data."""
        return [TiingoEquityHistoricalData.model_validate(d) for d in data]
