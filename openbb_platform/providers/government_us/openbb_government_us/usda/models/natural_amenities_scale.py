"""USDA ERS Natural Amenities Scale Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_natural_amenities_scale import (
    ALL_STATES,
    state_options,
)
from openbb_government_us.utils.serializers import NullTokenMixin


class NaturalAmenitiesScaleQueryParams(QueryParams):
    """USDA ERS Natural Amenities Scale Query Parameters.

    Source: https://www.ers.usda.gov/data-products/natural-amenities-scale
    """

    __json_schema_extra__ = {
        "state": {
            "x-widget_config": {
                "label": "State",
                "multiSelect": False,
                "multiple": False,
                "options": state_options(),
                "style": {"popupWidth": 260},
            },
        },
    }

    state: str | None = Field(
        default=None,
        description="Two-letter state postal abbreviation to scope the county"
        + " rows to a single state. If None, returns every county. The scale"
        + " covers the 48 contiguous states and the District of Columbia;"
        + " Alaska, Hawaii, and the territories are not scored.",
    )

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate the optional state filter."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        state = str(value).strip().upper()
        if not state:
            return None
        if state not in ALL_STATES:
            raise OpenBBError(
                f"Invalid state: {value}. Use a two-letter postal abbreviation,"
                + " e.g. 'TX'."
            )
        return state


class NaturalAmenitiesScaleData(NullTokenMixin, Data):
    """USDA ERS Natural Amenities Scale Data.

    A county lookup: one row per county FIPS carrying the six underlying
    physical measures, their standardized Z-scores, the composite natural
    amenity scale value, the 1-to-7 amenity rank, and the census division,
    Rural-Urban Continuum, Urban Influence, and topography classification
    codes.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Natural Amenities Scale",
                "$.description": "County-level natural amenities scale and its"
                " six climate, topography, and water-area components for the"
                " contiguous United States, published by the USDA Economic"
                " Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    fips: str = Field(
        description="County FIPS code, five digits with a leading zero.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FIPS",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 100,
            }
        },
    )
    fips_used_for_measures: str | None = Field(
        default=None,
        description="County FIPS whose measures this row carries, equal to the"
        + " FIPS code except for the 41 combined areas whose measures are"
        + " reported under a neighboring county.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FIPS Used for Measures",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )
    state: str | None = Field(
        default=None,
        description="Two-letter state postal abbreviation.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    county_name: str | None = Field(
        default=None,
        description="County or county-equivalent area name, as published.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "County",
                "pinned": "left",
                "minWidth": 180,
            }
        },
    )
    census_division: str | None = Field(
        default=None,
        description="Census division code, 1 to 9.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Census Division",
                "cellDataType": "text",
                "maxWidth": 150,
            }
        },
    )
    rural_urban_continuum_code: str | None = Field(
        default=None,
        description="Rural-Urban Continuum (Beale) code, 1993 vintage.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Rural-Urban Continuum Code (1993)",
                "cellDataType": "text",
            }
        },
    )
    urban_influence_code: str | None = Field(
        default=None,
        description="Urban Influence Code, 1993 vintage.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Urban Influence Code (1993)",
                "cellDataType": "text",
            }
        },
    )
    mean_january_temperature: float | None = Field(
        default=None,
        description="Mean January temperature in degrees Fahrenheit, 1941-70.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Mean January Temp (F)",
                "cellDataType": "number",
            }
        },
    )
    mean_january_sunlight: float | None = Field(
        default=None,
        description="Mean hours of January sunlight, 1941-70.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Mean January Sunlight (hrs)",
                "cellDataType": "number",
            }
        },
    )
    mean_july_temperature: float | None = Field(
        default=None,
        description="Mean July temperature in degrees Fahrenheit, 1941-70.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Mean July Temp (F)",
                "cellDataType": "number",
            }
        },
    )
    mean_july_humidity: float | None = Field(
        default=None,
        description="Mean relative July humidity in percent, 1941-70.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Mean July Humidity (%)",
                "cellDataType": "number",
            }
        },
    )
    topography_code: str | None = Field(
        default=None,
        description="Land surface form topography code, 1 to 21.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Topography Code",
                "cellDataType": "text",
            }
        },
    )
    percent_water_area: float | None = Field(
        default=None,
        description="Water area as a percent of the county's total area.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Percent Water Area",
                "cellDataType": "number",
            }
        },
    )
    log_water_area: float | None = Field(
        default=None,
        description="Natural log of the county's water area times 100.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Log Water Area x100",
                "cellDataType": "number",
            }
        },
    )
    january_temperature_z: float | None = Field(
        default=None,
        description="Standardized Z-score of the mean January temperature.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Jan Temp (Z)",
                "cellDataType": "number",
            }
        },
    )
    january_sunlight_z: float | None = Field(
        default=None,
        description="Standardized Z-score of the mean January sunlight.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Jan Sun (Z)",
                "cellDataType": "number",
            }
        },
    )
    july_temperature_z: float | None = Field(
        default=None,
        description="Standardized Z-score of the mean July temperature.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Jul Temp (Z)",
                "cellDataType": "number",
            }
        },
    )
    july_humidity_z: float | None = Field(
        default=None,
        description="Standardized Z-score of the mean July humidity, inverted"
        + " so that lower humidity scores higher.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Jul Humidity (Z)",
                "cellDataType": "number",
            }
        },
    )
    topography_z: float | None = Field(
        default=None,
        description="Standardized Z-score of the topography code.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Topography (Z)",
                "cellDataType": "number",
            }
        },
    )
    log_water_area_z: float | None = Field(
        default=None,
        description="Standardized Z-score of the log water area.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Log Water Area (Z)",
                "cellDataType": "number",
            }
        },
    )
    natural_amenity_scale: float | None = Field(
        default=None,
        description="Composite natural amenity scale, the sum of the six"
        + " standardized Z-scores.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Natural Amenity Scale",
                "cellDataType": "number",
            }
        },
    )
    natural_amenity_rank: str | None = Field(
        default=None,
        description="Natural amenity rank derived from the scale, 1 for the"
        + " lowest amenity through 7 for the highest.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Amenity Rank (1=Low, 7=High)",
                "cellDataType": "text",
            }
        },
    )


class NaturalAmenitiesScaleFetcher(
    Fetcher[
        NaturalAmenitiesScaleQueryParams,
        list[NaturalAmenitiesScaleData],
    ]
):
    """Fetch USDA ERS Natural Amenities Scale."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NaturalAmenitiesScaleQueryParams:
        """Transform the query params."""
        return NaturalAmenitiesScaleQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NaturalAmenitiesScaleQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the county-lookup records."""
        from openbb_government_us.usda.utils import ers_natural_amenities_scale

        return await ers_natural_amenities_scale.afetch_records()

    @staticmethod
    def transform_data(
        query: NaturalAmenitiesScaleQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[NaturalAmenitiesScaleData]:
        """Scope the county rows to the selected state and sort by FIPS."""
        selected = [
            record
            for record in data
            if query.state is None or record.get("state") == query.state
        ]
        if not selected:
            raise EmptyDataError("No records match the given filters.")
        selected.sort(key=lambda record: record["fips"])
        return [NaturalAmenitiesScaleData.model_validate(record) for record in selected]
