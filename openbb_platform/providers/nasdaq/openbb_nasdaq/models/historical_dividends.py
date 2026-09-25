"""Nasdaq Historical Dividends Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any
from warnings import warn

from dateutil import parser
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT


class NasdaqHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """Nasdaq Historical Dividends Query Params."""

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": False,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }


class NasdaqHistoricalDividendsData(HistoricalDividendsData):
    """Nasdaq Historical Dividends Data."""

    __alias_dict__ = {
        "ex_dividend_date": "exOrEffDate",
        "declaration_date": "declarationDate",
        "record_date": "recordDate",
        "payment_date": "paymentDate",
        "dividend_type": "type",
    }

    dividend_type: str | None = Field(
        default=None,
        description="The type of dividend - i.e., cash, stock.",
    )
    currency: str | None = Field(
        default=None,
        description="The currency in which the dividend is paid.",
    )
    record_date: dateType | None = Field(
        default=None,
        description="The record date of ownership for eligibility.",
    )
    payment_date: dateType | None = Field(
        default=None,
        description="The payment date of the dividend.",
    )
    declaration_date: dateType | None = Field(
        default=None,
        description="Declaration date of the dividend.",
    )

    @field_validator(
        "ex_dividend_date",
        "declaration_date",
        "record_date",
        "payment_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_date(cls, v: str):
        """Validate the date if available is a date object."""
        v = v.replace("N/A", "")
        if not v:
            return None
        return datetime.strptime(v, "%m/%d/%Y").date().strftime("%Y-%m-%d")

    @field_validator("amount", mode="before", check_fields=False)
    @classmethod
    def validate_amount(cls, v: str):
        """Validate the amount if available is a float."""
        v = v.replace("$", "").replace("N/A", "")
        if not v:
            return None
        return float(v)


class NasdaqHistoricalDividendsFetcher(
    Fetcher[NasdaqHistoricalDividendsQueryParams, list[NasdaqHistoricalDividendsData]]
):
    """Nasdaq Historical Dividends Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqHistoricalDividendsQueryParams:
        """Transform the params to the provider-specific query."""
        return NasdaqHistoricalDividendsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqHistoricalDividendsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the raw data."""
        import asyncio

        from openbb_nasdaq.utils.helpers import get_nasdaq_data, resolve_asset_class

        results = []
        symbols = query.symbol.split(",")

        async def get_one(symbol):
            """Collect one symbol's dividend history, trying stocks then ETFs."""
            data: list = []
            asset_class = await resolve_asset_class(symbol)

            try:
                payload = await get_nasdaq_data(
                    f"quote/{symbol}/dividends?assetclass={asset_class}"
                )
            except OpenBBError:
                payload = None

            data = ((payload or {}).get("dividends") or {}).get("rows") or []

            if data:
                if len(symbols) > 1:
                    for d in data:
                        d["symbol"] = symbol
                results.extend(data)
            if not data:
                warn(f"No data found for {symbol}")

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)
        if results:
            return results
        raise EmptyDataError()

    @staticmethod
    def transform_data(
        query: NasdaqHistoricalDividendsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[NasdaqHistoricalDividendsData]:
        """Return the transformed data."""
        results: list[NasdaqHistoricalDividendsData] = []
        for d in data:
            dt = parser.parse(str(d["exOrEffDate"])).date()
            if query.start_date and query.start_date > dt:
                continue
            if query.end_date and query.end_date < dt:
                continue
            results.append(NasdaqHistoricalDividendsData(**d))
        return results
