"""Nasdaq Nordic Instrument Info Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_nasdaq.utils.constants import NORDIC_SYMBOL_CHOICES_ENDPOINT

HEADER_FIELDS = {
    "Symbol": "symbol",
    "Name": "companyName",
    "ISIN": "isin",
    "Exchange": "exchange",
    "Segment": "segment",
    "Currency": "currency",
    "Market Status": "marketStatus",
}


class NasdaqNordicInfoQueryParams(QueryParams):
    """Nasdaq Nordic Instrument Info Query.

    Source: https://www.nasdaq.com/european-market-activity
    """

    __json_schema_extra__ = {
        "symbol": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": NORDIC_SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }

    symbol: str = Field(description="The Nasdaq Nordic instrument symbol.")


class NasdaqNordicInfoData(Data):
    """Nasdaq Nordic Instrument Info Data.

    Nasdaq publishes a different metadata set for each asset class - coupons
    and repayment terms for bonds, share counts and ICB codes for equities -
    so the record is served as one row per attribute.
    """

    category: str = Field(description="The section the attribute belongs to.")
    label: str = Field(description="The attribute name as Nasdaq publishes it.")
    value: str | None = Field(default=None, description="The attribute value.")
    as_of: str | None = Field(
        default=None, description="The date the attribute was reported."
    )


class NasdaqNordicInfoFetcher(
    Fetcher[
        NasdaqNordicInfoQueryParams,
        list[NasdaqNordicInfoData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqNordicInfoQueryParams:
        """Transform the query."""
        return NasdaqNordicInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Nasdaq endpoints."""
        import asyncio

        from openbb_nasdaq.utils.factsheet import get_instrument_factsheet
        from openbb_nasdaq.utils.helpers import get_nasdaq_data
        from openbb_nasdaq.utils.nordic import resolve_nordic_instrument

        instrument = await resolve_nordic_instrument(query.symbol)
        base = f"nordic/instruments/{instrument['orderbook_id']}"
        suffix = f"?assetClass={instrument['asset_class']}&lang=en"

        async def get_section(section: str) -> dict:
            """Collect one instrument section, tolerating an absent one."""
            try:
                return await get_nasdaq_data(f"{base}/{section}{suffix}") or {}
            except Exception:  # noqa: BLE001
                return {}

        info, summary, trade_info, price_info = await asyncio.gather(
            get_section("info"),
            get_section("summary"),
            get_section("trade-info"),
            get_section("price-info"),
        )

        return {
            "info": info,
            "summary": summary,
            "trade_info": trade_info,
            "price_info": price_info,
            "profile": (await get_instrument_factsheet(query.symbol))["profile"],
        }

    @staticmethod
    def transform_data(
        query: NasdaqNordicInfoQueryParams, data: dict, **kwargs: Any
    ) -> list[NasdaqNordicInfoData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If Nasdaq publishes no metadata for the instrument.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        results: list[NasdaqNordicInfoData] = []
        header = (data["info"] or {}).get("qdHeader") or {}

        for label, key in HEADER_FIELDS.items():
            value = normalize(header.get(key))

            if value is not None:
                results.append(
                    NasdaqNordicInfoData.model_validate(
                        {"category": "Instrument", "label": label, "value": value}
                    )
                )

        for label, block in (
            ("Quote", header.get("keyStats")),
            ("Summary", (data["summary"] or {}).get("summaryData")),
            ("Trading", (data["trade_info"] or {}).get("summary")),
        ):
            for item in (block or {}).values():
                if not isinstance(item, dict):
                    continue

                value = normalize(item.get("value"))

                if value is None:
                    continue

                results.append(
                    NasdaqNordicInfoData.model_validate(
                        {
                            "category": label,
                            "label": (item.get("label") or "").rstrip(":"),
                            "value": value,
                        }
                    )
                )

        for row in data.get("profile") or []:
            results.append(
                NasdaqNordicInfoData.model_validate(
                    {
                        "category": "Profile",
                        "label": row["label"],
                        "value": row["value"],
                    }
                )
            )

        for row in ((data["price_info"] or {}).get("trades") or {}).get("rows") or []:
            value = normalize(row.get("value"))

            if value is None:
                continue

            results.append(
                NasdaqNordicInfoData.model_validate(
                    {
                        "category": "Price",
                        "label": row.get("attribute"),
                        "value": value,
                        "as_of": normalize(row.get("date")),
                    }
                )
            )

        if not results:
            raise EmptyDataError(f"No instrument detail was found for {query.symbol}.")

        return results


def normalize(value: Any) -> str | None:
    """Trim a Nasdaq Nordic metadata value without altering its formatting.

    Parameters
    ----------
    value : Any
        The raw attribute value.

    Returns
    -------
    str or None
        The trimmed value, or None when the attribute carries no value.
    """
    from openbb_nasdaq.utils.helpers import NA_VALUES

    if value is None:
        return None

    trimmed = str(value).strip()

    return None if trimmed in NA_VALUES else trimmed
