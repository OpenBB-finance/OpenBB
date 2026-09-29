"""USDA ERS Area and Road Ruggedness Scales Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_area_and_road_ruggedness_scales import (
    ALL_STATES,
    DEFAULT_STATE,
    DEFAULT_VINTAGE,
    VINTAGE_OPTIONS,
    VINTAGES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix


class AreaAndRoadRuggednessScalesQueryParams(QueryParams):
    """USDA ERS Area and Road Ruggedness Scales Query Parameters.

    Source: https://www.ers.usda.gov/data-products/area-and-road-ruggedness-scales
    """

    __json_schema_extra__ = {
        "vintage": {
            "x-widget_config": {
                "label": "Vintage",
                "value": DEFAULT_VINTAGE,
                "multiSelect": False,
                "multiple": False,
                "options": VINTAGE_OPTIONS,
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "value": DEFAULT_STATE,
                "optionsEndpoint": f"{api_prefix}/usda/area_road_ruggedness_states",
                "optionsParams": {"vintage": "$vintage"},
                "style": {"popupWidth": 280},
            },
        },
    }

    vintage: str = Field(
        default=DEFAULT_VINTAGE,
        description="Census-tract vintage to retrieve, selecting the source"
        + " file. Each vintage is a separate census-tract lookup carrying the"
        + " Area Ruggedness Scale (ARS) and Road Ruggedness Scale (RRS)"
        + " classifications and their terrain statistics. Valid vintages"
        + " are:\n    "
        + ", ".join(VINTAGES)
        + "\n",
    )
    state: str = Field(
        default=DEFAULT_STATE,
        description="State to retrieve, as a two-letter postal abbreviation."
        + " The census-tract lookup carries tens of thousands of rows, so the"
        + " state is the primary scope filter. If None, defaults to West"
        + " Virginia.",
    )

    @field_validator("vintage", mode="before", check_fields=False)
    @classmethod
    def _validate_vintage(cls, v):
        """Validate the census-tract vintage."""
        if not v:
            return DEFAULT_VINTAGE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in VINTAGES:
            raise OpenBBError(
                f"Invalid vintage: {value}. Valid vintages are: " + ", ".join(VINTAGES)
            )
        return value

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate and canonicalize the state filter."""
        if not v:
            return DEFAULT_STATE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().upper()
        if value not in ALL_STATES:
            raise OpenBBError(
                f"Invalid state: {value}. Valid states are: "
                + ", ".join(sorted(ALL_STATES))
            )
        return value


