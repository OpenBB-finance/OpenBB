"""ECB Currency Historical Model."""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


def _exr_pair_choices() -> list[str]:
    """EUR currency pairs available in the EXR dataflow."""
    try:
        from openbb_ecb.utils.metadata import EcbMetadata

        dims = EcbMetadata().get_dataflow_dimensions("EXR")
        currencies = next((d["values"] for d in dims if d["id"] == "CURRENCY"), [])
        return [f"EUR{v['value']}" for v in currencies if v["value"] != "EUR"]
    except Exception:  # noqa: BLE001
        return []


class ECBCurrencyHistoricalQueryParams(CurrencyHistoricalQueryParams):
    """ECB Currency Historical Query."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True, "choices": _exr_pair_choices()}
    }

    frequency: Literal["daily", "monthly", "quarterly", "annual"] = Field(
        default="daily",
        description="The frequency of the reference exchange rates.",
    )
    use_cache: bool = Field(
        default=True,
        description="If true, cache parsed results on disk for the dataset TTL.",
    )


class ECBCurrencyHistoricalData(CurrencyHistoricalData):
    """ECB Currency Historical Data."""


class ECBCurrencyHistoricalFetcher(
    Fetcher[ECBCurrencyHistoricalQueryParams, list[ECBCurrencyHistoricalData]]
):
    """Fetch euro reference exchange rates from the ECB."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBCurrencyHistoricalQueryParams:
        """Transform query."""
        return ECBCurrencyHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBCurrencyHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the raw euro reference-rate series for each required currency."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.query_builder import fetch_sdmx_data
        from openbb_ecb.utils.series_keys import FREQUENCY_MAP, exr_key

        freq = FREQUENCY_MAP[query.frequency]
        start = query.start_date.strftime("%Y-%m-%d") if query.start_date else None
        end = query.end_date.strftime("%Y-%m-%d") if query.end_date else None

        currencies: set[str] = set()
        for pair in str(query.symbol).split(","):
            if pair.strip():
                base, quote = ECBCurrencyHistoricalFetcher._split_pair(
                    pair.strip().upper()
                )
                currencies.update({base, quote} - {"EUR"})

        async def get_currency(currency: str) -> list[dict]:
            async def loader() -> list[dict]:
                return await fetch_sdmx_data(
                    "EXR",
                    exr_key(currency, freq),
                    start_date=start,
                    end_date=end,
                    raise_empty=False,
                )

            cache_key = make_key(
                "exr", currency=currency, freq=freq, start=start, end=end
            )
            records = await cached_records(
                "exr", cache_key, loader, use_cache=query.use_cache
            )
            for record in records:
                record["_currency"] = currency
            return records

        batches = await asyncio.gather(*[get_currency(c) for c in sorted(currencies)])
        return [record for batch in batches for record in batch]

    @staticmethod
    def _split_pair(pair: str) -> tuple[str, str]:
        """Split a pair into base and quote."""
        if len(pair) == 3:
            return "EUR", pair
        if len(pair) != 6:
            raise OpenBBError(
                f"Invalid currency pair '{pair}'. Use CUR1CUR2 (e.g. 'EURUSD')."
            )
        return pair[:3], pair[3:]

    @staticmethod
    def transform_data(
        query: ECBCurrencyHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBCurrencyHistoricalData]:
        """Compute rates per requested pair and standardize."""
        rates: dict[str, dict[str, float]] = {}
        for record in data:
            if record.get("OBS_VALUE") is None:
                continue
            rates.setdefault(record["_currency"], {})[record["date"]] = record[
                "OBS_VALUE"
            ]

        results: list[dict] = []
        for raw_pair in str(query.symbol).split(","):
            pair = raw_pair.strip().upper()
            if not pair:
                continue
            base, quote = ECBCurrencyHistoricalFetcher._split_pair(pair)
            base_rates = rates.get(base, {})
            quote_rates = rates.get(quote, {})
            dates = (
                set(base_rates) | set(quote_rates)
                if base != "EUR" and quote != "EUR"
                else set(base_rates or quote_rates)
            )
            for date in dates:
                base_val = 1.0 if base == "EUR" else base_rates.get(date)
                quote_val = 1.0 if quote == "EUR" else quote_rates.get(date)
                if not base_val or not quote_val:
                    continue
                results.append(
                    {"date": date, "symbol": pair, "close": quote_val / base_val}
                )

        if not results:
            raise OpenBBError(
                EmptyDataError("No exchange rate data found for the requested pair(s).")
            )
        results.sort(key=lambda r: (r["symbol"], r["date"]))
        return [ECBCurrencyHistoricalData.model_validate(d) for d in results]
