"""OECD Composite Leading Indicator Data."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Literal
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.composite_leading_indicator import (
    CompositeLeadingIndicatorData,
    CompositeLeadingIndicatorQueryParams,
)
from openbb_oecd.utils.constants import CLI_COUNTRIES
from pydantic import Field, field_validator

COUNTRY_CHOICES = list(CLI_COUNTRIES) + ["all"]


class OECDCompositeLeadingIndicatorQueryParams(CompositeLeadingIndicatorQueryParams):
    """OECD Composite Leading Indicator Query."""

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": COUNTRY_CHOICES,
        },
    }

    country: str = Field(
        description="Country to get the CLI for, default is G20.",
        default="g20",
    )
    adjustment: Literal["amplitude", "normalized"] = Field(
        default="amplitude",
        description="Adjustment of the data, either 'amplitude' or 'normalized'."
        + " Default is amplitude.",
        json_schema_extra={"choices": ["amplitude", "normalized"]},
    )
    growth_rate: bool = Field(
        default=False,
        description="Return the 1-year growth rate (%) of the CLI, default is False.",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def country_validate(cls, v):
        """Validate countries."""
        if v is None:
            return "g20"
        new_countries: list = []
        if isinstance(v, str):
            countries = v.split(",")
        elif isinstance(v, list):
            countries = v
        if "all" in countries:
            return "all"
        for country in countries:
            if country.lower() not in COUNTRY_CHOICES:
                warn(f"Country {country} not supported, skipping...")
            else:
                new_countries.append(country)
        if not new_countries:
            raise OpenBBError("No valid countries found.")
        return ",".join(new_countries)


class OECDCompositeLeadingIndicatorData(CompositeLeadingIndicatorData):
    """OECD Composite Leading Indicator Data."""


class OECDCompositeLeadingIndicatorFetcher(
    Fetcher[
        OECDCompositeLeadingIndicatorQueryParams,
        list[OECDCompositeLeadingIndicatorData],
    ]
):
    """OECD Composite Leading Indicator Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> OECDCompositeLeadingIndicatorQueryParams:
        """Transform the query."""
        transformed_params = params.copy()

        if not transformed_params.get("start_date"):
            transformed_params["start_date"] = (
                date(2020, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1947, 1, 1)
            )

        if not transformed_params.get("end_date"):
            transformed_params["end_date"] = date(date.today().year, 12, 31)

        if not transformed_params.get("country"):
            transformed_params["country"] = "g20"

        return OECDCompositeLeadingIndicatorQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDCompositeLeadingIndicatorQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.query_builder import OecdQueryBuilder

        qb = OecdQueryBuilder()
        growth_rate = "GY" if query.growth_rate is True else "IX"
        adjustment = "AA" if query.adjustment == "amplitude" else "NOR"

        if growth_rate == "GY":
            adjustment = ""

        countries = qb.metadata.resolve_country_codes("DF_CLI", query.country)
        country_str = "+".join(countries) if countries else ""

        try:
            result = qb.fetch_data(
                dataflow="DF_CLI",
                start_date=str(query.start_date) if query.start_date else None,
                end_date=str(query.end_date) if query.end_date else None,
                _skip_validation=True,
                REF_AREA=country_str,
                FREQ="M",
                MEASURE="LI",
                ADJUSTMENT=adjustment,
                TRANSFORMATION=growth_rate,
                METHODOLOGY="H",
            )
        except Exception as exc:
            raise OpenBBError(f"Error fetching OECD data: {exc}") from exc

        records = result["data"]

        if not records:
            raise OpenBBError("No data returned from OECD for the given query.")

        return records

    @staticmethod
    def transform_data(
        query: OECDCompositeLeadingIndicatorQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[OECDCompositeLeadingIndicatorData]:
        """Transform the data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        is_growth = query.growth_rate is True
        output: list[OECDCompositeLeadingIndicatorData] = []

        for row in data:
            d = oecd_date_to_python_date(row.get("TIME_PERIOD", ""))

            if d is None:
                continue

            value = row.get("OBS_VALUE")

            if value is None or value == "":
                continue

            value = float(value)

            if is_growth:
                value = value / 100

            output.append(
                OECDCompositeLeadingIndicatorData(
                    date=d,
                    country=row.get("REF_AREA_label", row.get("REF_AREA", "")),
                    value=value,
                )
            )

        return sorted(output, key=lambda x: (x.date, x.country or ""))