class AreaAndRoadRuggednessScalesData(NullTokenMixin, Data):
    """USDA ERS Area and Road Ruggedness Scales Data.

    One row per census tract for the selected vintage, a geographic
    classification lookup carrying the Area Ruggedness Scale (ARS) and Road
    Ruggedness Scale (RRS) classifications with their terrain ruggedness index
    statistics, the tract's rurality and Ruggedness-Scale region, and its
    population, land area, and population density.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Area and Road Ruggedness Scales",
                "$.description": "Census-tract Area Ruggedness Scale (ARS) and"
                " Road Ruggedness Scale (RRS) classifications, with the"
                " underlying terrain ruggedness index statistics, rurality,"
                " and population, published in vintages by the USDA Economic"
                " Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    tract_fips: str = Field(
        description="Eleven-digit census-tract FIPS code, with leading zeros"
        + " preserved.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Tract FIPS",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 140,
            }
        },
    )
    tract_name: str | None = Field(
        default=None,
        description="Census-tract name, as published.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Tract Name",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )
    county_fips: str | None = Field(
        default=None,
        description="Five-digit county FIPS code, with leading zeros preserved.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "County FIPS",
                "cellDataType": "text",
                "hide": True,
                "maxWidth": 120,
            }
        },
    )
    county_name: str | None = Field(
        default=None,
        description="County or county-equivalent area name, as published.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "County",
                "cellDataType": "text",
                "pinned": "left",
                "minWidth": 180,
            }
        },
    )
    state_fips: str | None = Field(
        default=None,
        description="Two-digit state FIPS code, with a leading zero preserved.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State FIPS",
                "cellDataType": "text",
                "hide": True,
                "maxWidth": 110,
            }
        },
    )
    state: str = Field(
        description="Two-letter state or district postal code.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    state_name: str | None = Field(
        default=None,
        description="Full state or district name.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State Name",
                "cellDataType": "text",
                "pinned": "left",
                "minWidth": 150,
            }
        },
    )
    rs_region: str | None = Field(
        default=None,
        description="Ruggedness-Scale region code, 1 to 12.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "RS Region",
                "cellDataType": "text",
                "hide": True,
                "maxWidth": 110,
            }
        },
    )
    rs_region_name: str | None = Field(
        default=None,
        description="Ruggedness-Scale region name, one of the twelve regions"
        + " the ARS and RRS thresholds are calibrated within.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "RS Region Name",
                "cellDataType": "text",
                "minWidth": 180,
            }
        },
    )
    primary_ruca: str | None = Field(
        default=None,
        description="Primary Rural-Urban Commuting Area (RUCA) code, 1 to 10,"
        + " with 99 marking a water tract.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Primary RUCA",
                "cellDataType": "text",
                "hide": True,
                "maxWidth": 120,
            }
        },
    )
    rurality_code: str | None = Field(
        default=None,
        description="Rurality code, 1 to 3, with 99 marking a tract without a"
        + " rurality code.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Rurality Code",
                "cellDataType": "text",
                "hide": True,
                "maxWidth": 120,
            }
        },
    )
    rurality_name: str | None = Field(
        default=None,
        description="Rurality name: Urbanized area, Urban commuting, Rural, or"
        + " no rurality code.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Rurality",
                "cellDataType": "text",
                "minWidth": 150,
            }
        },
    )
    population: int | None = Field(
        default=None,
        description="Census-tract population, as a full count.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Population",
                "cellDataType": "number",
                "maxWidth": 130,
            }
        },
    )
    land_area: float | None = Field(
        default=None,
        description="Census-tract land area, in square miles.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Land Area (sq mi)",
                "cellDataType": "number",
            }
        },
    )
    pop_density: float | None = Field(
        default=None,
        description="Population density, in persons per square mile.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Pop. Density",
                "cellDataType": "number",
            }
        },
    )
    area_tri_count: int | None = Field(
        default=None,
        description="Count of terrain ruggedness index (TRI) grid cells summed"
        + " over the tract's area.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Area TRI Count",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    area_tri_mean: float | None = Field(
        default=None,
        description="Mean area terrain ruggedness index over the tract, in"
        + " meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Area TRI Mean",
                "cellDataType": "number",
            }
        },
    )
    area_tri_std_dev: float | None = Field(
        default=None,
        description="Standard deviation of the area terrain ruggedness index"
        + " over the tract, in meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Area TRI Std Dev",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    area_tri_median: float | None = Field(
        default=None,
        description="Median area terrain ruggedness index over the tract, in"
        + " meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Area TRI Median",
                "cellDataType": "number",
            }
        },
    )
    area_tri_min: float | None = Field(
        default=None,
        description="Minimum area terrain ruggedness index over the tract, in"
        + " meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Area TRI Min",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    area_tri_max: float | None = Field(
        default=None,
        description="Maximum area terrain ruggedness index over the tract, in"
        + " meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Area TRI Max",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    area_tri_range: float | None = Field(
        default=None,
        description="Range of the area terrain ruggedness index over the tract,"
        + " in meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Area TRI Range",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    ars: str | None = Field(
        default=None,
        description="Area Ruggedness Scale code, 1 to 6, from 1 Level to 6"
        + " Extremely rugged.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "ARS",
                "cellDataType": "text",
                "maxWidth": 90,
            }
        },
    )
    ars_description: str | None = Field(
        default=None,
        description="Area Ruggedness Scale description for the code.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "ARS Description",
                "cellDataType": "text",
                "minWidth": 160,
            }
        },
    )
    road_tri_count: int | None = Field(
        default=None,
        description="Count of terrain ruggedness index (TRI) grid cells sampled"
        + " along the tract's roads.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Road TRI Count",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    road_tri_mean: float | None = Field(
        default=None,
        description="Mean road terrain ruggedness index over the tract, in"
        + " meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Road TRI Mean",
                "cellDataType": "number",
            }
        },
    )
    road_tri_std_dev: float | None = Field(
        default=None,
        description="Standard deviation of the road terrain ruggedness index"
        + " over the tract, in meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Road TRI Std Dev",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    road_tri_median: float | None = Field(
        default=None,
        description="Median road terrain ruggedness index over the tract, in"
        + " meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Road TRI Median",
                "cellDataType": "number",
            }
        },
    )
    road_tri_min: float | None = Field(
        default=None,
        description="Minimum road terrain ruggedness index over the tract, in"
        + " meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Road TRI Min",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    road_tri_max: float | None = Field(
        default=None,
        description="Maximum road terrain ruggedness index over the tract, in"
        + " meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Road TRI Max",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    road_tri_range: float | None = Field(
        default=None,
        description="Range of the road terrain ruggedness index over the tract,"
        + " in meters.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Road TRI Range",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    rrs: str | None = Field(
        default=None,
        description="Road Ruggedness Scale code, 1 to 5, from 1 Level to 5"
        + " Highly rugged.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "RRS",
                "cellDataType": "text",
                "maxWidth": 90,
            }
        },
    )
    rrs_description: str | None = Field(
        default=None,
        description="Road Ruggedness Scale description for the code.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "RRS Description",
                "cellDataType": "text",
                "minWidth": 160,
            }
        },
    )


class AreaAndRoadRuggednessScalesFetcher(
    Fetcher[
        AreaAndRoadRuggednessScalesQueryParams,
        list[AreaAndRoadRuggednessScalesData],
    ]
):
    """Fetch USDA ERS Area and Road Ruggedness Scales for census tracts."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> AreaAndRoadRuggednessScalesQueryParams:
        """Transform the query params."""
        return AreaAndRoadRuggednessScalesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AreaAndRoadRuggednessScalesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected vintage's census-tract lookup records."""
        from openbb_government_us.usda.utils import (
            ers_area_and_road_ruggedness_scales as ers,
        )

        return await ers.afetch_vintage(query.vintage)

    @staticmethod
    def transform_data(
        query: AreaAndRoadRuggednessScalesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AreaAndRoadRuggednessScalesData]:
        """Scope the lookup to the selected state and sort by tract FIPS."""
        rows = [record for record in data if record.get("state") == query.state]
        if not rows:
            raise EmptyDataError("No records match the given filters.")
        rows.sort(key=lambda record: record.get("tract_fips") or "")
        return [
            AreaAndRoadRuggednessScalesData.model_validate(record) for record in rows
        ]
