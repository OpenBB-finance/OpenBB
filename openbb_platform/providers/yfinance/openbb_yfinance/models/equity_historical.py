"""Yahoo Finance Equity Historical Price Model."""

# pylint: disable=unused-argument
# ruff: noqa: SIM105

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.helpers import yf_download
from openbb_yfinance.utils.references import INTERVALS_DICT, PERIODS
from pandas import DataFrame, Timestamp
from pydantic import Field, PrivateAttr, field_validator, model_validator


class YFinanceEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Yahoo Finance Equity Historical Price Query.

    Source: https://finance.yahoo.com/
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: Literal[
        "1m",
        "2m",
        "5m",
        "15m",
        "30m",
        "60m",
        "90m",
        "1h",
        "1d",
        "5d",
        "1W",
        "1M",
        "1Q",
    ] = Field(
        default="1d",
        description=QUERY_DESCRIPTIONS.get("interval", ""),
    )
    extended_hours: bool = Field(
        default=False,
        description="Include Pre and Post market data.",
    )
    include_actions: bool = Field(
        default=True,
        description="Include dividends and stock splits in results.",
    )
    adjustment: Literal["splits_only", "splits_and_dividends"] = Field(
        default="splits_only",
        description="The adjustment factor to apply. Default is splits only.",
    )
    adjusted: bool = Field(
        default=False,
        exclude=True,
        description="This field is deprecated (4.1.5) and will be removed in a future version."
        + " Use 'adjustment' set as 'splits_and_dividends' instead.",
        json_schema_extra={"deprecated": True},
    )
    prepost: bool = Field(
        default=False,
        exclude=True,
        description="This field is deprecated (4.1.5) and will be removed in a future version."
        + " Use 'extended_hours' as True instead.",
        json_schema_extra={"deprecated": True},
    )

    _ignore_tz: bool = PrivateAttr(default=True)
    _progress: bool = PrivateAttr(default=False)
    _keepna: bool = PrivateAttr(default=False)
    _period: PERIODS = PrivateAttr(default="max")
    _rounding: bool = PrivateAttr(default=False)
    _repair: bool = PrivateAttr(default=False)
    _group_by: Literal["ticker", "column"] = PrivateAttr(default="ticker")

    @model_validator(mode="before")
    @classmethod
    def validate_deprecated_params(cls, values):
        """Validate the deprecated parameters."""
        for k, v in values.copy().items():
            if k in ["adjusted"] and v is True:
                warn(
                    f"The '{k}' parameter is deprecated and will be removed in a future version."
                )
                values["adjustment"] = "splits_and_dividends"
            if k in ["prepost"] and v is True:
                warn(
                    f"The '{k}' parameter is deprecated and will be removed in a future version."
                )
                values["extended_hours"] = True
        return values


class YFinanceEquityHistoricalData(EquityHistoricalData):
    """Yahoo Finance Equity Historical Price Data."""

    __alias_dict__ = {
        "split_ratio": "stock_splits",
        "dividend": "dividends",
    }

    split_ratio: Optional[float] = Field(
        default=None,
        description="Ratio of the equity split, if a split occurred.",
    )
    dividend: Optional[float] = Field(
        default=None,
        description="Dividend amount (split-adjusted), if a dividend was paid.",
    )

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        if isinstance(v, Timestamp):
            return v.to_pydatetime()
        return v


class YFinanceEquityHistoricalFetcher(
    Fetcher[
        YFinanceEquityHistoricalQueryParams,
        List[YFinanceEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceEquityHistoricalQueryParams:
        """Transform the query."""
        transformed_params = params
        now = datetime.now().date()

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return YFinanceEquityHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> DataFrame:
        """Return the raw data from the Yahoo Finance endpoint."""
        adjusted = query.adjustment == "splits_and_dividends"
        kwargs = {"auto_adjust": True, "back_adjust": True} if adjusted is True else {}
        # pylint: disable=protected-access
        data = yf_download(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            interval=INTERVALS_DICT[query.interval],  # type: ignore
            period=query._period,
            prepost=query.extended_hours,
            actions=query.include_actions,
            progress=query._progress,
            ignore_tz=query._ignore_tz,
            keepna=query._keepna,
            repair=query._repair,
            rounding=query._rounding,
            group_by=query._group_by,
            adjusted=adjusted,
            **kwargs,
        )

        if data.empty:
            raise EmptyDataError()

        return data

    @staticmethod
    def transform_data(
        query: YFinanceEquityHistoricalQueryParams,
        data: DataFrame,
        **kwargs: Any,
    ) -> List[YFinanceEquityHistoricalData]:
        """Transform the data to the standard format."""
        if "capital_gains" in data.columns:
            data = (
                data.drop(columns=["capital_gains"])
                if query.include_actions is False
                else data
            )
        return [
            YFinanceEquityHistoricalData.model_validate(d)
            for d in data.to_dict("records")
        ]
