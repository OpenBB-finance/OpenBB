"""OECD House Price Index Model."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.house_price_index import (
    HousePriceIndexData,
    HousePriceIndexQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_oecd.utils.constants import RHPI_COUNTRIES
from pydantic import Field, field_validator

FREQUENCY_MAP = {"monthly": "M", "quarter": "Q", "annual": "A"}
TRANSFORM_MAP = {"yoy": "PA", "period": "PC", "index": "IX"}


class OECDHousePriceIndexQueryParams(HousePriceIndexQueryParams):
    """OECD House Price Index Query.

    Notes
    -----
    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(RHPI_COUNTRIES) + ["all"],
        }
    }

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        return c.replace(" ", "_").strip().lower()


class OECDHousePriceIndexData(HousePriceIndexData):
    """OECD House Price Index Data."""


class OECDHousePriceIndexFetcher(
    Fetcher[OECDHousePriceIndexQueryParams, list[OECDHousePriceIndexData]]
):
    """OECD House Price Index Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> OECDHousePriceIndexQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                date(2000, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1969, 1, 1)
            )
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return OECDHousePriceIndexQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDHousePriceIndexQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.query_builder import OecdQueryBuilder

        qb = OecdQueryBuilder()
        freq_code = FREQUENCY_MAP.get(query.frequency, "Q")
        transform = TRANSFORM_MAP.get(query.transform, "PA")

        countries = qb.metadata.resolve_country_codes("DF_RHPI_TARGET", query.country)
        country_str = "+".join(countries) if countries else ""

        try:
            result = qb.fetch_data(
                dataflow="DF_RHPI_TARGET",
                start_date=(
                    query.start_date.strftime("%Y-%m") if query.start_date else None
                ),
                end_date=query.end_date.strftime("%Y-%m") if query.end_date else None,
                _skip_validation=True,
                REF_AREA_TYPE="COU",
                REF_AREA=country_str,
                FREQ=freq_code,
                MEASURE="RHPI",
                UNIT_MEASURE=transform,
            )
        except Exception as exc:
            # Fallback from monthly to quarterly if fetch fails
            if freq_code == "M":
                warn("No monthly data found. Switching to quarterly data.")
                try:
                    result = qb.fetch_data(
                        dataflow="DF_RHPI_TARGET",
                        start_date=(
                            query.start_date.strftime("%Y-%m")
                            if query.start_date
                            else None
                        ),
                        end_date=(
                            query.end_date.strftime("%Y-%m") if query.end_date else None
                        ),
                        _skip_validation=True,
                        REF_AREA_TYPE="COU",
                        REF_AREA=country_str,
                        FREQ="Q",
                        MEASURE="RHPI",
                        UNIT_MEASURE=transform,
                    )
                except Exception as exc2:
                    raise OpenBBError(f"Error fetching OECD data: {exc2}") from exc2
            else:
                raise OpenBBError(f"Error fetching OECD data: {exc}") from exc

        records = result["data"]
        if not records:
            raise EmptyDataError()

        return records

    @staticmethod
    def transform_data(
        query: OECDHousePriceIndexQueryParams, data: list[dict], **kwargs: Any
    ) -> list[OECDHousePriceIndexData]:
        """Transform the data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        output: list[OECDHousePriceIndexData] = []
        for row in data:
            d = oecd_date_to_python_date(row.get("TIME_PERIOD", ""))

            if d is None:
                continue

            value = row.get("OBS_VALUE")

            if value is None or value == "":
                continue

            if query.transform and query.transform != "index":
                value = float(value) / 100.0

            output.append(
                OECDHousePriceIndexData(
                    date=d,
                    country=row.get("REF_AREA_label", row.get("REF_AREA", "")),
                    value=float(value),
                )
            )

        return sorted(output, key=lambda x: (x.date, x.country or ""))
