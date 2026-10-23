"""USDA ERS Food Consumption, Nutrient Intakes, and Diet Quality Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_food_consumption_nutrient_intakes_and_diet_quality import (
    DEFAULT_DEMOGRAPHIC,
    DEFAULT_STATISTIC,
    DEFAULT_TABLE,
    DEMOGRAPHICS,
    FOOD_SOURCES,
    RECOMMENDED_COLUMN_ORDER,
    RECOMMENDED_TABLE,
    SAMPLE_TABLE,
    STATISTIC_CHOICES,
    TABLE_FILES,
    TABLE_LABELS,
)
from openbb_government_us.utils.serializers import NullTokenMixin


def _cycle_year(cycle: str) -> int | None:
    """Return the starting calendar year of a survey-cycle label."""
    head = cycle[:4]
    return int(head) if head.isdigit() else None


def _source_index(food_source: str | None) -> int:
    """Return the published ordering rank of a food source."""
    if food_source in FOOD_SOURCES:
        return FOOD_SOURCES.index(food_source)
    return 0


def _finalize(
    rows: list[dict], column_order: list[str]
) -> list["FoodConsumptionNutrientIntakesAndDietQualityData"]:
    """Sort rows, spread the value columns rectangularly, and validate them."""
    rows.sort(key=lambda row: (row["_item_order"], row["_source_index"], row["_order"]))
    results: list[FoodConsumptionNutrientIntakesAndDietQualityData] = []
    for row in rows:
        source = row["food_source"]
        payload = {
            "item": f"{row['item']} — {source}" if source else row["item"],
            "food_source": source,
            "units": row["units"],
        }
        for column in column_order:
            payload[column] = row.get(column)
        results.append(
            FoodConsumptionNutrientIntakesAndDietQualityData.model_validate(payload)
        )
    return results


def _pivot_sample(
    query: "FoodConsumptionNutrientIntakesAndDietQualityQueryParams", data: list[dict]
):
    """Pivot Table 1 sample sizes into one row per subgroup, cycles as columns."""
    item_first: dict[str, int] = {}
    groups: dict[str, dict] = {}
    present: set[str] = set()
    for record in data:
        year = _cycle_year(record["cycle"])
        if year is None:
            continue
        if query.start_year is not None and year < query.start_year:
            continue
        if query.end_year is not None and year > query.end_year:
            continue
        subgroup = record["demographic"]
        item_first.setdefault(subgroup, record["order"])
        row = groups.get(subgroup)
        if row is None:
            row = {
                "_order": record["order"],
                "_source_index": 0,
                "item": subgroup,
                "food_source": None,
                "units": None,
            }
            groups[subgroup] = row
        row[record["cycle"]] = record["value"]
        present.add(record["cycle"])
    if not groups:
        raise EmptyDataError("No records match the given filters.")
    for row in groups.values():
        row["_item_order"] = item_first[row["item"]]
    column_order = sorted(present, key=lambda cycle: _cycle_year(cycle) or 0)
    return list(groups.values()), column_order


def _pivot_intake(
    query: "FoodConsumptionNutrientIntakesAndDietQualityQueryParams", data: list[dict]
):
    """Pivot an intake table (2-7) into one row per item and food source."""
    demographic = query.demographics
    statistic = STATISTIC_CHOICES[query.statistic]
    item_first: dict[str, int] = {}
    groups: dict[tuple, dict] = {}
    present: set[str] = set()
    for record in data:
        if record["demographics"] != demographic:
            continue
        if record["statistic"] != statistic:
            continue
        year = _cycle_year(record["cycle"])
        if year is None:
            continue
        if query.start_year is not None and year < query.start_year:
            continue
        if query.end_year is not None and year > query.end_year:
            continue
        item = record["item"]
        source = record["food_source"]
        item_first.setdefault(item, record["order"])
        key = (item, source)
        row = groups.get(key)
        if row is None:
            row = {
                "_order": record["order"],
                "_source_index": _source_index(source),
                "item": item,
                "food_source": source,
                "units": record["units"],
            }
            groups[key] = row
        if row["units"] is None and record["units"] is not None:
            row["units"] = record["units"]
        row[record["cycle"]] = record["value"]
        present.add(record["cycle"])
    if not groups:
        raise EmptyDataError("No records match the given filters.")
    for row in groups.values():
        row["_item_order"] = item_first[row["item"]]
    column_order = sorted(present, key=lambda cycle: _cycle_year(cycle) or 0)
    return list(groups.values()), column_order


def _pivot_recommended(
    query: "FoodConsumptionNutrientIntakesAndDietQualityQueryParams", data: list[dict]
):
    """Pivot Table 8 into one row per item, recommended and actual densities as columns."""
    item_first: dict[str, int] = {}
    groups: dict[str, dict] = {}
    for record in data:
        item = record["item"]
        item_first.setdefault(item, record["order"])
        row = groups.get(item)
        if row is None:
            row = {
                "_order": record["order"],
                "_source_index": 0,
                "item": item,
                "food_source": None,
                "units": None,
            }
            groups[item] = row
        row[record["column"]] = record["value"]
    if not groups:
        raise EmptyDataError("No records match the given filters.")
    for row in groups.values():
        row["_item_order"] = item_first[row["item"]]
    return list(groups.values()), list(RECOMMENDED_COLUMN_ORDER)


class FoodConsumptionNutrientIntakesAndDietQualityQueryParams(QueryParams):
    """USDA ERS Food Consumption, Nutrient Intakes, and Diet Quality Query Parameters.

    Source: https://www.ers.usda.gov/data-products/food-consumption-nutrient-intakes-and-diet-quality
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in TABLE_LABELS.items()
                ],
                "style": {"popupWidth": 460},
            },
        },
        "demographics": {
            "x-widget_config": {
                "label": "Demographic subgroup",
                "value": DEFAULT_DEMOGRAPHIC,
                "multiSelect": False,
                "multiple": False,
                "options": [{"label": label, "value": label} for label in DEMOGRAPHICS],
                "style": {"popupWidth": 360},
            },
        },
        "statistic": {
            "x-widget_config": {
                "label": "Statistic",
                "value": DEFAULT_STATISTIC,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in STATISTIC_CHOICES.items()
                ],
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Table to retrieve. Tables 1-7 are a 1977-2018 survey-cycle"
        + " series, pivoted with the survey cycles as columns; Table 8 pivots"
        + " the recommended and 2017-2018 actual densities into columns."
        + " Valid tables are:\n    "
        + ", ".join(TABLE_FILES)
        + "\n",
    )
    demographics: str = Field(
        default=DEFAULT_DEMOGRAPHIC,
        description="Population subgroup filter for the intake tables (2-7),"
        + " keeping the survey-cycle columns to a single subgroup. Ignored by"
        + " the sample-size table (1), which lists every subgroup, and by the"
        + " recommended-density table (8). Valid subgroups are:\n    "
        + ", ".join(DEMOGRAPHICS)
        + "\n",
    )
    statistic: str = Field(
        default=DEFAULT_STATISTIC,
        description="Statistic to spread across the survey-cycle columns for"
        + " the intake tables (2-7): the mean, or the standard error of the"
        + " mean. Ignored by the sample-size and recommended-density tables."
        + " Valid statistics are:\n    "
        + ", ".join(STATISTIC_CHOICES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the survey-cycle columns,"
        + " compared against the first year of each cycle. Ignored by the"
        + " recommended-density table. If None, returns from 1977.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the survey-cycle columns, compared"
        + " against the first year of each cycle. Ignored by the recommended-"
        + "density table. If None, returns through 2017-2018.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v[0] if isinstance(v, (list, tuple)) else v
        table = str(table).strip()
        if table not in TABLE_FILES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: " + ", ".join(TABLE_FILES)
            )
        return table

    @field_validator("demographics", mode="before", check_fields=False)
    @classmethod
    def _validate_demographics(cls, v):
        """Validate demographics."""
        if not v:
            return DEFAULT_DEMOGRAPHIC
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in DEMOGRAPHICS:
            raise OpenBBError(
                f"Invalid demographics: {value}. Valid subgroups are: "
                + ", ".join(DEMOGRAPHICS)
            )
        return value

    @field_validator("statistic", mode="before", check_fields=False)
    @classmethod
    def _validate_statistic(cls, v):
        """Validate statistic."""
        if not v:
            return DEFAULT_STATISTIC
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in STATISTIC_CHOICES:
            raise OpenBBError(
                f"Invalid statistic: {value}. Valid statistics are: "
                + ", ".join(STATISTIC_CHOICES)
            )
        return value


class FoodConsumptionNutrientIntakesAndDietQualityData(NullTokenMixin, Data):
    """USDA ERS Food Consumption, Nutrient Intakes, and Diet Quality Data.

    One selected table pivoted to a wide layout: the line-item identity stays
    in the rows while the survey cycles (Tables 1-7) or the recommended and
    actual densities (Table 8) spread into value columns, whose set varies by
    table.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Food Consumption, Nutrient Intakes, and Diet"
                " Quality",
                "$.description": "U.S. daily nutrient and food-group intake, share,"
                " and density by food source, with population-subgroup sample"
                " sizes and 2020-2025 recommended densities, from 1977 to 2018,"
                " published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    item: str = Field(
        description="Row identity: the nutrient (Tables 2-4, 8), food group"
        + " (Tables 5-8), or population subgroup (Table 1), as published. On the"
        + " intake tables (2-7) the food source is appended, e.g. 'Energy — FAH',"
        + " because each nutrient repeats once per food source.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Item",
                "pinned": "left",
                "minWidth": 260,
            }
        },
    )
    food_source: str | None = Field(
        default=None,
        description="Food source of the observation for the intake tables"
        + " (2-7): Total, food at home (FAH), food away from home (FAFH), or an"
        + " FAFH outlet. Already folded into the item label; kept as a separate"
        + " toggleable column. None for the sample-size and recommended-density"
        + " tables.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Food source",
                "pinned": "left",
                "minWidth": 150,
                "hide": True,
            }
        },
    )
    units: str | None = Field(
        default=None,
        description="Unit of the row's values, as published, e.g. 'Calories',"
        + " 'Grams', 'Percent of total', or 'Grams per 1,000 calories'. None"
        + " for the sample-size table and where a unit is carried in the item"
        + " label instead.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Units",
                "pinned": "left",
                "minWidth": 150,
                "hide": True,
            }
        },
    )


class FoodConsumptionNutrientIntakesAndDietQualityFetcher(
    Fetcher[
        FoodConsumptionNutrientIntakesAndDietQualityQueryParams,
        list[FoodConsumptionNutrientIntakesAndDietQualityData],
    ]
):
    """Fetch USDA ERS Food Consumption, Nutrient Intakes, and Diet Quality."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FoodConsumptionNutrientIntakesAndDietQualityQueryParams:
        """Transform the query params."""
        return FoodConsumptionNutrientIntakesAndDietQualityQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FoodConsumptionNutrientIntakesAndDietQualityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import (
            ers_food_consumption_nutrient_intakes_and_diet_quality,
        )

        return (
            await ers_food_consumption_nutrient_intakes_and_diet_quality.afetch_table(
                query.table
            )
        )

    @staticmethod
    def transform_data(
        query: FoodConsumptionNutrientIntakesAndDietQualityQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FoodConsumptionNutrientIntakesAndDietQualityData]:
        """Pivot the long-format rows into the selected wide table."""
        if query.table == SAMPLE_TABLE:
            rows, column_order = _pivot_sample(query, data)
        elif query.table == RECOMMENDED_TABLE:
            rows, column_order = _pivot_recommended(query, data)
        else:
            rows, column_order = _pivot_intake(query, data)
        return _finalize(rows, column_order)
