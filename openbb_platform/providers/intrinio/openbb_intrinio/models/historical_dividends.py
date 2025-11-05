"""Intrinio Historical Dividends Model."""

# pylint: disable=unused-argument
from datetime import datetime
from typing import Any

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import get_data_many
from pydantic import Field


class IntrinioHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """Intrinio Historical Dividends Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_security_stock_price_adjustments_v2
    """

    __alias_dict__ = {"limit": "page_size"}

    limit: int | None = Field(
        default=100,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )


class IntrinioHistoricalDividendsData(HistoricalDividendsData):
    """Intrinio Historical Dividends Data."""

    __alias_dict__ = {
        "ex_dividend_date": "date",
        "amount": "dividend",
        "currency": "dividend_currency",
    }

    factor: float | None = Field(
        default=None,
        description=(
            "factor by which to multiply stock prices before this date, "
            "in order to calculate historically-adjusted stock prices."
        ),
    )
    currency: str | None = Field(
        default=None,
        description="The currency in which the dividend is paid.",
    )
    split_ratio: float | None = Field(
        default=None,
        description="The ratio of the stock split, if a stock split occurred.",
    )


class IntrinioHistoricalDividendsFetcher(
    Fetcher[
        IntrinioHistoricalDividendsQueryParams,
        list[IntrinioHistoricalDividendsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> IntrinioHistoricalDividendsQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(year=1)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioHistoricalDividendsQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioHistoricalDividendsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com/securities"
        query_str = get_querystring(query.model_dump(), ["symbol"])
        url = f"{base_url}/{query.symbol}/prices/adjustments?{query_str}&api_key={api_key}"

        return await get_data_many(url, "stock_price_adjustments", **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioHistoricalDividendsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[IntrinioHistoricalDividendsData]:
        """Return the transformed data."""
        transformed_data: list[dict] = [
            {"symbol": query.symbol, **item} for item in data
        ]
        return [
            IntrinioHistoricalDividendsData.model_validate(d) for d in transformed_data
        ]
