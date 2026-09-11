"""USDA ERS Food-at-Home Monthly Area Prices Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_food_at_home_monthly_area_prices import (
    AREA_FIELDS,
    AREAS,
    DEFAULT_GROUP,
    DEFAULT_ITEM,
    DEFAULT_MEASURE,
    DEFAULT_TABLE,
    EFPG,
    FMAP_TABLES,
    GROUPS,
    MEASURES,
    resolve_measure,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

TABLE_OPTIONS = [
    {"label": config["label"], "value": key} for key, config in FMAP_TABLES.items()
]

GROUP_OPTIONS = [{"label": group, "value": group} for group in GROUPS]


def _area(header: str) -> dict:
    """Build a numeric area column config for one area field."""
    return {"x-widget_config": {"headerName": header, "cellDataType": "number"}}


class FoodAtHomeMonthlyAreaPricesQueryParams(QueryParams):
    """USDA ERS Food-at-Home Monthly Area Prices Query Parameters.

    Source: https://www.ers.usda.gov/data-products/food-at-home-monthly-area-prices
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": TABLE_OPTIONS,
                "style": {"popupWidth": 320},
            },
        },
        "group": {
            "x-widget_config": {
                "label": "Food group",
                "value": DEFAULT_GROUP,
                "multiSelect": False,
                "multiple": False,
                "options": GROUP_OPTIONS,
                "style": {"popupWidth": 320},
            },
        },
        "item": {
            "x-widget_config": {
                "label": "Food item",
                "type": "endpoint",
                "value": DEFAULT_ITEM,
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/fmap_food_items",
                "optionsParams": {"group": "$group"},
                "style": {"popupWidth": 420},
            },
        },
        "measure": {
            "x-widget_config": {
                "label": "Measure",
                "type": "endpoint",
                "value": DEFAULT_MEASURE,
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/fmap_measures",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 400},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Table to retrieve. The main table carries the nine F-MAP"
        + " price, purchase, and store measures for 2012-2018; the supplemental"
        + " table carries six alternative price-index formulas for 2016-2018."
        + " Valid tables are:\n    "
        + ", ".join(FMAP_TABLES)
        + "\n",
    )
    group: str = Field(
        default=DEFAULT_GROUP,
        description="Tier-1 food group that narrows the food-item options."
        + " Ignored once an item is chosen. Valid groups are:\n    "
        + ", ".join(GROUPS)
        + "\n",
    )
    item: str = Field(
        default=DEFAULT_ITEM,
        description="ERS Food Purchase Group (EFPG) code of the food item whose"
        + " monthly area prices are spread across the area columns, e.g. '40000'"
        + " for whole milk.",
    )
    measure: str = Field(
        default=DEFAULT_MEASURE,
        description="Measure spread into the 15 area columns. Only measures the"
        + " selected table publishes are valid; an unavailable measure falls"
        + " back to the table's default. Valid measures are:\n    "
        + ", ".join(MEASURES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from the first year of the table.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the last year of the table.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in FMAP_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: " + ", ".join(FMAP_TABLES)
            )
        return table

    @field_validator("group", mode="before", check_fields=False)
    @classmethod
    def _validate_group(cls, v):
        """Validate group."""
        if not v:
            return DEFAULT_GROUP
        group = v.strip() if isinstance(v, str) else v
        if group not in GROUPS:
            raise OpenBBError(
                f"Invalid group: {group}. Valid groups are: " + ", ".join(GROUPS)
            )
        return group

    @field_validator("item", mode="before", check_fields=False)
    @classmethod
    def _validate_item(cls, v):
        """Validate item."""
        if not v:
            return DEFAULT_ITEM
        value = v[0] if isinstance(v, (list, tuple)) else v
        item = str(value).strip()
        if item not in EFPG:
            raise OpenBBError(
                f"Invalid item: {item}. Valid items are EFPG codes: " + ", ".join(EFPG)
            )
        return item

    @field_validator("measure", mode="before", check_fields=False)
    @classmethod
    def _validate_measure(cls, v):
        """Validate measure."""
        if not v:
            return DEFAULT_MEASURE
        measure = v.strip() if isinstance(v, str) else v
        if measure not in MEASURES:
            raise OpenBBError(
                f"Invalid measure: {measure}. Valid measures are: "
                + ", ".join(MEASURES)
            )
        return measure


class FoodAtHomeMonthlyAreaPricesData(NullTokenMixin, Data):
    """USDA ERS Food-at-Home Monthly Area Prices Data.

    One selected food item and measure pivoted to a wide layout: the monthly
    dates stay in the rows while the 15 U.S. areas spread into value columns.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Food-at-Home Monthly Area Prices",
                "$.description": "Monthly food-at-home unit values, purchases,"
                " store counts, and price indexes for a selected food item and"
                " measure, spread across the national, four Census-region, and"
                " ten metropolitan areas, published by the USDA Economic"
                " Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    date: dateType = Field(
        description="First day of the observation month.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Date",
                "cellDataType": "date",
                "pinned": "left",
                "maxWidth": 120,
            }
        },
    )
    national: float | None = Field(
        default=None,
        description="Selected measure for the United States.",
        json_schema_extra=_area("National"),
    )
    northeast: float | None = Field(
        default=None,
        description="Selected measure for Census Region 1: Northeast.",
        json_schema_extra=_area("Northeast"),
    )
    midwest: float | None = Field(
        default=None,
        description="Selected measure for Census Region 2: Midwest.",
        json_schema_extra=_area("Midwest"),
    )
    south: float | None = Field(
        default=None,
        description="Selected measure for Census Region 3: South.",
        json_schema_extra=_area("South"),
    )
    west: float | None = Field(
        default=None,
        description="Selected measure for Census Region 4: West.",
        json_schema_extra=_area("West"),
    )
    atlanta: float | None = Field(
        default=None,
        description="Selected measure for the Atlanta, GA metro area.",
        json_schema_extra=_area("Atlanta, GA"),
    )
    boston: float | None = Field(
        default=None,
        description="Selected measure for the Boston, MA-NH metro area.",
        json_schema_extra=_area("Boston, MA-NH"),
    )
    chicago: float | None = Field(
        default=None,
        description="Selected measure for the Chicago, IL-IN-WI metro area.",
        json_schema_extra=_area("Chicago, IL-IN-WI"),
    )
    dallas: float | None = Field(
        default=None,
        description="Selected measure for the Dallas-Fort Worth, TX metro area.",
        json_schema_extra=_area("Dallas-Fort Worth, TX"),
    )
    detroit: float | None = Field(
        default=None,
        description="Selected measure for the Detroit, MI metro area.",
        json_schema_extra=_area("Detroit, MI"),
    )
    houston: float | None = Field(
        default=None,
        description="Selected measure for the Houston, TX metro area.",
        json_schema_extra=_area("Houston, TX"),
    )
    los_angeles: float | None = Field(
        default=None,
        description="Selected measure for the Los Angeles, CA metro area.",
        json_schema_extra=_area("Los Angeles, CA"),
    )
    miami: float | None = Field(
        default=None,
        description="Selected measure for the Miami, FL metro area.",
        json_schema_extra=_area("Miami, FL"),
    )
    new_york: float | None = Field(
        default=None,
        description="Selected measure for the New York, NY-NJ-PA metro area.",
        json_schema_extra=_area("New York, NY-NJ-PA"),
    )
    philadelphia: float | None = Field(
        default=None,
        description="Selected measure for the Philadelphia, PA-NJ-DE-MD metro"
        + " area.",
        json_schema_extra=_area("Philadelphia, PA-NJ-DE-MD"),
    )


class FoodAtHomeMonthlyAreaPricesFetcher(
    Fetcher[
        FoodAtHomeMonthlyAreaPricesQueryParams,
        list[FoodAtHomeMonthlyAreaPricesData],
    ]
):
    """Fetch USDA ERS Food-at-Home Monthly Area Prices."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FoodAtHomeMonthlyAreaPricesQueryParams:
        """Transform the query params."""
        return FoodAtHomeMonthlyAreaPricesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FoodAtHomeMonthlyAreaPricesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract one item and measure's monthly area observations."""
        from openbb_government_us.usda.utils import (
            ers_food_at_home_monthly_area_prices as fmap,
        )

        measure = resolve_measure(query.table, query.measure)
        source = MEASURES[measure]["source"]
        return await fmap.afetch_series(query.table, query.item, source)

    @staticmethod
    def transform_data(
        query: FoodAtHomeMonthlyAreaPricesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FoodAtHomeMonthlyAreaPricesData]:
        """Pivot the long observations into wide monthly rows by area."""
        pivoted: dict[tuple[int, int], dict] = {}
        for record in data:
            year = record["year"]
            month = record["month"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            key = (year, month)
            row = pivoted.get(key)
            if row is None:
                row = {"date": dateType(year, month, 1)}
                for field in AREA_FIELDS:
                    row[field] = None
                pivoted[key] = row
            area = AREAS.get(record["area_code"])
            if area is not None:
                row[area[0]] = record["value"]
        return [
            FoodAtHomeMonthlyAreaPricesData.model_validate(pivoted[key])
            for key in sorted(pivoted)
        ]
