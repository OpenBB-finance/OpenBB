"""USDA ERS Rural-Urban Commuting Area Codes Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.ers_rural_urban_commuting_area_codes import (
    DEFAULT_STATE,
    DEFAULT_TABLE,
    TABLE_LABELS,
    allowed_states,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

TABLE_OPTIONS = [{"label": label, "value": key} for key, label in TABLE_LABELS.items()]

SERVED_FIELDS = (
    "area_fips",
    "state",
    "county",
    "area_name",
    "area_type",
    "primary_ruca",
    "primary_ruca_description",
    "secondary_ruca",
    "secondary_ruca_description",
    "population",
    "land_area",
    "population_density",
)


class RuralUrbanCommutingAreaCodesQueryParams(QueryParams):
    """USDA ERS Rural-Urban Commuting Area Codes Query Parameters.

    Source: https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": TABLE_OPTIONS,
                "style": {"popupWidth": 260},
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "type": "endpoint",
                "value": DEFAULT_STATE,
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/ruca_states",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 280},
            },
        },
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Vintage and geography of the code set to retrieve, as one"
        + " lookup table per census-tract or ZIP-code vintage. Valid tables"
        + " are:\n    "
        + ", ".join(TABLE_LABELS)
        + "\n",
    )
    state: str | None = Field(
        default=DEFAULT_STATE,
        description="Two-letter state or territory code to scope the lookup to,"
        + " e.g. 'DE'. If None, every area in the table is returned, which is"
        + " tens of thousands of rows. The set of states differs by table.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in TABLE_LABELS:
            raise OpenBBError(
                f"Invalid table: {value}. Valid tables are: " + ", ".join(TABLE_LABELS)
            )
        return value

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Normalize state to an upper-case two-letter code or None for all."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().upper()
        return value or None

    @model_validator(mode="after")
    def _validate_state_for_table(self):
        """Validate that the state is published for the selected table."""
        if self.state is None:
            return self
        codes = allowed_states(self.table)
        if self.state not in codes:
            raise OpenBBError(
                f"Invalid state '{self.state}' for table '{self.table}'."
                + " Valid states are: "
                + ", ".join(codes)
            )
        return self


class RuralUrbanCommutingAreaCodesData(NullTokenMixin, Data):
    """USDA ERS Rural-Urban Commuting Area Codes Data.

    One row per geographic unit (census tract or ZIP code) of the selected
    vintage, carrying its primary and secondary RUCA classification codes,
    the code descriptions, and any published area attributes. This is a
    lookup table, not a time series, so there is no pivot.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Rural-Urban Commuting Area (RUCA) Codes",
                "$.description": "Whole-number and decimal Rural-Urban"
                " Commuting Area classification codes for U.S. census tracts"
                " and ZIP codes across the 1990, 2000, 2010, and 2020"
                " vintages, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    area_fips: str = Field(
        description="Geographic identifier of the row: the 11-digit census"
        + " tract FIPS code for a tract table, or the 5-digit ZIP code for a"
        + " ZIP table.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FIPS / ZIP Code",
                "cellDataType": "text",
                "pinned": "left",
            }
        },
    )
    state: str | None = Field(
        default=None,
        description="Two-letter state or territory code of the area.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    county: str | None = Field(
        default=None,
        description="County of the census tract, for the tract tables that"
        + " publish it. Not published for the ZIP or 1990 tables.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "County",
                "cellDataType": "text",
                "pinned": "left",
                "minWidth": 160,
            }
        },
    )
    area_name: str | None = Field(
        default=None,
        description="Name of the area: the census-tract name for the 2020"
        + " tract table or the post-office name for the 2020 ZIP table."
        + " Not published for the other tables.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Area name",
                "cellDataType": "text",
                "minWidth": 160,
            }
        },
    )
    area_type: str | None = Field(
        default=None,
        description="Type of the ZIP record, 'ZIP Code Area' or a post office"
        + " or large-volume customer, for the ZIP tables. Not published for"
        + " the tract tables.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "ZIP type",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )
    primary_ruca: str | None = Field(
        default=None,
        description="Primary RUCA code, a whole number 1 to 10 or 99,"
        + " classifying the area by its primary commuting flow.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Primary RUCA",
                "cellDataType": "text",
                "maxWidth": 130,
            }
        },
    )
    primary_ruca_description: str | None = Field(
        default=None,
        description="Description of the primary RUCA code.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Primary RUCA description",
                "cellDataType": "text",
            }
        },
    )
    secondary_ruca: str | None = Field(
        default=None,
        description="Secondary RUCA code, the primary code optionally extended"
        + " with a decimal sub-code for a secondary commuting flow.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Secondary RUCA",
                "cellDataType": "text",
                "maxWidth": 140,
            }
        },
    )
    secondary_ruca_description: str | None = Field(
        default=None,
        description="Description of the secondary RUCA code.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Secondary RUCA description",
                "cellDataType": "text",
            }
        },
    )
    population: int | None = Field(
        default=None,
        description="Population of the area in the vintage year, for the tract"
        + " tables that publish it. Not published for the ZIP tables.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Population",
                "cellDataType": "number",
                "maxWidth": 140,
            }
        },
    )
    land_area: float | None = Field(
        default=None,
        description="Land area of the tract in square miles, for the tract"
        + " tables that publish it. Not published for the 2000 or ZIP tables.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Land area (sq mi)",
                "cellDataType": "number",
                "maxWidth": 150,
            }
        },
    )
    population_density: float | None = Field(
        default=None,
        description="Population per square mile of the tract, for the 2020 and"
        + " 2010 tract tables that publish it.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Population density (per sq mi)",
                "cellDataType": "number",
                "maxWidth": 200,
            }
        },
    )


class RuralUrbanCommutingAreaCodesFetcher(
    Fetcher[
        RuralUrbanCommutingAreaCodesQueryParams,
        list[RuralUrbanCommutingAreaCodesData],
    ]
):
    """Fetch USDA ERS Rural-Urban Commuting Area Codes."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> RuralUrbanCommutingAreaCodesQueryParams:
        """Transform the query params."""
        return RuralUrbanCommutingAreaCodesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: RuralUrbanCommutingAreaCodesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download and parse the selected vintage's file for the state filter."""
        from openbb_government_us.usda.utils import (
            ers_rural_urban_commuting_area_codes,
        )

        return await ers_rural_urban_commuting_area_codes.afetch_table(
            query.table, query.state
        )

    @staticmethod
    def transform_data(
        query: RuralUrbanCommutingAreaCodesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[RuralUrbanCommutingAreaCodesData]:
        """Order the lookup records by identifier and validate the row schema."""
        if not data:
            raise EmptyDataError("No records match the given filters.")
        ordered = sorted(data, key=lambda record: record.get("area_fips") or "")
        return [
            RuralUrbanCommutingAreaCodesData.model_validate(
                {key: record.get(key) for key in SERVED_FIELDS}
            )
            for record in ordered
        ]
