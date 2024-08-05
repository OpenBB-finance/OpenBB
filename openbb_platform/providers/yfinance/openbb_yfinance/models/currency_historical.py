"""Yahoo Finance Currency Price Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.references import INTERVALS_DICT
from pydantic import Field


class YFinanceCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """Yahoo Finance Currency Price Query.

    Source: https://finance.yahoo.com/currencies/
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


class YFinanceCurrencyHistoricalData(CurrencyHistoricalData):
    """Yahoo Finance Currency Price Data."""


class YFinanceCurrencyHistoricalFetcher(
    Fetcher[
        YFinanceCurrencyHistoricalQueryParams,
        List[YFinanceCurrencyHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> YFinanceCurrencyHistoricalQueryParams:
        """Transform the query."""
        # pylint: disable=import-outside-toplevel
        from dateutil.relativedelta import relativedelta

        transformed_params = params
        symbols = params["symbol"].split(",")
        new_symbols = [
            f"{s.upper()}=X" if "=X" not in s.upper() else s.upper() for s in symbols
        ]
        transformed_params["symbol"] = ",".join(new_symbols)

        now = datetime.now().date()

        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return YFinanceCurrencyHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: YFinanceCurrencyHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_yfinance.utils.helpers import yf_download

        data = yf_download(
            query.symbol,
            start_date=query.start_date,
            end_date=query.end_date,
            interval=INTERVALS_DICT.get(query.interval, "1d"),  # type: ignore
            auto_adjust=False,
            actions=False,
            prepost=True,
        )

        if data.empty:
            raise EmptyDataError()

        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: YFinanceCurrencyHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceCurrencyHistoricalData]:
        """Transform the data to the standard format."""
        return [YFinanceCurrencyHistoricalData.model_validate(d) for d in data]
