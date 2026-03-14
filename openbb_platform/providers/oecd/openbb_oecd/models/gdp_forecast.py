"""OECD Forecast GDP Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.gdp_forecast import (
    GdpForecastData,
    GdpForecastQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_oecd.utils.constants import GDP_FORECAST_COUNTRIES
from pydantic import Field

_MEASURE_MAP = {
    "current_prices": "GDP_USD",
    "volume": "GDPV_USD",
    "capita": "GDPVD_CAP",
    "growth": "GDPV_ANNPCT",
    "deflator": "PGDP",
}


class OECDGdpForecastQueryParams(GdpForecastQueryParams):
    """OECD GDP Forecast Query.

    The OECD Economic Outlook presents the OECD's analysis of the major
    global economic trends and prospects for the next two years.
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(GDP_FORECAST_COUNTRIES) + ["all"],
        },
    }

    country: str = Field(
        description="Country, or countries, to get forward GDP projections for. Default is all.",
        default="all",
    )
    frequency: Literal["annual", "quarter"] = Field(
        default="annual",
        description="Frequency of the data, default is annual.",
        json_schema_extra={"choices": ["annual", "quarter"]},
    )
    units: Literal["current_prices", "volume", "capita", "growth", "deflator"] = Field(
        default="volume",
        description="Units of the data, default is volume (chain linked volume, 2015)."
        + "\n'current_prices', 'volume', and 'capita' are expressed in USD; 'growth' as a percent;"
        + " 'deflator' as an index.",
        json_schema_extra={
            "choices": ["current_prices", "volume", "capita", "growth", "deflator"]
        },
    )


class OECDGdpForecastData(GdpForecastData):
    """OECD GDP Forecast Data."""


class OECDGdpForecastFetcher(
    Fetcher[OECDGdpForecastQueryParams, list[OECDGdpForecastData]]
):
    """OECD GDP Forecast Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> OECDGdpForecastQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        countries = transformed_params.get("country")
        if not countries:
            transformed_params["country"] = "all"

        if not transformed_params.get("start_date"):
            transformed_params["start_date"] = datetime(
                datetime.today().year, 1, 1
            ).date()

        if not transformed_params.get("end_date"):
            transformed_params["end_date"] = datetime(
                datetime.today().year + 2, 12, 31
            ).date()

        return OECDGdpForecastQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: OECDGdpForecastQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.query_builder import OecdQueryBuilder

        qb = OecdQueryBuilder()
        freq_code = "Q" if query.frequency == "quarter" else "A"
        measure = _MEASURE_MAP.get(query.units, "GDPV_USD")

        if query.units == "capita" and freq_code == "Q":
            warn(
                "Capita data is not available for quarterly data, using annual data instead."
            )
            freq_code = "A"

        countries = qb.metadata.resolve_country_codes("DF_EO", query.country)
        country_str = "+".join(countries) if countries else ""

        try:
            result = qb.fetch_data(
                dataflow="DF_EO",
                start_date=str(query.start_date) if query.start_date else None,
                end_date=str(query.end_date) if query.end_date else None,
                _skip_validation=True,
                REF_AREA=country_str,
                MEASURE=measure,
                FREQ=freq_code,
            )
        except Exception as exc:
            raise OpenBBError(f"Error fetching OECD data: {exc}") from exc

        records = result["data"]
        if not records:
            raise EmptyDataError("No data was found.")

        return records

    @staticmethod
    def transform_data(
        query: OECDGdpForecastQueryParams, data: list[dict], **kwargs: Any
    ) -> list[OECDGdpForecastData]:
        """Transform the data from the OECD endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        is_growth = query.units == "growth"
        is_deflator = query.units == "deflator"
        output: list[OECDGdpForecastData] = []
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
            elif not is_deflator:
                value = int(value)
            if value <= 0:
                continue
            output.append(
                OECDGdpForecastData(
                    date=d,
                    country=row.get("REF_AREA_label", row.get("REF_AREA", "")),
                    value=value,
                )
            )

        return sorted(output, key=lambda x: (x.date, -(x.value or 0)))
