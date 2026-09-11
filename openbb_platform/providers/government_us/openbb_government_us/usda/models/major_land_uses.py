"""Major Land Uses Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_major_land_uses import (
    CROPLAND_VARIABLES,
    GEOGRAPHIES,
    LAND_USE_CATEGORIES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

Table = Literal["land_use", "cropland_used_for_crops"]

GEOGRAPHY_LOOKUP = {name.casefold(): name for name in GEOGRAPHIES}


class MajorLandUsesQueryParams(QueryParams):
    """Major Land Uses Query Parameters.

    Source: https://www.ers.usda.gov/data-products/major-land-uses
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "options": [
                    {"label": "Land use by region & State", "value": "land_use"},
                    {
                        "label": "Cropland used for crops (annual)",
                        "value": "cropland_used_for_crops",
                    },
                ],
            },
        },
        "land_use": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Land use",
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": slug.replace("_", " ").capitalize(), "value": slug}
                    for slug in sorted(LAND_USE_CATEGORIES)
                ],
                "style": {"popupWidth": 340},
            },
        },
        "geography": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Geography",
                "multiSelect": False,
                "multiple": False,
                "value": "48 States",
                "options": [{"label": name, "value": name} for name in GEOGRAPHIES],
                "style": {"popupWidth": 300},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: Table = Field(
        default="land_use",
        description="Dataset to retrieve. 'land_use' is land by major use,"
        + " region, and State for Census of Agriculture benchmark years"
        + " 1945-2017. 'cropland_used_for_crops' is the national annual"
        + " cropland-used-for-crops series, 1910 to the current year.",
    )
    land_use: str | None = Field(
        default=None,
        description="Land use category(ies) to retrieve, as a comma-separated"
        + " list. Only applies when table='land_use'; if None, all categories"
        + " are returned. Valid categories are:\n    "
        + ", ".join(sorted(LAND_USE_CATEGORIES))
        + "\n",
    )
    geography: str | None = Field(
        default=None,
        description="Geography(ies) to retrieve, as a comma-separated list of"
        + " State names, farm production region names, '48 States', or"
        + " 'U.S. total'. Only applies when table='land_use'; if None, all"
        + " geographies are returned. Valid geographies are:\n    "
        + ", ".join(GEOGRAPHIES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " None returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("land_use", mode="before", check_fields=False)
    @classmethod
    def _validate_land_use(cls, v):
        """Validate land_use."""
        if not v:
            return None
        items = v.split(",") if isinstance(v, str) else list(v)
        items = [item.strip() for item in items if item and item.strip()]
        if not items:
            return None
        unknown = [item for item in items if item not in LAND_USE_CATEGORIES]
        if unknown:
            raise OpenBBError(
                f"Invalid land_use value(s): {', '.join(unknown)}."
                + " Valid categories are: "
                + ", ".join(sorted(LAND_USE_CATEGORIES))
            )
        return ",".join(items)

    @field_validator("geography", mode="before", check_fields=False)
    @classmethod
    def _validate_geography(cls, v):
        """Validate geography."""
        if not v:
            return None
        items = v.split(",") if isinstance(v, str) else list(v)
        items = [item.strip() for item in items if item and item.strip()]
        if not items:
            return None
        unknown = [item for item in items if item.casefold() not in GEOGRAPHY_LOOKUP]
        if unknown:
            raise OpenBBError(
                f"Invalid geography value(s): {', '.join(unknown)}."
                + " Valid geographies are: "
                + ", ".join(GEOGRAPHIES)
            )
        return ",".join(GEOGRAPHY_LOOKUP[item.casefold()] for item in items)


class MajorLandUsesData(NullTokenMixin, Data):
    """Major Land Uses Data.

    Land area by major use in the United States, from the USDA ERS Major
    Land Uses series.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Major Land Uses",
                "$.description": "Land area by major use for the United States, its regions, and States, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    geography: str = Field(
        description="Geography of the observation: a State name, a farm"
        + " production region name, '48 States', or 'U.S. total' for the"
        + " land_use table; 'United States' for the annual table.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Geography", "pinned": "left"}
        },
    )
    land_use: str = Field(
        description="Land use category of the observation. For the land_use"
        + " table, one of the 16 category slugs; for the annual table, one"
        + " of: "
        + ", ".join(CROPLAND_VARIABLES)
        + ".",
        json_schema_extra={
            "x-widget_config": {"headerName": "Land use", "pinned": "left"}
        },
    )
    region: str | None = Field(
        default=None,
        description="Farm production region the State belongs to."
        + " None for regional and national aggregate rows.",
        json_schema_extra={"x-widget_config": {"headerName": "Region", "hide": True}},
    )


class MajorLandUsesFetcher(
    Fetcher[
        MajorLandUsesQueryParams,
        list[MajorLandUsesData],
    ]
):
    """Fetch USDA ERS Major Land Uses."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> MajorLandUsesQueryParams:
        """Transform the query params."""
        return MajorLandUsesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: MajorLandUsesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's tidy records."""
        from openbb_government_us.usda.utils import ers_major_land_uses

        if query.table == "cropland_used_for_crops":
            return await ers_major_land_uses.afetch_cropland_used_for_crops()
        return await ers_major_land_uses.afetch_land_use()

    @staticmethod
    def transform_data(
        query: MajorLandUsesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[MajorLandUsesData]:
        """Transform the data."""
        selected_uses = (
            set(query.land_use.split(","))
            if query.land_use is not None and query.table == "land_use"
            else None
        )
        selected_geographies = (
            set(query.geography.split(","))
            if query.geography is not None and query.table == "land_use"
            else None
        )
        pivoted: dict[tuple, dict] = {}
        for order, record in enumerate(data):
            if query.start_year is not None and record["year"] < query.start_year:
                continue
            if query.end_year is not None and record["year"] > query.end_year:
                continue
            if selected_uses is not None and record["land_use"] not in selected_uses:
                continue
            if (
                selected_geographies is not None
                and record["geography"] not in selected_geographies
            ):
                continue
            key = (record["geography"], record["land_use"])
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_order": order,
                    "geography": record["geography"],
                    "land_use": record["land_use"],
                    "region": record.get("region"),
                }
                pivoted[key] = row
            row[str(record["year"])] = record["value"]
        results = sorted(pivoted.values(), key=lambda row: row["_order"])
        return [
            MajorLandUsesData.model_validate(
                {k: v for k, v in row.items() if k != "_order"}
            )
            for row in results
        ]
