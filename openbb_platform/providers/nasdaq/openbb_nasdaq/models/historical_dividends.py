"""Nasdaq Historical Dividends Model."""

# pylint: disable=unused-argument
import asyncio
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional
from warnings import warn

from dateutil import parser
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_nasdaq.utils.helpers import IPO_HEADERS
from pydantic import Field, field_validator


class NasdaqHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """Nasdaq Historical Dividends Query Params."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class NasdaqHistoricalDividendsData(HistoricalDividendsData):
    """Nasdaq Historical Dividends Data."""

    __alias_dict__ = {
        "ex_dividend_date": "exOrEffDate",
        "declaration_date": "declarationDate",
        "record_date": "recordDate",
        "payment_date": "paymentDate",
        "dividend_type": "type",
    }

    dividend_type: Optional[str] = Field(
        default=None,
        description="The type of dividend - i.e., cash, stock.",
    )
    currency: Optional[str] = Field(
        default=None,
        description="The currency in which the dividend is paid.",
    )
    record_date: Optional[dateType] = Field(
        default=None,
        description="The record date of ownership for eligibility.",
    )
    payment_date: Optional[dateType] = Field(
        default=None,
        description="The payment date of the dividend.",
    )
    declaration_date: Optional[dateType] = Field(
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
    Fetcher[NasdaqHistoricalDividendsQueryParams, List[NasdaqHistoricalDividendsData]]
):
    """Nasdaq Historical Dividends Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqHistoricalDividendsQueryParams:
        """Transform the params to the provider-specific query."""
        return NasdaqHistoricalDividendsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqHistoricalDividendsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data."""
        results = []
        symbols = query.symbol.split(",")

        async def get_one(symbol):
            """Response Callback."""
            data = []
            asset_class = "stocks"
            url = f"https://api.nasdaq.com/api/quote/{symbol}/dividends?assetclass={asset_class}"

            response = await amake_request(
                url,
                headers=IPO_HEADERS,
            )
            if response.get("status").get("rCode") == 400:  # type: ignore
                response = await amake_request(
                    url.replace("stocks", "etf"),
                    headers=IPO_HEADERS,
                )
            if response.get("status").get("rCode") == 200:  # type: ignore
                data = response.get("data").get("dividends").get("rows")  # type: ignore

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
        data: List[Dict],
        **kwargs: Any,
    ) -> List[NasdaqHistoricalDividendsData]:
        """Return the transformed data."""
        results: List[NasdaqHistoricalDividendsData] = []
        for d in data:
            dt = parser.parse(str(d["exOrEffDate"])).date()
            if query.start_date and query.start_date > dt:
                continue
            if query.end_date and query.end_date < dt:
                continue
            results.append(NasdaqHistoricalDividendsData(**d))
        return results
