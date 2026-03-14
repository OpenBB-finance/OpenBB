"""OECD Country Interest Rates Data."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.country_interest_rates import (
    CountryInterestRatesData,
    CountryInterestRatesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_oecd.utils.constants import KEI_COUNTRIES
from pydantic import Field, field_validator

DURATION_DICT = {
    "immediate": "IRSTCI",
    "short": "IR3TIB",
    "long": "IRLT",
}


class OecdCountryInterestRatesQueryParams(CountryInterestRatesQueryParams):
    """OECD Country Interest Rates Query."""

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(KEI_COUNTRIES) + ["all"],
        },
        "frequency": {
            "multiple_items_allowed": False,
            "choices": ["monthly", "quarter", "annual"],
        },
        "duration": {
            "multiple_items_allowed": False,
            "choices": ["immediate", "short", "long"],
        },
    }

    duration: Literal["immediate", "short", "long"] = Field(
        description="Duration of the interest rate."
        + " 'immediate' is the overnight rate, 'short' is the 3-month rate, and 'long' is the 10-year rate.",
        default="short",
    )
    frequency: Literal["monthly", "quarter", "annual"] = Field(
        description="Frequency to get interest rate for for.", default="monthly"
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        return c.replace(" ", "_").strip().lower()


class OecdCountryInterestRatesData(CountryInterestRatesData):
    """OECD Country Interest Rates Data."""


class OecdCountryInterestRatesFetcher(
    Fetcher[OecdCountryInterestRatesQueryParams, list[OecdCountryInterestRatesData]]
):
    """OECD Country Interest Rates Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> OecdCountryInterestRatesQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                date(2020, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1954, 1, 1)
            )
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return OecdCountryInterestRatesQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OecdCountryInterestRatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.query_builder import OecdQueryBuilder

        qb = OecdQueryBuilder()
        freq_code = query.frequency[0].upper()
        measure = DURATION_DICT.get(query.duration, "IR3TIB")
        countries = qb.metadata.resolve_country_codes("DF_KEI", query.country)
        country_str = "+".join(countries) if countries else ""

        try:
            result = qb.fetch_data(
                dataflow="DF_KEI",
                start_date=(
                    query.start_date.strftime("%Y-%m") if query.start_date else None
                ),
                end_date=query.end_date.strftime("%Y-%m") if query.end_date else None,
                _skip_validation=True,
                REF_AREA=country_str,
                FREQ=freq_code,
                MEASURE=measure,
                UNIT_MEASURE="PA",
                ACTIVITY="_Z",
                ADJUSTMENT="_Z",
                TRANSFORMATION="_Z",
            )
        except Exception as exc:
            raise OpenBBError(f"Error fetching OECD data: {exc}") from exc

        records = result["data"]

        if not records:
            raise EmptyDataError()

        return records

    @staticmethod
    def transform_data(
        query: OecdCountryInterestRatesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[OecdCountryInterestRatesData]:
        """Transform the data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        output: list[OecdCountryInterestRatesData] = []

        for row in data:
            d = oecd_date_to_python_date(row.get("TIME_PERIOD", ""))

            if d is None:
                continue

            value = row.get("OBS_VALUE")

            if value is None or value == "":
                continue

            output.append(
                OecdCountryInterestRatesData(
                    date=d,
                    country=row.get("REF_AREA_label", row.get("REF_AREA", "")),
                    value=float(value) / 100,
                )
            )

        return sorted(output, key=lambda x: (x.date, x.country or ""))
