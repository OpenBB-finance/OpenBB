"""OECD Balance of Payments (BOP6) Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_of_payments import (
    BalanceOfPaymentsQueryParams,
    BP6BopUsdData,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_oecd.utils.constants import BOP_COUNTRIES
from pydantic import Field, field_validator

# Map (MEASURE, ACCOUNTING_ENTRY, UNIT_MEASURE) → BP6BopUsdData field name.
_COL_MAP: dict[tuple[str, str, str], str] = {
    ("CA", "B", "PT_B1GQ"): "balance_percent_of_gdp",
    ("CA", "B", "USD_EXC"): "balance_total",
    ("S", "B", "USD_EXC"): "balance_total_services",
    ("IN2", "B", "USD_EXC"): "balance_total_secondary_income",
    ("G", "B", "USD_EXC"): "balance_total_goods",
    ("IN1", "B", "USD_EXC"): "balance_total_primary_income",
    ("S", "C", "PT_GS"): "credits_services_percent_of_goods_and_services",
    ("S", "C", "PT_CA"): "credits_services_percent_of_current_account",
    ("S", "C", "USD_EXC"): "credits_total_services",
    ("G", "C", "USD_EXC"): "credits_total_goods",
    ("IN1", "C", "USD_EXC"): "credits_total_primary_income",
    ("IN2", "C", "USD_EXC"): "credits_total_secondary_income",
    ("CA", "C", "USD_EXC"): "credits_total",
    ("S", "D", "PT_GS"): "debits_services_percent_of_goods_and_services",
    ("S", "D", "PT_CA"): "debits_services_percent_of_current_account",
    ("S", "D", "USD_EXC"): "debits_total_services",
    ("G", "D", "USD_EXC"): "debits_total_goods",
    ("IN1", "D", "USD_EXC"): "debits_total_primary_income",
    ("CA", "D", "USD_EXC"): "debits_total",
    ("IN2", "D", "USD_EXC"): "debits_total_secondary_income",
}

_FREQ_MAP = {"annual": "A", "quarterly": "Q"}
_Q_MAP = {
    1: "Q1",
    2: "Q1",
    3: "Q1",
    4: "Q2",
    5: "Q2",
    6: "Q2",
    7: "Q3",
    8: "Q3",
    9: "Q3",
    10: "Q4",
    11: "Q4",
    12: "Q4",
}


def _format_start_period(d: dateType, freq: str) -> str:
    """Format a date as an SDMX startPeriod for the given frequency."""
    if freq == "A":
        return str(d.year)
    if freq == "Q":
        return f"{d.year}-{_Q_MAP[d.month]}"
    return f"{d.year}-{d.month:02d}"


def _format_end_period(d: dateType, freq: str) -> str:
    """Format a date as an SDMX endPeriod for the given frequency."""
    if freq == "A":
        return str(d.year)
    if freq == "Q":
        return f"{d.year}-{_Q_MAP[d.month]}"
    return f"{d.year}-{d.month:02d}"


class OECDBalanceOfPaymentsQueryParams(BalanceOfPaymentsQueryParams):
    """OECD Balance of Payments Query.

    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(BOP_COUNTRIES) + ["all"],
        },
    }

    country: str = Field(
        default="united_states",
        description=QUERY_DESCRIPTIONS.get("country", ""),
    )
    frequency: Literal["annual", "quarterly"] = Field(
        default="quarterly",
        description="Frequency of the data.",
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
    def validate_country(cls, c: str):
        """Validate country."""
        return c.replace(" ", "_").strip().lower()


class OECDBalanceOfPaymentsData(BP6BopUsdData):
    """OECD Balance of Payments Data."""

    __alias_dict__ = {"period": "date"}


class OECDBalanceOfPaymentsFetcher(
    Fetcher[OECDBalanceOfPaymentsQueryParams, list[OECDBalanceOfPaymentsData]]
):
    """OECD Balance of Payments Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> OECDBalanceOfPaymentsQueryParams:
        """Transform the query."""
        return OECDBalanceOfPaymentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: OECDBalanceOfPaymentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return raw data from the OECD BOP endpoint."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO
        from openbb_core.provider.utils.helpers import make_request
        from openbb_oecd.utils.metadata import OecdMetadata
        from pandas import read_csv, to_numeric
        from pandas.api.types import is_string_dtype

        meta = OecdMetadata()
        countries = meta.resolve_country_codes("DF_BOP", query.country)
        country_str = "+".join(countries) if countries else ""
        freq_code = _FREQ_MAP[query.frequency]

        # Only request the measures/entries/units we actually map.
        measures = sorted({k[0] for k in _COL_MAP})
        entries = sorted({k[1] for k in _COL_MAP})
        units = sorted({k[2] for k in _COL_MAP})

        dim_filter = (
            f"{country_str}"
            "."
            f".{'+'.join(measures)}"
            f".{'+'.join(entries)}"
            "."
            f".{freq_code}"
            f".{'+'.join(units)}"
            ".Y"
        )
        url = f"https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_BOP@DF_BOP,1.0/{dim_filter}"
        params: list[str] = []

        if query.start_date:
            params.append(
                f"startPeriod={_format_start_period(query.start_date, freq_code)}"
            )

        if query.end_date:
            params.append(f"endPeriod={_format_end_period(query.end_date, freq_code)}")

        if params:
            url += "?" + "&".join(params)

        headers = {
            "Accept": "application/vnd.sdmx.data+csv; version=2.0.0; labels=both",
            "User-Agent": "OpenBB/1.0",
        }
        response = make_request(url, headers=headers, timeout=120)

        if response.status_code != 200:
            raise OpenBBError(
                f"OECD BOP request failed ({response.status_code}): {response.reason}"
            )

        text = response.text

        if not text or not text.strip():
            raise OpenBBError(
                EmptyDataError(f"Empty response from OECD BOP. URL: {url}")
            )

        try:
            df = read_csv(StringIO(text))
        except Exception as exc:
            raise OpenBBError(
                f"Failed to parse OECD BOP CSV: {exc}\nURL: {url}"
            ) from exc

        if df.empty:
            raise OpenBBError(EmptyDataError(f"No BOP data rows. URL: {url}"))

        # Strip "CODE: Label" columns to just "CODE".
        rename_map: dict[str, str] = {}

        for col in df.columns:
            if ": " in col:
                rename_map[col] = col.split(":")[0].strip()
            else:
                rename_map[col] = col

        df = df.rename(columns=rename_map)
        skip_cols = {
            "TIME_PERIOD",
            "OBS_VALUE",
            "DATAFLOW",
            "STRUCTURE",
            "STRUCTURE_ID",
            "ACTION",
        }

        for col in [
            c for c in df.columns if c not in skip_cols and is_string_dtype(df[c])
        ]:
            sample = df[col].dropna().head(10)

            if sample.empty:
                continue

            if sample.str.contains(": ", regex=False).any():
                split = df[col].str.split(": ", n=1, expand=True)
                df[col] = split[0].str.strip()

                if split.shape[1] > 1:
                    df[f"{col}_label"] = split[1].str.strip()
                else:
                    df[f"{col}_label"] = df[col]

        if "OBS_VALUE" in df.columns:
            df["OBS_VALUE"] = to_numeric(df["OBS_VALUE"], errors="coerce")

        return df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDBalanceOfPaymentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[OECDBalanceOfPaymentsData]:
        """Pivot long OECD rows into wide BP6 format indexed by date."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        # Group values by (date, country) and map each row to its column.
        groups: dict[tuple, dict[str, Any]] = {}

        for row in data:
            value = row.get("OBS_VALUE")

            if value is None or value == "":
                continue

            d = oecd_date_to_python_date(row.get("TIME_PERIOD", ""))

            if d is None:
                continue

            if query.start_date and d < query.start_date:
                continue

            if query.end_date and d > query.end_date:
                continue

            measure = row.get("MEASURE", "")
            entry = row.get("ACCOUNTING_ENTRY", "")
            unit = row.get("UNIT_MEASURE", "")
            col_name = _COL_MAP.get((measure, entry, unit))

            if col_name is None:
                continue

            key = (d, row.get("REF_AREA_label", row.get("REF_AREA", "")))

            if key not in groups:
                groups[key] = {"date": d, "country": key[1]}

            val = float(value)

            if col_name == "balance_percent_of_gdp" or "percent" in col_name:
                val = val / 100

            groups[key][col_name] = val

        output: list[OECDBalanceOfPaymentsData] = []

        for rec in groups.values():
            output.append(OECDBalanceOfPaymentsData.model_validate(rec))

        return sorted(
            output,
            key=lambda r: (r.period or dateType.min),
        )
