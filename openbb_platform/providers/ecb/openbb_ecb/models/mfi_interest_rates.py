"""ECB MFI Interest Rates Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_indicators import (
    EconomicIndicatorsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_ecb.utils.series_keys import MIR_SERIES

_MFI_LABELS: dict[str, str] = {
    "household_overnight_deposits": "Households – overnight deposits",
    "household_deposits_with_agreed_maturity": (
        "Households – deposits with agreed maturity"
    ),
    "household_deposits_redeemable_at_notice": (
        "Households – deposits redeemable at notice"
    ),
    "household_loans_for_house_purchase": "Households – loans for house purchase",
    "household_loans_for_house_purchase_cost_of_borrowing": (
        "Households – house purchase (cost of borrowing)"
    ),
    "household_consumer_credit": "Households – consumer credit",
    "household_other_loans": "Households – other loans",
    "corporate_overnight_deposits": "NFCs – overnight deposits",
    "corporate_deposits_with_agreed_maturity": ("NFCs – deposits with agreed maturity"),
    "corporate_loans": "NFCs – loans",
    "corporate_loans_cost_of_borrowing": "NFCs – loans (cost of borrowing)",
    "household_loans_outstanding": "Households – loans outstanding",
    "household_house_purchase_outstanding": "Households – house purchase outstanding",
    "household_consumer_and_other_outstanding": (
        "Households – consumer & other outstanding"
    ),
}
MFI_SERIES_CHOICES = list(_MFI_LABELS)
DEFAULT_MFI_SYMBOL = ",".join(MFI_SERIES_CHOICES)
_MIR_AREAS = [
    "U2",
    "AT",
    "BE",
    "BG",
    "CY",
    "CZ",
    "DE",
    "DK",
    "EE",
    "ES",
    "FI",
    "FR",
    "GR",
    "HR",
    "HU",
    "IE",
    "IT",
    "LT",
    "LU",
    "LV",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SE",
    "SI",
    "SK",
]


def _rate(label: str):
    """Build a percent-valued rate column."""
    return Field(
        default=None,
        description=f"{label}, in percent.",
        json_schema_extra={
            "x-widget_config": {"headerName": label},
            "x-unit_measurement": "percent",
        },
    )


class ECBMfiInterestRatesQueryParams(EconomicIndicatorsQueryParams):
    """ECB MFI Interest Rates Query."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True, "choices": MFI_SERIES_CHOICES},
        "country": {"choices": _MIR_AREAS},
    }

    symbol: str = Field(
        default=DEFAULT_MFI_SYMBOL,
        description="Headline MFI rate series to include as columns (default: all)."
        " One or more of: " + ", ".join(MFI_SERIES_CHOICES),
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


class ECBMfiInterestRatesData(Data):
    """ECB MFI Interest Rates Data."""

    date: dateType = Field(description="Observation date.")
    household_overnight_deposits: float | None = _rate(
        _MFI_LABELS["household_overnight_deposits"]
    )
    household_deposits_with_agreed_maturity: float | None = _rate(
        _MFI_LABELS["household_deposits_with_agreed_maturity"]
    )
    household_deposits_redeemable_at_notice: float | None = _rate(
        _MFI_LABELS["household_deposits_redeemable_at_notice"]
    )
    household_loans_for_house_purchase: float | None = _rate(
        _MFI_LABELS["household_loans_for_house_purchase"]
    )
    household_loans_for_house_purchase_cost_of_borrowing: float | None = _rate(
        _MFI_LABELS["household_loans_for_house_purchase_cost_of_borrowing"]
    )
    household_consumer_credit: float | None = _rate(
        _MFI_LABELS["household_consumer_credit"]
    )
    household_other_loans: float | None = _rate(_MFI_LABELS["household_other_loans"])
    corporate_overnight_deposits: float | None = _rate(
        _MFI_LABELS["corporate_overnight_deposits"]
    )
    corporate_deposits_with_agreed_maturity: float | None = _rate(
        _MFI_LABELS["corporate_deposits_with_agreed_maturity"]
    )
    corporate_loans: float | None = _rate(_MFI_LABELS["corporate_loans"])
    corporate_loans_cost_of_borrowing: float | None = _rate(
        _MFI_LABELS["corporate_loans_cost_of_borrowing"]
    )
    household_loans_outstanding: float | None = _rate(
        _MFI_LABELS["household_loans_outstanding"]
    )
    household_house_purchase_outstanding: float | None = _rate(
        _MFI_LABELS["household_house_purchase_outstanding"]
    )
    household_consumer_and_other_outstanding: float | None = _rate(
        _MFI_LABELS["household_consumer_and_other_outstanding"]
    )


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
        """Pivot the per-series records into one wide row per date."""
        by_date: dict[str, dict] = {}
        for record in data:
            value = record.get("OBS_VALUE")
            series = record.get("_series_name")
            if value is None or series not in _MFI_LABELS:
                continue
            row = by_date.setdefault(record["date"], {"date": record["date"]})
            row[series] = float(value)

        if not by_date:
            raise EmptyDataError("No MFI interest rate data found for the query.")
        rows = sorted(by_date.values(), key=lambda r: r["date"])
        return [ECBMfiInterestRatesData.model_validate(r) for r in rows]
