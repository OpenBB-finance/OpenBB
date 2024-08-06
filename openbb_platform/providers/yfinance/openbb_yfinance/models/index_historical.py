"""Yahoo Finance Index Historical Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.references import INDICES, INTERVALS_DICT
from pydantic import Field


class YFinanceIndexHistoricalQueryParams(IndexHistoricalQueryParams):
    """YFinance Index Historical Query.

    Source: https://finance.yahoo.com/world-indices
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "interval": {
            "choices": [
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
            ]
        },
    }

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


class YFinanceIndexHistoricalData(IndexHistoricalData):
    """YFinance Index Historical Data."""


class YFinanceIndexHistoricalFetcher(
    Fetcher[
        YFinanceIndexHistoricalQueryParams,
        List[YFinanceIndexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceIndexHistoricalQueryParams:
        """Transform the query."""
        # pylint: disable=import-outside-toplevel
        from dateutil.relativedelta import relativedelta
        from pandas import DataFrame

        transformed_params = params
        now = datetime.now().date()

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        tickers = params.get("symbol").lower().split(",")  # type: ignore

        new_tickers = []
        for ticker in tickers:
            _ticker = ""
            indices = DataFrame(INDICES).transpose().reset_index()
            indices.columns = ["code", "name", "symbol"]

            if ticker in indices["code"].values:
                _ticker = indices[indices["code"] == ticker]["symbol"].values[0]

            if ticker.title() in indices["name"].values:
                _ticker = indices[indices["name"] == ticker.title()]["symbol"].values[0]

            if "^" + ticker.upper() in indices["symbol"].values:
                _ticker = "^" + ticker.upper()

            if ticker.upper() in indices["symbol"].values:
                _ticker = ticker.upper()

            if _ticker != "":
                new_tickers.append(_ticker)
            else:
                warn(f"Symbol Error: {ticker} is not a supported index.")

        transformed_params["symbol"] = ",".join(new_tickers)

        return YFinanceIndexHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceIndexHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_yfinance.utils.helpers import yf_download

        data = yf_download(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            interval=INTERVALS_DICT[query.interval],  # type: ignore
            prepost=True,
        )

        if data.empty:
            raise EmptyDataError()

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: YFinanceIndexHistoricalQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> List[YFinanceIndexHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceIndexHistoricalData.model_validate(d) for d in data]
