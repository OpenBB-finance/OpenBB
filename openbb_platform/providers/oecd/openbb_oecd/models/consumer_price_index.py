"""OECD CPI Data."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.consumer_price_index import (
    ConsumerPriceIndexData,
    ConsumerPriceIndexQueryParams,
)
from openbb_oecd.utils.constants import CPI_COUNTRIES
from pydantic import Field, field_validator

# Domain-specific expenditure mappings (COICOP codes → human labels).
# These are NOT country dicts — they are indicator-level constants specific to the
# CPI dataflow and are kept here intentionally.
expenditure_dict_rev = {
    # --- Main COICOP categories (CP01-CP12) ---
    "_T": "total",
    "CP01": "food_non_alcoholic_beverages",
    "CP02": "alcoholic_beverages_tobacco_narcotics",
    "CP03": "clothing_footwear",
    "CP04": "housing_water_electricity_gas",
    "CP041": "actual_rentals",
    "CP042": "imputed_rentals",
    "CP043": "maintenance_repair_dwelling",
    "CP044": "water_supply_other_services",
    "CP045": "electricity_gas_other_fuels",
    "CP05": "furniture_household_equipment",
    "CP06": "health",
    "CP07": "transport",
    "CP0722": "fuels_lubricants_personal",
    "CP08": "communication",
    "CP09": "recreation_culture",
    "CP10": "education",
    "CP11": "restaurants_hotels",
    "CP12": "miscellaneous_goods_services",
    # --- Aggregate / special categories ---
    "CP045_0722": "energy",
    "GD": "goods",
    "CP041T043": "housing",
    "CP041T043X042": "housing_excluding_rentals",
    "_TXCP01_NRG": "all_non_food_non_energy",
    "SERVXCP041_042_0432": "services_less_housing",
    "SERVXCP041_0432": "services_less_house_excl_rentals",
    "SERV": "services",
    "_TXNRG_01_02": "overall_excl_energy_food_alcohol_tobacco",
    "CPRES": "residuals",
}
expenditure_dict = {v: k for k, v in expenditure_dict_rev.items()}

expenditure_choices = sorted(expenditure_dict.keys()) + ["all"]
transform_choices = ["index", "yoy", "period"]

# CPI transformation codes: user-facing name → TRANSFORMATION dimension value.
_TRANSFORM_MAP = {
    "index": "_Z",  # Index — no transformation
    "yoy": "GY",  # Growth rate, over 1 year
    "period": "G1",  # Growth rate, period on period
}

# Frequency codes.
_FREQ_MAP = {"annual": "A", "quarter": "Q", "monthly": "M"}

# User-friendly unit labels keyed by transform name.
_UNIT_LABELS = {
    "index": "Index",
    "yoy": "Year-over-year (YOY) percent change",
    "period": "Period-over-period percent change",
}

# Sort order for expenditure categories (COICOP codes).
_EXPENDITURE_ORDER: dict[str, int] = {
    # Main COICOP categories
    "_T": 0,
    "CP01": 1,
    "CP02": 2,
    "CP03": 3,
    "CP04": 4,
    "CP041": 5,
    "CP042": 6,
    "CP043": 7,
    "CP044": 8,
    "CP045": 9,
    "CP05": 10,
    "CP06": 11,
    "CP07": 12,
    "CP0722": 13,
    "CP08": 14,
    "CP09": 15,
    "CP10": 16,
    "CP11": 17,
    "CP12": 18,
    # Aggregate / special categories
    "CP045_0722": 19,
    "GD": 20,
    "CP041T043": 21,
    "CP041T043X042": 22,
    "_TXCP01_NRG": 23,
    "SERVXCP041_042_0432": 24,
    "SERVXCP041_0432": 25,
    "SERV": 26,
    "_TXNRG_01_02": 27,
    "CPRES": 28,
}


class OECDCPIQueryParams(ConsumerPriceIndexQueryParams):
    """OECD CPI Query.

    Notes
    -----
    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(CPI_COUNTRIES) + ["all"],
        },
        "frequency": {
            "choices": ["annual", "quarter", "monthly"],
        },
        "transform": {
            "choices": transform_choices,
        },
        "expenditure": {
            "choices": expenditure_choices,
        },
    }

    expenditure: str = Field(
        description="Expenditure component of CPI.",
        default="total",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c: str):
        """Validate country."""
        return c.replace(" ", "_").strip().lower()

    @field_validator("expenditure", mode="before", check_fields=False)
    @classmethod
    def validate_expenditure(cls, v):
        """Validate expenditure."""
        if v.lower() not in expenditure_choices:
            raise ValueError(
                f"Expenditure '{v}' is not a valid choice. Valid choices:\n\n{expenditure_choices}"
            )
        return v


