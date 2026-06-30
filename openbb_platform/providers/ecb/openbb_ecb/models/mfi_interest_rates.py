"""ECB MFI (bank) Interest Rates Model (MIR dataflow).

MFI interest rate statistics — the rates euro-area banks charge/pay households
and non-financial corporations on loans and deposits. These are economic
indicator series, so the model reuses the standard ``EconomicIndicators``
model; the ``symbol`` parameter is constrained to a curated set of headline
series so callers don't need to know raw MIR dimension keys.
"""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_indicators import (
    EconomicIndicatorsData,
    EconomicIndicatorsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_ecb.utils.series_keys import MIR_SERIES

MFI_SERIES_CHOICES = list(MIR_SERIES)
DEFAULT_MFI_SYMBOL = "household_loans_for_house_purchase"


class ECBMfiInterestRatesQueryParams(EconomicIndicatorsQueryParams):
    """ECB MFI Interest Rates Query."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True, "choices": MFI_SERIES_CHOICES}
    }

    symbol: str = Field(
        default=DEFAULT_MFI_SYMBOL,
        description="The headline MFI interest rate series to fetch. One or more of: "
        + ", ".join(MFI_SERIES_CHOICES),
    )
    country: str | None = Field(
        default="U2",
        description="Reference area: 'U2' (euro area) or an ISO country code"
        " (e.g. 'DE', 'FR') for national data.",
    )
    use_cache: bool = Field(
        default=True,
        description="If true, cache parsed results on disk for the dataset TTL.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v):
        """Validate each comma-separated series name against the curated set."""
        if v is None:
            return DEFAULT_MFI_SYMBOL
        items = v if isinstance(v, list) else str(v).split(",")
        cleaned = [item.strip() for item in items if str(item).strip()]
        if not cleaned:
            return DEFAULT_MFI_SYMBOL
        invalid = [item for item in cleaned if item not in MIR_SERIES]
        if invalid:
            raise ValueError(
                f"Invalid MFI series {invalid}. Choose from: {MFI_SERIES_CHOICES}"
            )
        return ",".join(cleaned)


class ECBMfiInterestRatesData(EconomicIndicatorsData):
    """ECB MFI Interest Rates Data."""

    model_config = ConfigDict(extra="allow")


class ECBMfiInterestRatesFetcher(
    Fetcher[ECBMfiInterestRatesQueryParams, list[ECBMfiInterestRatesData]]
):
    """Fetch curated MFI interest rate series from the ECB MIR dataflow."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBMfiInterestRatesQueryParams:
        """Transform query."""
        return ECBMfiInterestRatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBMfiInterestRatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch each requested MFI rate series."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.query_builder import fetch_sdmx_data
        from openbb_ecb.utils.series_keys import mir_key

        ref_area = (query.country or "U2").upper()
        series_list = [s.strip() for s in str(query.symbol).split(",") if s.strip()]
        start = query.start_date.strftime("%Y-%m-%d") if query.start_date else None
        end = query.end_date.strftime("%Y-%m-%d") if query.end_date else None

        async def get_one(series_name: str) -> list[dict]:
            key = mir_key(series_name, ref_area=ref_area)

            async def loader() -> list[dict]:
                return await fetch_sdmx_data(
                    "MIR", key, start_date=start, end_date=end, raise_empty=False
                )

            cache_key = make_key(
                "mfi_interest_rates",
                series=series_name,
                area=ref_area,
                start=start,
                end=end,
            )
            records = await cached_records(
                "mfi_interest_rates", cache_key, loader, use_cache=query.use_cache
            )
            for record in records:
                record["_series_name"] = series_name
                record["_key"] = key
            return records

        gathered = await asyncio.gather(*[get_one(s) for s in series_list])
        results = [record for batch in gathered for record in batch]
        if not results:
            raise OpenBBError(
                EmptyDataError("No MFI interest rate data found for the query.")
            )
        return results

    @staticmethod
    def transform_data(
        query: ECBMfiInterestRatesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBMfiInterestRatesData]:
        """Standardize into the EconomicIndicators model."""
        rows = []
        for record in data:
            if record.get("OBS_VALUE") is None:
                continue
            rows.append(
                {
                    "date": record["date"],
                    "symbol_root": record.get("_series_name"),
                    "symbol": f"MIR::{record.get('_key', '')}",
                    "country": record.get("REF_AREA__label") or query.country,
                    "value": record.get("OBS_VALUE"),
                    "title": record.get("TITLE") or record.get("BS_ITEM__label"),
                }
            )
        rows.sort(key=lambda r: (r["symbol_root"] or "", r["date"]))
        return [ECBMfiInterestRatesData.model_validate(r) for r in rows]
