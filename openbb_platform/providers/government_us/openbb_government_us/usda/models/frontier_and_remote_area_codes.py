"""USDA ERS Frontier and Remote Area Codes (ZIP) Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_frontier_and_remote_area_codes import (
    ALL_STATES,
    DEFAULT_STATE,
    DEFAULT_YEAR,
    FAR_ZIP_FILES,
    year_options,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix


class FrontierAndRemoteAreaCodesQueryParams(QueryParams):
    """USDA ERS Frontier and Remote Area Codes Query Parameters.

    Source: https://www.ers.usda.gov/data-products/frontier-and-remote-area-codes
    """

    __json_schema_extra__ = {
        "year": {
            "x-widget_config": {
                "label": "Vintage",
                "value": DEFAULT_YEAR,
                "multiSelect": False,
                "multiple": False,
                "options": year_options(),
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "value": DEFAULT_STATE,
                "optionsEndpoint": f"{api_prefix}/usda/far_zip_states",
                "optionsParams": {"year": "$year"},
            },
        },
    }

    year: str = Field(
        default=DEFAULT_YEAR,
        description="Decennial classification vintage to retrieve, selecting the"
        + " source workbook. Valid vintages are:\n    "
        + ", ".join(FAR_ZIP_FILES)
        + "\n",
    )
    state: str = Field(
        default=DEFAULT_STATE,
        description="State to retrieve, as a two-letter postal abbreviation. The"
        + " ZIP-code lookup carries tens of thousands of rows, so the state is"
        + " the primary scope filter. The 2000 vintage covers the contiguous"
        + " States and excludes Alaska and Hawaii. If None, defaults to Montana.",
    )

    @field_validator("year", mode="before", check_fields=False)
    @classmethod
    def _validate_year(cls, v):
        """Validate the classification vintage."""
        if not v:
            return DEFAULT_YEAR
        year = str(v).strip()
        if year not in FAR_ZIP_FILES:
            raise OpenBBError(
                f"Invalid vintage: {year}. Valid vintages are: "
                + ", ".join(FAR_ZIP_FILES)
            )
        return year

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate and canonicalize the state filter."""
        if not v:
            return DEFAULT_STATE
        state = str(v).strip().upper()
        if state not in ALL_STATES:
            raise OpenBBError(
                f"Invalid state: {state}. Valid states are: "
                + ", ".join(sorted(ALL_STATES))
            )
        return state


class FrontierAndRemoteAreaCodesData(NullTokenMixin, Data):
    """USDA ERS Frontier and Remote Area Codes Data.

    One row per ZIP-code area for the selected vintage, a geographic
    classification lookup carrying the four Frontier and Remote (FAR) level
    flags with the area's grid population, land area, and population density,
    plus the population and population share classified at each FAR level.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Frontier and Remote Area Codes (ZIP)",
                "$.description": "Frontier and Remote (FAR) area classification"
                " for U.S. ZIP Code areas at four FAR levels, with grid"
                " population, land area, and population density, published by"
                " the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    zip_code: str = Field(
        description="ZIP Code of the area.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "ZIP Code",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 110,
            }
        },
    )
    state: str = Field(
        description="Two-letter postal abbreviation of the area's State.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    po_name: str | None = Field(
        default=None,
        description="Post office name of the ZIP-code area, as published. The"
        + " 2000 vintage carries no area name.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Area Name",
                "cellDataType": "text",
                "pinned": "left",
                "hide": True,
            }
        },
    )
    far_level_1: int | None = Field(
        default=None,
        description="FAR level 1 flag: 1 when the area is frontier and remote at"
        + " level 1, else 0.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 1",
                "cellDataType": "text",
                "maxWidth": 110,
            }
        },
    )
    far_level_2: int | None = Field(
        default=None,
        description="FAR level 2 flag: 1 when the area is frontier and remote at"
        + " level 2, else 0.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 2",
                "cellDataType": "text",
                "maxWidth": 110,
            }
        },
    )
    far_level_3: int | None = Field(
        default=None,
        description="FAR level 3 flag: 1 when the area is frontier and remote at"
        + " level 3, else 0.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 3",
                "cellDataType": "text",
                "maxWidth": 110,
            }
        },
    )
    far_level_4: int | None = Field(
        default=None,
        description="FAR level 4 flag: 1 when the area is frontier and remote at"
        + " level 4, else 0.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 4",
                "cellDataType": "text",
                "maxWidth": 110,
            }
        },
    )
    grid_population: float | None = Field(
        default=None,
        description="Population of the area's populated grid cells.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Grid Population",
                "cellDataType": "number",
            }
        },
    )
    land_area_sq_mi: float | None = Field(
        default=None,
        description="Land area of the area, in square miles.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Land Area (sq mi)",
                "cellDataType": "number",
            }
        },
    )
    population_density: float | None = Field(
        default=None,
        description="Population density of the area, in persons per square mile.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Population Density",
                "cellDataType": "number",
            }
        },
    )
    far_level_1_population: float | None = Field(
        default=None,
        description="Population of the area classified as FAR level 1.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 1 Population",
                "cellDataType": "number",
            }
        },
    )
    far_level_2_population: float | None = Field(
        default=None,
        description="Population of the area classified as FAR level 2.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 2 Population",
                "cellDataType": "number",
            }
        },
    )
    far_level_3_population: float | None = Field(
        default=None,
        description="Population of the area classified as FAR level 3.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 3 Population",
                "cellDataType": "number",
            }
        },
    )
    far_level_4_population: float | None = Field(
        default=None,
        description="Population of the area classified as FAR level 4.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 4 Population",
                "cellDataType": "number",
            }
        },
    )
    far_level_1_population_pct: float | None = Field(
        default=None,
        description="Share of the area's grid population classified as FAR"
        + " level 1, in percent.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 1 Population %",
                "cellDataType": "number",
            }
        },
    )
    far_level_2_population_pct: float | None = Field(
        default=None,
        description="Share of the area's grid population classified as FAR"
        + " level 2, in percent.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 2 Population %",
                "cellDataType": "number",
            }
        },
    )
    far_level_3_population_pct: float | None = Field(
        default=None,
        description="Share of the area's grid population classified as FAR"
        + " level 3, in percent.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 3 Population %",
                "cellDataType": "number",
            }
        },
    )
    far_level_4_population_pct: float | None = Field(
        default=None,
        description="Share of the area's grid population classified as FAR"
        + " level 4, in percent.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FAR Level 4 Population %",
                "cellDataType": "number",
            }
        },
    )


class FrontierAndRemoteAreaCodesFetcher(
    Fetcher[
        FrontierAndRemoteAreaCodesQueryParams,
        list[FrontierAndRemoteAreaCodesData],
    ]
):
    """Fetch USDA ERS Frontier and Remote Area Codes for ZIP-code areas."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FrontierAndRemoteAreaCodesQueryParams:
        """Transform the query params."""
        return FrontierAndRemoteAreaCodesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FrontierAndRemoteAreaCodesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected vintage's ZIP-code lookup rows."""
        from openbb_government_us.usda.utils import (
            ers_frontier_and_remote_area_codes as ers,
        )

        return await ers.afetch_far_zip(query.year)

    @staticmethod
    def transform_data(
        query: FrontierAndRemoteAreaCodesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FrontierAndRemoteAreaCodesData]:
        """Scope the lookup to the selected state and sort by ZIP code."""
        rows = [record for record in data if record.get("state") == query.state]
        rows.sort(key=lambda record: record.get("zip_code") or "")
        return [
            FrontierAndRemoteAreaCodesData.model_validate(record) for record in rows
        ]
