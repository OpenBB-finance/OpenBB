"""USDA ERS Food Availability (Per Capita) Data System Model."""

from collections import OrderedDict
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.ers_food_availability_per_capita_data_system import (
    CATALOG,
    DATA_SYSTEM_LABELS,
    DATA_SYSTEMS,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_DATA_SYSTEM = "food_availability"

SYSTEM_DEFAULT_GROUP: dict[str, str] = {
    "food_availability": "eggs",
    "loss_adjusted": "fruit",
    "nutrient": "totals",
}

DATA_SYSTEM_OPTIONS = [
    {"label": DATA_SYSTEM_LABELS[system], "value": system} for system in DATA_SYSTEMS
]


class FoodAvailabilityPerCapitaDataSystemQueryParams(QueryParams):
    """USDA ERS Food Availability (Per Capita) Data System Query Parameters.

    Source: https://www.ers.usda.gov/data-products/food-availability-per-capita-data-system
    """

    __json_schema_extra__ = {
        "data_system": {
            "x-widget_config": {
                "label": "Data system",
                "value": DEFAULT_DATA_SYSTEM,
                "multiSelect": False,
                "multiple": False,
                "options": DATA_SYSTEM_OPTIONS,
                "style": {"popupWidth": 320},
            },
        },
        "food_group": {
            "x-widget_config": {
                "label": "Food group",
                "type": "endpoint",
                "value": "eggs",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/food_availability_groups",
                "optionsParams": {"data_system": "$data_system"},
                "style": {"popupWidth": 360},
            },
        },
        "commodity": {
            "x-widget_config": {
                "label": "Commodity",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/food_availability_commodities",
                "optionsParams": {
                    "data_system": "$data_system",
                    "food_group": "$food_group",
                },
                "style": {"popupWidth": 420},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    data_system: str = Field(
        default=DEFAULT_DATA_SYSTEM,
        description="Data system to retrieve. Each selection downloads one"
        + " cached file, pivoted to a wide layout with the measures spread into"
        + " columns and the years in the rows. Valid data systems are:\n    "
        + ", ".join(DATA_SYSTEMS)
        + "\n",
    )
    food_group: str | None = Field(
        default=None,
        description="Food group file within the data system, as a slug. The"
        + " same slug can appear under more than one data system. If None, the"
        + " data system's default file is used.",
    )
    commodity: str | None = Field(
        default=None,
        description="Commodity block within the file, as its published name."
        + " If None, the file's first block is used.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("data_system", mode="before", check_fields=False)
    @classmethod
    def _validate_data_system(cls, v):
        """Validate data_system."""
        if not v:
            return DEFAULT_DATA_SYSTEM
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in DATA_SYSTEMS:
            raise OpenBBError(
                f"Invalid data system: {value}. Valid data systems are: "
                + ", ".join(DATA_SYSTEMS)
            )
        return value

    @field_validator("food_group", "commodity", mode="before", check_fields=False)
    @classmethod
    def _normalize_optional(cls, v):
        """Normalize an optional string filter to a stripped string or None."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip() or None

    @model_validator(mode="after")
    def _resolve_food_group(self):
        """Resolve the food group to the system default and validate it."""
        if self.food_group is None:
            self.food_group = SYSTEM_DEFAULT_GROUP[self.data_system]
        elif self.food_group not in CATALOG[self.data_system]:
            raise OpenBBError(
                f"Invalid food group '{self.food_group}' for data system"
                f" '{self.data_system}'. Valid food groups are: "
                + ", ".join(CATALOG[self.data_system])
            )
        return self


class FoodAvailabilityPerCapitaDataSystemData(NullTokenMixin, Data):
    """USDA ERS Food Availability (Per Capita) Data System Data.

    One selected file's commodity block, pivoted to a wide layout: the years
    stay in the rows while the measures spread into value columns, whose set is
    dynamic and varies by file and block. Amounts are the raw published values.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Food Availability (Per Capita)",
                "$.description": "Per capita food supply, loss-adjusted"
                " availability, and nutrient availability of the U.S. food"
                " supply, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: int = Field(
        description="Calendar year of the observation.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "number",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )


class FoodAvailabilityPerCapitaDataSystemFetcher(
    Fetcher[
        FoodAvailabilityPerCapitaDataSystemQueryParams,
        list[FoodAvailabilityPerCapitaDataSystemData],
    ]
):
    """Fetch USDA ERS Food Availability (Per Capita) Data System."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FoodAvailabilityPerCapitaDataSystemQueryParams:
        """Transform the query params."""
        return FoodAvailabilityPerCapitaDataSystemQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FoodAvailabilityPerCapitaDataSystemQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected file's long-format records."""
        from openbb_government_us.usda.utils import (
            ers_food_availability_per_capita_data_system as ers,
        )

        food_group = query.food_group or SYSTEM_DEFAULT_GROUP[query.data_system]
        return await ers.afetch_records(query.data_system, food_group)

    @staticmethod
    def transform_data(
        query: FoodAvailabilityPerCapitaDataSystemQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FoodAvailabilityPerCapitaDataSystemData]:
        """Pivot the selected block's measures into columns, oldest year first."""
        block = query.commodity or (data[0]["block"] if data else None)
        column_order: OrderedDict[str, None] = OrderedDict()
        populated: set[str] = set()
        by_year: dict[int, dict] = {}
        for record in data:
            if record["block"] != block:
                continue
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            attribute = record["attribute"]
            value = record["value"]
            column_order.setdefault(attribute, None)
            if value is not None:
                populated.add(attribute)
            row = by_year.get(year)
            if row is None:
                row = {"year": year}
                by_year[year] = row
            row[attribute] = value
        columns = [name for name in column_order if name in populated]
        if not by_year:
            raise EmptyDataError("No records match the given filters.")
        results: list[FoodAvailabilityPerCapitaDataSystemData] = []
        for year in sorted(by_year):
            source = by_year[year]
            row = {"year": year}
            for name in columns:
                row[name] = source.get(name)
            results.append(FoodAvailabilityPerCapitaDataSystemData.model_validate(row))
        return results
