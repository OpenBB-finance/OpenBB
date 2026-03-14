"""OECD Nominal GDP Model."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.gdp_nominal import (
    GdpNominalData,
    GdpNominalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_oecd.utils.constants import GDP_REAL_COUNTRIES
from pydantic import Field, field_validator

# Map units param to data-flow suffix and price-base code.
_UNIT_DATAFLOW = {
    "level": "USD",
    "index": "INDICES",
    "capita": "CAPITA",
}


class OECDGdpNominalQueryParams(GdpNominalQueryParams):
    """OECD Nominal GDP Query.

    Notes
    -----
    Source: https://www.oecd.org/en/data/datasets/gdp-and-non-financial-accounts.html
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(GDP_REAL_COUNTRIES) + ["all"],
        }
    }

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", "")
        + " Use 'all' to get data for all available countries.",
        default="united_states",
    )
    frequency: Literal["quarter", "annual"] = Field(
        description="Frequency of the data.",
        default="quarter",
        json_schema_extra={"choices": ["quarter", "annual"]},
    )
    units: Literal["level", "index", "capita"] = Field(
        default="level",
        description=QUERY_DESCRIPTIONS.get("units", "")
        + "Both 'level' and 'capita' (per) are measured in USD.",
        json_schema_extra={"choices": ["level", "index", "capita"]},
    )
    price_base: Literal["current_prices", "volume"] = Field(
        default="current_prices",
        description="Price base for the data, volume is chain linked volume.",
        json_schema_extra={"choices": ["current_prices", "volume"]},
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        return c.replace(" ", "_").strip().lower()


class OECDGdpNominalData(GdpNominalData):
    """OECD Nominal GDP Data."""


class OECDGdpNominalFetcher(
    Fetcher[OECDGdpNominalQueryParams, list[OECDGdpNominalData]]
):
    """OECD GDP Nominal Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> OECDGdpNominalQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                date(2020, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1947, 1, 1)
            )
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return OECDGdpNominalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDGdpNominalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.query_builder import OecdQueryBuilder

        qb = OecdQueryBuilder()
        freq_code = "Q" if query.frequency == "quarter" else "A"

        unit_suffix = _UNIT_DATAFLOW.get(query.units, "USD")
        dataflow = f"DF_QNA_EXPENDITURE_{unit_suffix}"

        price_base = "V" if query.price_base == "current_prices" else "LR"
        if query.units == "index" and price_base == "V":
            price_base = "DR"

        countries = qb.metadata.resolve_country_codes(dataflow, query.country)
        country_str = "+".join(countries) if countries else ""

        transaction = "B1GQ_POP" if query.units == "capita" else "B1GQ"

        try:
            result = qb.fetch_data(
                dataflow=dataflow,
                start_date=str(query.start_date) if query.start_date else None,
                end_date=str(query.end_date) if query.end_date else None,
                _skip_validation=True,
                FREQ=freq_code,
                REF_AREA=country_str,
                SECTOR="S1",
                TRANSACTION=transaction,
                PRICE_BASE=price_base,
            )
        except Exception as exc:
            raise OpenBBError(f"Error fetching OECD data: {exc}") from exc

        records = result["data"]
        if not records:
            raise EmptyDataError()

        return records

    @staticmethod
    def transform_data(
        query: OECDGdpNominalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[OECDGdpNominalData]:
        """Transform the data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        is_level = query.units == "level"
        output: list[OECDGdpNominalData] = []
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
            if is_level:
                value = int(value * 1_000_000)
            output.append(
                OECDGdpNominalData(
                    date=d,
                    country=row.get("REF_AREA_label", row.get("REF_AREA", "")),
                    value=value,
                )
            )

        return sorted(output, key=lambda x: (x.date, -(x.value or 0)))