class OECDCPIData(ConsumerPriceIndexData):
    """OECD CPI Data."""

    unit: str = Field(description="Unit of measurement.")
    unit_multiplier: int | float = Field(
        description="Unit multiplier for the observation value.",
    )
    country_code: str = Field(description="ISO3 country code.")
    series_id: str = Field(description="OECD series identifier.")
    expenditure: str = Field(description="Expenditure component of CPI.")
    title: str = Field(description="Complete reference title for the series.")
    order: int | None = Field(
        default=None,
        description="Sort order for expenditure categories.",
    )


class OECDCPIFetcher(Fetcher[OECDCPIQueryParams, list[OECDCPIData]]):
    """OECD CPI Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> OECDCPIQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = date(1950, 1, 1)
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return OECDCPIQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDCPIQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.query_builder import OecdQueryBuilder

        qb = OecdQueryBuilder()
        countries = qb.metadata.resolve_country_codes("DF_PRICES_ALL", query.country)
        country_str = "+".join(countries) if countries else ""
        methodology = "HICP" if query.harmonized is True else "N"
        # Harmonized data not available quarterly — force monthly
        freq = query.frequency

        if query.harmonized is True and freq == "quarter":
            freq = "monthly"

        freq_code = _FREQ_MAP.get(freq, freq[0].upper() if freq else "M")
        transform_code = _TRANSFORM_MAP.get(query.transform, "_Z")
        expenditure_code = (
            ""
            if query.expenditure == "all"
            else expenditure_dict.get(query.expenditure, query.expenditure)
        )

        try:
            result = qb.fetch_data(
                dataflow="DF_PRICES_ALL",
                start_date=str(query.start_date) if query.start_date else None,
                end_date=str(query.end_date) if query.end_date else None,
                _skip_validation=True,
                REF_AREA=country_str,
                FREQ=freq_code,
                METHODOLOGY=methodology,
                MEASURE="CPI",
                EXPENDITURE=expenditure_code,
                TRANSFORMATION=transform_code,
            )
        except Exception as exc:
            raise OpenBBError("No data found for the given query.") from exc

        records = result["data"]

        if not records:
            raise OpenBBError("No data found for the given query.")

        return records

    @staticmethod
    def transform_data(
        query: OECDCPIQueryParams, data: list[dict], **kwargs: Any
    ) -> list[OECDCPIData]:
        """Transform the data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        is_pct = query.transform in ("yoy", "period")
        unit_label = _UNIT_LABELS.get(query.transform, query.transform)
        unit_mult = 100 if is_pct else 1
        methodology = "HICP" if query.harmonized else "CPI"
        output: list[OECDCPIData] = []

        for row in data:
            d = oecd_date_to_python_date(row.get("TIME_PERIOD", ""))

            if d is None:
                continue

            if query.start_date and d < query.start_date:
                continue

            if query.end_date and d > query.end_date:
                continue

            value = row.get("OBS_VALUE")

            if value is None or value == "":
                continue

            value = float(value)

            if is_pct:
                value = value / 100

            exp_code = row.get("EXPENDITURE", "_T")
            country_code = row.get("REF_AREA", "")
            freq_label = row.get("FREQ_label", "")
            measure_label = row.get("MEASURE_label", "Consumer price index")
            exp_label = row.get(
                "EXPENDITURE_label", expenditure_dict_rev.get(exp_code, exp_code)
            )
            transform_label = row.get("TRANSFORMATION_label", unit_label)
            # Build a descriptive title
            # "Monthly Consumer price index - Total - Growth rate, over 1 year"
            title_parts = [f"{freq_label} {measure_label} ({methodology})", exp_label]

            if transform_label and transform_label.lower() not in ("not applicable",):
                title_parts.append(transform_label)

            title = " - ".join(title_parts)
            # Build series_id in the same DATAFLOW::INDICATOR format used by
            # economy.indicators / available_indicators so it's round-trippable.
            series_id = f"DF_PRICES_ALL::{row.get('MEASURE', 'CPI')}"
            output.append(
                OECDCPIData(
                    date=d,
                    country=row.get("REF_AREA_label", country_code),
                    country_code=country_code,
                    value=value,
                    unit=unit_label,
                    unit_multiplier=unit_mult,
                    series_id=series_id,
                    expenditure=exp_label,
                    title=title,
                    order=_EXPENDITURE_ORDER.get(exp_code),
                )
            )

        return sorted(
            output,
            key=lambda x: (x.date, x.country, x.order if x.order is not None else 99),
        )
