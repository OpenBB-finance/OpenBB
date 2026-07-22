"""Food Dollar Series Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.ers_food_dollar_series import (
    COMPONENT_COLUMNS,
    FOOD_DOLLAR_FILES,
    SERIES_COMPONENTS,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

Series = Literal["nominal", "real"]
Units = Literal["share", "level"]


class FoodDollarSeriesQueryParams(QueryParams):
    """Food Dollar Series Query Parameters.

    Source: https://www.ers.usda.gov/data-products/food-dollar-series
    """

    __json_schema_extra__ = {
        "series": {
            "x-widget_config": {
                "label": "Series",
                "multiSelect": False,
                "multiple": False,
                "value": "nominal",
                "options": [
                    {"label": "Nominal (current dollars)", "value": "nominal"},
                    {"label": "Real (2017 dollars)", "value": "real"},
                ],
            },
        },
        "units": {
            "x-widget_config": {
                "label": "Units",
                "multiSelect": False,
                "multiple": False,
                "value": "share",
                "options": [
                    {"label": "Share (cents per food dollar)", "value": "share"},
                    {"label": "Level (million dollars)", "value": "level"},
                ],
            },
        },
        "component": {
            "x-widget_config": {
                "label": "Primary factor",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "value": "total",
                "optionsEndpoint": f"{api_prefix}/usda/food_dollar_components",
                "optionsParams": {"series": "$series"},
                "style": {"popupWidth": 280},
            },
        },
        "table": {
            "x-widget_config": {
                "label": "Table",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "value": 1,
                "optionsEndpoint": f"{api_prefix}/usda/food_dollar_tables",
                "optionsParams": {"series": "$series"},
                "style": {"popupWidth": 420},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    series: Series = Field(
        default="nominal",
        description="Series to retrieve, selecting the source dataset. 'nominal'"
        + " is current-year dollars with the full primary-factor decomposition"
        + " and all 22 tables; 'real' is inflation-adjusted 2017 dollars with"
        + " only the six food-dollar aggregate tables.",
    )
    units: Units = Field(
        default="share",
        description="Units of the cell values. 'share' is cents per domestic"
        + " food dollar; 'level' is millions of dollars. Orthogonal to series.",
    )
    component: str = Field(
        default="total",
        description="Primary-factor component that fills the cells. Valid"
        + " components depend on series; for nominal:\n    "
        + ", ".join(SERIES_COMPONENTS["nominal"])
        + "\nfor real:\n    "
        + ", ".join(SERIES_COMPONENTS["real"])
        + "\n'total' is populated for every year and category.",
    )
    table: int = Field(
        default=1,
        description="Food-dollar table to retrieve, by table number. Nominal"
        + " offers tables 1-22 (six dollar aggregates and 16 commodity groups);"
        + " real offers only tables 1-6.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from the series' first year.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("series", mode="before", check_fields=False)
    @classmethod
    def _validate_series(cls, v):
        """Validate series."""
        if not v:
            return "nominal"
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip().lower()

    @field_validator("units", mode="before", check_fields=False)
    @classmethod
    def _validate_units(cls, v):
        """Validate units."""
        if not v:
            return "share"
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip().lower()

    @field_validator("component", mode="before", check_fields=False)
    @classmethod
    def _validate_component(cls, v):
        """Validate component."""
        if not v:
            return "total"
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip().lower()

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if v is None or v == "":
            return 1
        value = v[0] if isinstance(v, (list, tuple)) else v
        try:
            return int(str(value).strip())
        except ValueError as error:
            raise OpenBBError(
                f"Invalid table: {value}. Expected a table number."
            ) from (error)

    @model_validator(mode="after")
    def _validate_series_scope(self):
        """Validate that component and table belong to the selected series."""
        components = SERIES_COMPONENTS[self.series]
        if self.component not in components:
            raise OpenBBError(
                f"Invalid component '{self.component}' for series '{self.series}'."
                " Valid components are: " + ", ".join(components)
            )
        tables = FOOD_DOLLAR_FILES[self.series]["tables"]
        if self.table not in tables:
            raise OpenBBError(
                f"Invalid table {self.table} for series '{self.series}'."
                f" Valid tables are {tables[0]}-{tables[-1]}."
            )
        return self


class FoodDollarSeriesData(NullTokenMixin, Data):
    """Food Dollar Series Data.

    One selected food-dollar table pivoted to a wide layout: the marketing-bill
    industry groups stay in the rows while the years spread into value columns,
    each cell holding the chosen primary-factor component in the chosen units.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Food Dollar Series",
                "$.description": "The marketing-bill breakdown of the U.S. food"
                " dollar into the industry groups and primary factors that supply"
                " it, in nominal and real terms, published by the USDA Economic"
                " Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    industry_group: str = Field(
        description="Marketing-bill industry group or aggregate, as published,"
        + " e.g. 'Farm production', 'Foodservices', or 'Farm share'.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Industry group", "pinned": "left"}
        },
    )


class FoodDollarSeriesFetcher(
    Fetcher[
        FoodDollarSeriesQueryParams,
        list[FoodDollarSeriesData],
    ]
):
    """Fetch USDA ERS Food Dollar Series."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FoodDollarSeriesQueryParams:
        """Transform the query params."""
        return FoodDollarSeriesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FoodDollarSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected series' tidy CSV rows."""
        from openbb_government_us.usda.utils import ers_food_dollar_series

        return await ers_food_dollar_series.afetch_series(query.series)

    @staticmethod
    def transform_data(
        query: FoodDollarSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FoodDollarSeriesData]:
        """Pivot the selected table's industry groups against the years."""
        entry = FOOD_DOLLAR_FILES[query.series]
        units_label = entry["units"][query.units]
        component_column = COMPONENT_COLUMNS[query.component]
        pivoted: dict[int, dict] = {}
        for record in data:
            if record["table_num"] != query.table:
                continue
            if record["units"] != units_label:
                continue
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            row = pivoted.get(record["category_num"])
            if row is None:
                row = {
                    "_category_num": record["category_num"],
                    "industry_group": record["industry_group"],
                }
                pivoted[record["category_num"]] = row
            row[str(year)] = record[component_column]
        results: list[dict] = []
        for row in sorted(pivoted.values(), key=lambda item: item["_category_num"]):
            year_keys = [key for key in row if key.isdigit()]
            if not any(row[key] is not None for key in year_keys):
                continue
            results.append(row)
        if not results:
            raise EmptyDataError("No records match the given filters.")
        validated: list[FoodDollarSeriesData] = []
        for row in results:
            dimensions = {"industry_group": row["industry_group"]}
            years = {
                key: row[key]
                for key in sorted((k for k in row if k.isdigit()), key=int)
            }
            validated.append(
                FoodDollarSeriesData.model_validate({**dimensions, **years})
            )
        return validated
