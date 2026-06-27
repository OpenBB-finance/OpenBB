"""CME Futures Instruments Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import datetime
from typing import Any

from openbb_cme.utils.helpers import CME_PRODUCT_MAP, fetch_product_calendar
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_instruments import (
    FuturesInstrumentsData,
    FuturesInstrumentsQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator


class CMEFuturesInstrumentsQueryParams(FuturesInstrumentsQueryParams):
    """
    CME Futures Instruments Query — lists available contracts and expiration dates.

    Source: https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/{product_id}/FUT
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "choices": list(CME_PRODUCT_MAP),
        },
    }

    symbol: str = Field(
        default="ES",
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " One or more CME root symbols separated by commas."
        + " Supported: "
        + ", ".join(CME_PRODUCT_MAP),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v: str) -> str:
        """Validate all requested symbols."""
        symbols = [s.strip().upper() for s in v.split(",")]
        unsupported = [s for s in symbols if s not in CME_PRODUCT_MAP]
        if unsupported:
            raise ValueError(
                f"Unsupported symbols: {', '.join(unsupported)}."
                f" Supported: {', '.join(CME_PRODUCT_MAP)}"
            )
        return ",".join(symbols)


class CMEFuturesInstrumentData(FuturesInstrumentsData):
    """CME Futures Instrument — listed contract with expiration details."""

    model_config = ConfigDict(extra="ignore")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    root_symbol: str = Field(description="CME root (product) symbol (e.g. 'ES', 'NQ').")
    name: str = Field(description="Full product name.")
    exchange: str = Field(description="Exchange (e.g. 'CME/Globex').")
    expiration_date: datetime | None = Field(
        default=None, description="Contract expiration date and time (exchange local)."
    )
    description: str | None = Field(
        default=None, description="Human-readable contract description."
    )
    is_active: bool = Field(
        default=True,
        description="Whether this contract is currently listed for trading.",
    )


class CMEFuturesInstrumentsFetcher(
    Fetcher[CMEFuturesInstrumentsQueryParams, list[CMEFuturesInstrumentData]]
):
    """CME Futures Instruments Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CMEFuturesInstrumentsQueryParams:
        """Transform the query."""
        return CMEFuturesInstrumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CMEFuturesInstrumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch listed contracts from CME product calendar."""
        symbols = query.symbol.split(",")

        async def fetch_one(symbol: str) -> list[dict]:
            spec = CME_PRODUCT_MAP[symbol]
            rows = await fetch_product_calendar(spec["product_id"])
            enriched: list[dict] = []
            for row in rows:
                exp_raw = row.get("expiration", "")
                try:
                    exp_dt = datetime.fromisoformat(exp_raw.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    exp_dt = None
                enriched.append(
                    {
                        "symbol": row.get("symbol", ""),
                        "root_symbol": symbol,
                        "name": spec["name"],
                        "exchange": spec["exchange"],
                        "expiration_date": exp_dt,
                        "description": row.get("description"),
                        "is_active": row.get("is_active", True),
                    }
                )
            return enriched

        nested = await asyncio.gather(
            *[fetch_one(s) for s in symbols], return_exceptions=True
        )

        rows: list[dict] = []
        for result in nested:
            if isinstance(result, BaseException):
                # pylint: disable=import-outside-toplevel
                from openbb_core.app.model.abstract.error import OpenBBError

                if isinstance(result, OpenBBError):
                    raise result
                continue
            rows.extend(result)

        if not rows:
            raise EmptyDataError("No instrument data found for the given symbols.")

        return sorted(
            rows, key=lambda x: (x["root_symbol"], x.get("expiration_date") or "")
        )

    @staticmethod
    def transform_data(
        query: CMEFuturesInstrumentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CMEFuturesInstrumentData]:
        """Transform the data."""
        return [CMEFuturesInstrumentData.model_validate(d) for d in data]
