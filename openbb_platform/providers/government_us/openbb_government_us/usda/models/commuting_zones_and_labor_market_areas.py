"""Commuting Zones and Labor Market Areas Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_commuting_zones_and_labor_market_areas import (
    DEFAULT_VINTAGE,
    STATE_NAMES,
    VINTAGE_FILES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

_STATE_LOOKUP = {name.casefold(): name for name in STATE_NAMES}


class CommutingZonesAndLaborMarketAreasQueryParams(QueryParams):
    """Commuting Zones and Labor Market Areas Query Parameters.

    Source: https://www.ers.usda.gov/data-products/commuting-zones-and-labor-market-areas
    """

    __json_schema_extra__ = {
        "vintage": {
            "x-widget_config": {
                "label": "Vintage",
                "value": DEFAULT_VINTAGE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": config["label"], "value": key}
                    for key, config in VINTAGE_FILES.items()
                ],
                "style": {"popupWidth": 420},
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "multiSelect": False,
                "multiple": False,
                "options": [{"label": name, "value": name} for name in STATE_NAMES],
                "style": {"popupWidth": 260},
            },
        },
    }

    vintage: str = Field(
        default=DEFAULT_VINTAGE,
        description="Classification vintage to retrieve. Each vintage is a"
        + " separate county lookup published for a base year; the county rows"
        + " and their commuting-zone codes replace one another across vintages"
        + " rather than forming a time series. Valid vintages are:\n    "
        + ", ".join(VINTAGE_FILES)
        + "\n",
    )
    state: str | None = Field(
        default=None,
        description="State to retrieve, by full name, e.g. 'Texas'."
        + " If None, all states are returned. Puerto Rico is published for the"
        + " 2020 and preliminary 2020 vintages only.",
    )

    @field_validator("vintage", mode="before", check_fields=False)
    @classmethod
    def _validate_vintage(cls, v):
        """Validate vintage."""
        if not v:
            return DEFAULT_VINTAGE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in VINTAGE_FILES:
            raise OpenBBError(
                f"Invalid vintage: {value}. Valid vintages are: "
                + ", ".join(VINTAGE_FILES)
            )
        return value

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate state."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        canonical = _STATE_LOOKUP.get(value.casefold())
        if canonical is None:
            raise OpenBBError(
                f"Invalid state: {value}. Valid states are: " + ", ".join(STATE_NAMES)
            )
        return canonical


class CommutingZonesAndLaborMarketAreasData(NullTokenMixin, Data):
    """Commuting Zones and Labor Market Areas Data.

    One row per county for the selected vintage: the county's FIPS code, state,
    and name, its primary commuting-zone code and name, and its commuter
    containment. Codes published only for the older vintages are hidden by
    default.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Commuting Zones and Labor Market Areas",
                "$.description": "County-level commuting zone and labor market"
                " area classifications for the 2020, preliminary 2020, 2000, and"
                " 1980/1990 vintages, published by the USDA Economic Research"
                " Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    fips: str = Field(
        description="Five-digit county FIPS code.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "County FIPS",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 120,
            }
        },
    )
    state: str | None = Field(
        default=None,
        description="Full state name, derived from the county FIPS code.",
        json_schema_extra={
            "x-widget_config": {"headerName": "State", "pinned": "left"}
        },
    )
    county_name: str | None = Field(
        default=None,
        description="County name, as published.",
        json_schema_extra={
            "x-widget_config": {"headerName": "County", "pinned": "left"}
        },
    )
    commuting_zone: str | None = Field(
        default=None,
        description="Primary commuting-zone identifier of the vintage: CZ2020"
        + " for 2020, the preliminary CZ for preliminary 2020, the 2000"
        + " commuting-zone id for 2000, and CZ90 for 1980/1990.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Commuting Zone",
                "cellDataType": "text",
            }
        },
    )
    commuting_zone_name: str | None = Field(
        default=None,
        description="Commuting-zone name for the 2020 vintage, or the name of"
        + " the largest place in the commuting zone for the 1980/1990 vintage.",
        json_schema_extra={"x-widget_config": {"headerName": "Commuting Zone Name"}},
    )
    cz_containment: float | None = Field(
        default=None,
        description="Percent of the county's commuters contained within its"
        + " commuting zone. 2020 vintage only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Containment (%)",
                "cellDataType": "number",
            }
        },
    )
    cz_avg_containment: float | None = Field(
        default=None,
        description="Average commuter containment across the counties of the"
        + " commuting zone, in percent. 2020 vintage only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Avg. Containment (%)",
                "cellDataType": "number",
            }
        },
    )
    cz_1990: str | None = Field(
        default=None,
        description="1990 commuting-zone identifier of the county. 2000 vintage"
        + " only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Commuting Zone (1990)",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )
    cz_1980: str | None = Field(
        default=None,
        description="1980 commuting-zone identifier of the county, published in"
        + " the 2000 and 1980/1990 vintages.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Commuting Zone (1980)",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )
    metro_area: str | None = Field(
        default=None,
        description="2003 metropolitan or micropolitan area of the county, as"
        + " published. 2000 vintage only.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Metropolitan Area (2003)", "hide": True}
        },
    )
    county_population: int | None = Field(
        default=None,
        description="County population: the 2000 census count for the 2000"
        + " vintage, or the 1990 census count for the 1980/1990 vintage.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "County Population",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    commuting_zone_population: int | None = Field(
        default=None,
        description="2000 census population of the commuting zone. 2000 vintage"
        + " only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Commuting Zone Population",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    distance: float | None = Field(
        default=None,
        description="Cluster distance metric of the county's assignment to its"
        + " commuting zone. 1980/1990 vintage only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Distance",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    beale_code: str | None = Field(
        default=None,
        description="1993 rural-urban continuum (Beale) code of the county."
        + " 1980/1990 vintage only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Beale Code (1993)",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )
    msa_code: str | None = Field(
        default=None,
        description="1993 metropolitan statistical area code of the county."
        + " 1980/1990 vintage only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "MSA Code (1993)",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )
    msa_name: str | None = Field(
        default=None,
        description="1993 metropolitan statistical area name of the county."
        + " 1980/1990 vintage only.",
        json_schema_extra={
            "x-widget_config": {"headerName": "MSA Name (1993)", "hide": True}
        },
    )
    place_code: str | None = Field(
        default=None,
        description="State place code of the largest place in the commuting"
        + " zone. 1980/1990 vintage only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State Place Code",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )


class CommutingZonesAndLaborMarketAreasFetcher(
    Fetcher[
        CommutingZonesAndLaborMarketAreasQueryParams,
        list[CommutingZonesAndLaborMarketAreasData],
    ]
):
    """Fetch USDA ERS Commuting Zones and Labor Market Areas."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CommutingZonesAndLaborMarketAreasQueryParams:
        """Transform the query params."""
        return CommutingZonesAndLaborMarketAreasQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CommutingZonesAndLaborMarketAreasQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected vintage's county records."""
        from openbb_government_us.usda.utils import (
            ers_commuting_zones_and_labor_market_areas,
        )

        return await ers_commuting_zones_and_labor_market_areas.afetch_vintage(
            query.vintage
        )

    @staticmethod
    def transform_data(
        query: CommutingZonesAndLaborMarketAreasQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CommutingZonesAndLaborMarketAreasData]:
        """Filter the county lookup by state and order it by FIPS code."""
        rows = [
            record
            for record in data
            if query.state is None
            or (record["state"] or "").casefold() == query.state.casefold()
        ]
        if not rows:
            raise EmptyDataError("No records match the given filters.")
        rows.sort(key=lambda record: record["fips"])
        return [
            CommutingZonesAndLaborMarketAreasData.model_validate(record)
            for record in rows
        ]
