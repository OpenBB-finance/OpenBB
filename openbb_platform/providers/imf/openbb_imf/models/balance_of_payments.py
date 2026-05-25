"""IMF Balance of Payments Model."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_of_payments import (
    BalanceOfPaymentsQueryParams,
    BP6BopUsdData,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_imf.utils.metadata import ImfMetadata

api_prefix = SystemService().system_settings.api_settings.prefix

_BOP_TABLE_SYMBOL = "BOP::H_BOP_BOP_AGG_STANDARD_PRESENTATION"

_CANONICAL_ORDER: tuple[str, ...] = (
    "period",
    "country",
    "balance_total",
    "balance_total_goods",
    "balance_total_services",
    "balance_total_primary_income",
    "balance_total_secondary_income",
    "balance_percent_of_gdp",
    "credits_total",
    "credits_total_goods",
    "credits_total_services",
    "credits_total_primary_income",
    "credits_total_secondary_income",
    "credits_services_percent_of_goods_and_services",
    "credits_services_percent_of_current_account",
    "debits_total",
    "debits_total_goods",
    "debits_total_services",
    "debits_total_primary_income",
    "debits_total_secondary_income",
    "debits_services_percent_of_goods_and_services",
    "debits_services_percent_of_current_account",
)


def _load_bop_countries() -> tuple[dict[str, str], set[str]]:
    """Return ``(label_to_code, code_set)`` from the BOP dataflow."""
    metadata = ImfMetadata()
    params = metadata.get_dataflow_parameters("BOP")
    countries = params.get("COUNTRY", [])
    label_to_code: dict[str, str] = {}
    code_set: set[str] = set()
    for entry in sorted(countries, key=lambda p: p.get("label", "")):
        code = entry.get("value")
        label = entry.get("label", code or "")
        if not code:
            continue
        code_set.add(code.upper())
        label_to_code[label.lower().replace(" ", "_")] = code.upper()
    return label_to_code, code_set


BOP_LABEL_TO_CODE, BOP_CODE_SET = _load_bop_countries()

_BALANCE_FIELD: dict[str, str] = {
    "CAB": "balance_total",
    "G": "balance_total_goods",
    "S": "balance_total_services",
    "IN1": "balance_total_primary_income",
    "IN2": "balance_total_secondary_income",
}

_CREDIT_FIELD: dict[str, str] = {
    "G": "credits_total_goods",
    "S": "credits_total_services",
    "IN1": "credits_total_primary_income",
    "IN2": "credits_total_secondary_income",
}

_DEBIT_FIELD: dict[str, str] = {
    "G": "debits_total_goods",
    "S": "debits_total_services",
    "IN1": "debits_total_primary_income",
    "IN2": "debits_total_secondary_income",
}

_FREQ_CODE: dict[str, str] = {"annual": "A", "quarterly": "Q", "monthly": "M"}


class ImfBalanceOfPaymentsQueryParams(BalanceOfPaymentsQueryParams):
    """IMF Balance of Payments Query Parameters."""

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/imf/list_bop_country_choices",
                "value": ["USA"],
                "style": {"popupWidth": 400},
            },
        },
    }

    country: str = Field(
        default="USA",
        description=QUERY_DESCRIPTIONS.get("country", ""),
        validate_default=True,
    )
    frequency: Literal["annual", "quarterly"] = Field(
        default="quarterly",
        description="Reporting frequency.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c: str) -> str:
        """Resolve country name or ISO3 token(s) against the BOP dataflow's countries."""
        out: list[str] = []
        for token in c.replace(" ", "_").split(","):
            upper = token.upper()
            lower = token.lower()
            if upper in BOP_CODE_SET:
                out.append(upper)
            elif lower in BOP_LABEL_TO_CODE:
                out.append(BOP_LABEL_TO_CODE[lower])
            else:
                raise ValueError(
                    f"Country '{token}' is not in the IMF BOP dataflow's country list "
                    f"(value must be one of {len(BOP_CODE_SET)} ISO3 codes "
                    "or matching country labels)."
                )
        return "+".join(out)


