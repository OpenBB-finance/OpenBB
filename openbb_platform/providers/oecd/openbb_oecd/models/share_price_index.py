"""OECD Share Price Index Model."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.share_price_index import (
    SharePriceIndexData,
    SharePriceIndexQueryParams,
)
from openbb_oecd.utils.constants import FINMARK_COUNTRIES
from pydantic import field_validator

FREQUENCY_MAP = {"monthly": "M", "quarter": "Q", "annual": "A"}


class OECDSharePriceIndexQueryParams(SharePriceIndexQueryParams):
    """OECD Share Price Index Query.

    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(FINMARK_COUNTRIES) + ["all"],
        }
    }

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        return c.replace(" ", "_").strip().lower()


class OECDSharePriceIndexData(SharePriceIndexData):
    """OECD Share Price Index Data."""


class OECDSharePriceIndexFetcher(
    Fetcher[OECDSharePriceIndexQueryParams, list[OECDSharePriceIndexData]]
):
    """OECD Share Price Index Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> OECDSharePriceIndexQueryParams:
        """Transform the query."""
        transformed_params = params.copy()

        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = (
                date(2000, 1, 1)
                if transformed_params.get("country") == "all"
                else date(1958, 1, 1)
            )

        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)

        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return OECDSharePriceIndexQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDSharePriceIndexQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.query_builder import OecdQueryBuilder

        qb = OecdQueryBuilder()
        freq_code = FREQUENCY_MAP.get(query.frequency, "M")

        countries = qb.metadata.resolve_country_codes("DF_FINMARK", query.country)
        country_str = "+".join(countries) if countries else ""

        try:
            result = qb.fetch_data(
                dataflow="DF_FINMARK",
                start_date=(
                    query.start_date.strftime("%Y-%m") if query.start_date else None
                ),
                end_date=query.end_date.strftime("%Y-%m") if query.end_date else None,
                _skip_validation=True,
                REF_AREA=country_str,
                FREQ=freq_code,
                MEASURE="SHARE",
            )
        except Exception as exc:
            raise OpenBBError(f"Error fetching OECD data: {exc}") from exc

        records = result["data"]

        if not records:
            raise OpenBBError(
                "OECD returned no data rows for the given query parameters."
            )

        return records

    @staticmethod
    def transform_data(
        query: OECDSharePriceIndexQueryParams, data: list[dict], **kwargs: Any
    ) -> list[OECDSharePriceIndexData]:
        """Transform the data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        output: list[OECDSharePriceIndexData] = []
        for row in data:
            d = oecd_date_to_python_date(row.get("TIME_PERIOD", ""))

            if d is None:
                continue

            value = row.get("OBS_VALUE")

            if value is None or value == "":
                continue

            output.append(
                OECDSharePriceIndexData(
                    date=d,
                    country=row.get("REF_AREA_label", row.get("REF_AREA", "")),
                    value=float(value),
                )
            )

        return sorted(output, key=lambda x: (x.date, x.country or ""))
