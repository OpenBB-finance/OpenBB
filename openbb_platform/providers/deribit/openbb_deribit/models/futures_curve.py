"""Deribit Futures Curve Model."""

# pylint: disable=unused-argument

from typing import Any, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_deribit.utils.helpers import (
    DERIBIT_FUTURES_CURVE_SYMBOLS,
    FuturesCurveSymbols,
)
from pydantic import Field, field_validator, model_validator


class DeribitFuturesCurveQueryParams(FuturesCurveQueryParams):
    """
    Deribit Futures Curve Query.

    Source: https://docs.deribit.com/?shell#public-ticker
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": False,
            "choices": DERIBIT_FUTURES_CURVE_SYMBOLS,
        },
        "hours_ago": {
            "multiple_items_allowed": True,
        },
    }

    symbol: FuturesCurveSymbols = Field(
        default="BTC",
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " Default is 'btc' Supported symbols are: ['btc', 'eth', 'paxg']",
    )
    hours_ago: Optional[Union[int, list[int], str]] = Field(
        default=None,
        description="Compare the current curve with the specified number of hours ago. Default is None.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def validate_symbol(cls, v):
        """Validate the symbol."""
        symbol = v.upper()
        if symbol not in DERIBIT_FUTURES_CURVE_SYMBOLS:
            raise ValueError(
                f"Invalid Deribit symbol, {symbol}. Supported symbols are: {', '.join(DERIBIT_FUTURES_CURVE_SYMBOLS)}"
            )
        return symbol

    @field_validator("hours_ago", mode="before", check_fields=False)
    @classmethod
    def _validate_hours_ago(cls, v):
        """Validate hours ago."""
        if isinstance(v, str):
            return v
        if isinstance(v, int):
            return v
        if isinstance(v, list):
            return ",".join([str(i) for i in v])
        return None

    @model_validator(mode="before")
    @classmethod
    def _validate_model(cls, values):
        """Validate the model."""
        if values.get("date"):
            raise ValueError(
                "Date field is not supported for Deribit provider. Use 'hours_ago' instead."
            )
        return values


class DeribitFuturesCurveData(FuturesCurveData):
    """Deribit Futures Curve Data."""

    hours_ago: Optional[int] = Field(
        default=None,
        description="The number of hours ago represented by the price."
        + " Only available when hours_ago is set in the query.",
    )


class DeribitFuturesCurveFetcher(
    Fetcher[DeribitFuturesCurveQueryParams, list[DeribitFuturesCurveData]]
):
    """Deribit Futures Curve Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitFuturesCurveQueryParams:
        """Transform query params."""
        return DeribitFuturesCurveQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitFuturesCurveQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list:
        """Extract the raw data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_deribit.utils.helpers import (
            get_futures_curve_symbols,
            get_ticker_data,
            get_futures_curve_by_hours_ago,
        )

        try:
            symbols = await get_futures_curve_symbols(query.symbol)
            tasks = [get_ticker_data(s) for s in symbols]
            data = await asyncio.gather(*tasks, return_exceptions=True)

            if query.hours_ago is not None:
                num_hours = query.hours_ago

                hours_ago = (
                    [int(d) for d in num_hours.split(",")]
                    if isinstance(num_hours, str)
                    else [int(num_hours)] if isinstance(num_hours, int) else num_hours
                )

                for hours in hours_ago:
                    hours_data = await get_futures_curve_by_hours_ago(
                        query.symbol, hours
                    )
                    if hours_data:
                        data.extend(hours_data)
            return data
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(
                f"Failed to get futures curve -> {e.__class__.__name__ if hasattr(e, '__class__') else e}: {e.args}"
            ) from e

    @staticmethod
    def transform_data(
        query: DeribitFuturesCurveQueryParams, data: list, **kwargs: Any
    ) -> list[DeribitFuturesCurveData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from datetime import datetime  # noqa
        from pandas import to_datetime

        if not data:
            raise EmptyDataError("No data found")

        futures_curve: list[DeribitFuturesCurveData] = []

        for d in data:

            if not d:
                continue

            ins_name = d.get("instrument_name", "")
            exp = ins_name.split("-")[1]
            hours_ago = d.get("hours_ago", 0)
            exp = (
                datetime.today().strftime("%Y-%m-%d")
                if exp == "PERPETUAL"
                else to_datetime(exp).strftime("%Y-%m-%d")
            )

            price = d.get("last_price", d.get("mark_price"))

            result = {"expiration": exp, "price": price}
            if query.hours_ago:
                result["hours_ago"] = hours_ago

            if price:
                futures_curve.append(DeribitFuturesCurveData.model_validate(result))

        if not futures_curve:
            raise EmptyDataError("No data found.")

        return sorted(futures_curve, key=lambda x: x.expiration)