class ImfBalanceOfPaymentsData(BP6BopUsdData):
    """IMF Balance of Payments Data."""

    __alias_dict__ = {"period": "date"}

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Balance of Payments",
                "$.description": (
                    "BPM6 Balance of Payments aggregated standard presentation."
                ),
                "$.gridData": {"w": 40, "h": 14},
                "$.refetchInterval": False,
                "$.category": "Economy",
                "$.subCategory": "Balance of Payments",
            }
        },
    )

    country: str | None = Field(
        default=None,
        description="ISO3 country code (or label) reported alongside each row.",
    )
    balance_total: float | None = Field(
        default=None, description="Current Account Total Balance (USD)"
    )
    balance_total_goods: float | None = Field(
        default=None, description="Current Account Total Goods Balance (USD)"
    )
    balance_total_services: float | None = Field(
        default=None, description="Current Account Total Services Balance (USD)"
    )
    balance_total_primary_income: float | None = Field(
        default=None,
        description="Current Account Total Primary Income Balance (USD)",
    )
    balance_total_secondary_income: float | None = Field(
        default=None,
        description="Current Account Total Secondary Income Balance (USD)",
    )
    balance_percent_of_gdp: float | None = Field(
        default=None,
        description="Current Account Balance as Percent of GDP (not provided by IMF BOP).",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    credits_total: float | None = Field(
        default=None, description="Current Account Credits Total (USD)"
    )
    credits_total_goods: float | None = Field(
        default=None, description="Current Account Credits Total Goods (USD)"
    )
    credits_total_services: float | None = Field(
        default=None, description="Current Account Credits Total Services (USD)"
    )
    credits_total_primary_income: float | None = Field(
        default=None, description="Current Account Credits Total Primary Income (USD)"
    )
    credits_total_secondary_income: float | None = Field(
        default=None,
        description="Current Account Credits Total Secondary Income (USD)",
    )
    credits_services_percent_of_goods_and_services: float | None = Field(
        default=None,
        description="Current Account Credits Services as Percent of Goods and Services",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    credits_services_percent_of_current_account: float | None = Field(
        default=None,
        description="Current Account Credits Services as Percent of Current Account",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    debits_total: float | None = Field(
        default=None, description="Current Account Debits Total (USD)"
    )
    debits_total_goods: float | None = Field(
        default=None, description="Current Account Debits Total Goods (USD)"
    )
    debits_total_services: float | None = Field(
        default=None, description="Current Account Debits Total Services (USD)"
    )
    debits_total_primary_income: float | None = Field(
        default=None, description="Current Account Debits Total Primary Income (USD)"
    )
    debits_total_secondary_income: float | None = Field(
        default=None,
        description="Current Account Debits Total Secondary Income (USD)",
    )
    debits_services_percent_of_goods_and_services: float | None = Field(
        default=None,
        description="Current Account Debits Services as Percent of Goods and Services",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    debits_services_percent_of_current_account: float | None = Field(
        default=None,
        description="Current Account Debits Services as Percent of Current Account",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Dump fields in BPM6 reading order regardless of inherited declarations."""
        raw = super().model_dump(**kwargs)
        ordered: dict[str, Any] = {}
        for key in _CANONICAL_ORDER:
            if key in raw:
                ordered[key] = raw.pop(key)
        ordered.update(raw)
        return ordered


class ImfBalanceOfPaymentsFetcher(
    Fetcher[ImfBalanceOfPaymentsQueryParams, list[ImfBalanceOfPaymentsData]]
):
    """IMF Balance of Payments Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfBalanceOfPaymentsQueryParams:
        """Validate query params."""
        return ImfBalanceOfPaymentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: ImfBalanceOfPaymentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Fetch the IMF BOP rows."""
        from openbb_imf.utils.query_builder import ImfQueryBuilder

        freq = _FREQ_CODE[query.frequency]
        start_date = query.start_date.strftime("%Y-%m-%d") if query.start_date else None
        end_date = query.end_date.strftime("%Y-%m-%d") if query.end_date else None

        try:
            result = ImfQueryBuilder().fetch_data(
                "BOP",
                start_date=start_date,
                end_date=end_date,
                COUNTRY=query.country,
                BOP_ACCOUNTING_ENTRY="NETCD_T+CD_T+DB_T",
                INDICATOR="CAB+G+S+IN1+IN2",
                UNIT="USD",
                FREQUENCY=freq,
                _skip_validation=True,
            )
        except (ValueError, OpenBBError) as e:
            raise OpenBBError(e) from e

        rows = result.get("data", []) if isinstance(result, dict) else []
        if not rows:
            raise OpenBBError(EmptyDataError("No BOP data for the selected query."))
        return rows

    @staticmethod
    def transform_data(
        query: ImfBalanceOfPaymentsQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[ImfBalanceOfPaymentsData]:
        """Pivot long SDMX rows into wide BP6 records keyed by date+country."""
        groups: dict[tuple[str, str], dict[str, Any]] = {}
        for row in data:
            indicator = str(row.get("INDICATOR_code") or row.get("INDICATOR") or "")
            entry = row.get("BOP_ACCOUNTING_ENTRY_code") or row.get(
                "BOP_ACCOUNTING_ENTRY"
            )
            if entry == "NETCD_T":
                field = _BALANCE_FIELD.get(indicator)
            elif entry == "CD_T":
                field = _CREDIT_FIELD.get(indicator)
            elif entry == "DB_T":
                field = _DEBIT_FIELD.get(indicator)
            else:
                field = None
            if field is None:
                continue
            period = row.get("TIME_PERIOD")
            if not period:
                continue
            country = (
                row.get("COUNTRY_label")
                or row.get("COUNTRY_code")
                or row.get("COUNTRY")
                or ""
            )
            value = row.get("OBS_VALUE")
            if value in (None, ""):
                continue
            try:
                fval = float(value)
            except (TypeError, ValueError):
                continue
            bucket = groups.setdefault(
                (period, country),
                {"period": period, "country": country},
            )
            bucket[field] = fval

        for bucket in groups.values():
            credits_components = [
                bucket.get(c)
                for c in (
                    "credits_total_goods",
                    "credits_total_services",
                    "credits_total_primary_income",
                    "credits_total_secondary_income",
                )
            ]
            debits_components = [
                bucket.get(c)
                for c in (
                    "debits_total_goods",
                    "debits_total_services",
                    "debits_total_primary_income",
                    "debits_total_secondary_income",
                )
            ]
            if all(v is not None for v in credits_components):
                bucket["credits_total"] = sum(credits_components)
            if all(v is not None for v in debits_components):
                bucket["debits_total"] = sum(debits_components)

            services_credits = bucket.get("credits_total_services")
            services_debits = bucket.get("debits_total_services")
            goods_credits = bucket.get("credits_total_goods")
            goods_debits = bucket.get("debits_total_goods")
            credits_total = bucket.get("credits_total")
            debits_total = bucket.get("debits_total")

            if (
                services_credits is not None
                and goods_credits is not None
                and (services_credits + goods_credits)
            ):
                bucket["credits_services_percent_of_goods_and_services"] = (
                    services_credits / (services_credits + goods_credits)
                )
            if services_credits is not None and credits_total:
                bucket["credits_services_percent_of_current_account"] = (
                    services_credits / credits_total
                )
            if (
                services_debits is not None
                and goods_debits is not None
                and (services_debits + goods_debits)
            ):
                bucket["debits_services_percent_of_goods_and_services"] = (
                    services_debits / (services_debits + goods_debits)
                )
            if services_debits is not None and debits_total:
                bucket["debits_services_percent_of_current_account"] = (
                    services_debits / debits_total
                )

        return sorted(
            [ImfBalanceOfPaymentsData.model_validate(rec) for rec in groups.values()],
            key=lambda r: (r.period or dateType.min, r.country or ""),
        )
