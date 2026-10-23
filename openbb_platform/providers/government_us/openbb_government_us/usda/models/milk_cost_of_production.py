"""Milk Cost Of Production Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.ers_milk_cost_of_production import (
    CATEGORY_CHOICES,
    ITEM_CHOICES,
    SIZE_CHOICES,
    STATE_CHOICES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

Report = Literal["by_state", "by_size_of_operation"]


def _validate_selection(v, choices: dict[str, str], name: str) -> str | None:
    """Normalize a list or comma-string selection against valid choices.

    Parameters
    ----------
    v : Any
        Raw selection value, a list or comma-separated string.
    choices : dict[str, str]
        Valid choice keys mapped to published labels.
    name : str
        Field name used in the error message.

    Returns
    -------
    str | None
        Comma-joined normalized selection, or None when empty.

    Raises
    ------
    OpenBBError
        If any selected value is not a valid choice.
    """
    if not v:
        return None
    values = v.split(",") if isinstance(v, str) else list(v)
    values = [value.strip() for value in values if value and value.strip()]
    if not values:
        return None
    unknown = [value for value in values if value not in choices]
    if unknown:
        raise OpenBBError(
            f"Invalid {name}(s): {', '.join(unknown)}. Valid choices are: "
            + ", ".join(sorted(choices))
        )
    return ",".join(values)


class MilkCostOfProductionQueryParams(QueryParams):
    """Milk Cost Of Production Query Parameters.

    Source: https://www.ers.usda.gov/data-products/milk-cost-of-production-estimates
    """

    __json_schema_extra__ = {
        "report": {
            "x-widget_config": {
                "label": "Report",
                "options": [
                    {"label": "By state", "value": "by_state"},
                    {
                        "label": "By herd-size class",
                        "value": "by_size_of_operation",
                    },
                ],
            },
        },
        "state": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "State",
                "multiSelect": False,
                "multiple": False,
                "value": "us_total",
                "options": [
                    {"label": label, "value": key}
                    for key, label in STATE_CHOICES.items()
                ],
            },
        },
        "size": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Herd-size class",
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in SIZE_CHOICES.items()
                ],
            },
        },
        "category": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Cost category",
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in CATEGORY_CHOICES.items()
                ],
                "style": {"popupWidth": 300},
            },
        },
        "item": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Cost item",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/milk_cost_items",
                "optionsParams": {"report": "$report", "category": "$category"},
                "style": {"popupWidth": 360},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    report: Report = Field(
        default="by_state",
        description="Report to retrieve: estimates by state or by size of"
        + " operation (herd-size class).",
    )
    state: str | None = Field(
        default=None,
        description="State(s) to filter, as a comma-separated list."
        + " Only valid with report='by_state'."
        + " If None, all states and the U.S. total are returned."
        + " Valid states are:\n    "
        + ", ".join(sorted(STATE_CHOICES))
        + "\n",
    )
    size: str | None = Field(
        default=None,
        description="Herd-size class(es) to filter, as a comma-separated list."
        + " Only valid with report='by_size_of_operation'."
        + " If None, all size classes are returned. Valid sizes are:\n    "
        + ", ".join(sorted(SIZE_CHOICES))
        + "\n",
    )
    category: str | None = Field(
        default=None,
        description="Estimate category(s) to filter, as a comma-separated list."
        + " If None, all categories are returned. Valid categories are:\n    "
        + ", ".join(sorted(CATEGORY_CHOICES))
        + "\n",
    )
    item: str | None = Field(
        default=None,
        description="Estimate item(s) to filter, as a comma-separated list."
        + " If None, all items are returned. Valid items are:\n    "
        + ", ".join(sorted(ITEM_CHOICES))
        + "\n",
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

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate state."""
        return _validate_selection(v, STATE_CHOICES, "state")

    @field_validator("size", mode="before", check_fields=False)
    @classmethod
    def _validate_size(cls, v):
        """Validate size."""
        return _validate_selection(v, SIZE_CHOICES, "size")

    @field_validator("category", mode="before", check_fields=False)
    @classmethod
    def _validate_category(cls, v):
        """Validate category."""
        return _validate_selection(v, CATEGORY_CHOICES, "category")

    @field_validator("item", mode="before", check_fields=False)
    @classmethod
    def _validate_item(cls, v):
        """Validate item."""
        return _validate_selection(v, ITEM_CHOICES, "item")

    @model_validator(mode="after")
    def _validate_report_filters(self):
        """Validate that state and size match the selected report."""
        if self.report == "by_state" and self.size is not None:
            raise OpenBBError(
                "The 'size' filter applies only to report='by_size_of_operation'."
            )
        if self.report == "by_size_of_operation" and self.state is not None:
            raise OpenBBError("The 'state' filter applies only to report='by_state'.")
        return self


class MilkCostOfProductionData(NullTokenMixin, Data):
    """Milk Cost Of Production Data.

    Annual milk cost-of-production estimates from USDA ERS, built from the
    2021 Agricultural Resource Management Survey base. Each row is one
    cost-and-returns line for one State or one herd-size class, with one
    value column per year.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Milk Cost of Production",
                "$.description": "Annual milk cost-of-production estimates by state and by size of operation, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    group: str = Field(
        description="Population the estimate covers: the State, or 'U.S. total'"
        + " for the national aggregate, in the by_state report; the herd-size"
        + " class in the by_size_of_operation report.",
        json_schema_extra={
            "x-widget_config": {"headerName": "State / herd size", "pinned": "left"}
        },
    )
    category: str = Field(
        description="Estimate category, as published. One of: Gross value of"
        + " production, Operating costs, Allocated overhead, Costs listed,"
        + " Net value, Supporting information.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Cost category", "pinned": "left"}
        },
    )
    item: str = Field(
        description="Estimate item, as published, with footnote superscripts"
        + " stripped. Includes published subtotal and net-value rows.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Cost item", "pinned": "left"}
        },
    )
    unit: str = Field(
        description="Unit of the value, as published. Cost and return items"
        + " are 'dollars per hundredweight sold'; 'Milk cows' is"
        + " 'head per farm' and 'Output per cow' is 'pounds'.",
        json_schema_extra={"x-widget_config": {"headerName": "Unit"}},
    )


class MilkCostOfProductionFetcher(
    Fetcher[
        MilkCostOfProductionQueryParams,
        list[MilkCostOfProductionData],
    ]
):
    """Fetch USDA ERS Milk Cost of Production Estimates."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> MilkCostOfProductionQueryParams:
        """Transform the query params."""
        return MilkCostOfProductionQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: MilkCostOfProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected report's tidy CSV rows."""
        from openbb_government_us.usda.utils import ers_milk_cost_of_production

        return await ers_milk_cost_of_production.afetch_report(query.report)

    @staticmethod
    def transform_data(
        query: MilkCostOfProductionQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[MilkCostOfProductionData]:
        """Filter the report's rows and spread the years into ascending columns.

        Returns
        -------
        list[MilkCostOfProductionData]
            One record per State or herd-size class, cost category and item,
            ordered by the published dimension, category and item order, with
            subtotal lines last within a category.

        Raises
        ------
        EmptyDataError
            If no record survives the filters.
        """
        states = (
            {STATE_CHOICES[value] for value in query.state.split(",")}
            if query.state
            else None
        )
        sizes = (
            {SIZE_CHOICES[value] for value in query.size.split(",")}
            if query.size
            else None
        )
        categories = (
            {CATEGORY_CHOICES[value] for value in query.category.split(",")}
            if query.category
            else None
        )
        items = (
            {ITEM_CHOICES[value] for value in query.item.split(",")}
            if query.item
            else None
        )
        group_order = list(
            (STATE_CHOICES if query.report == "by_state" else SIZE_CHOICES).values()
        )
        category_order = list(CATEGORY_CHOICES.values())
        pivoted: dict[tuple, dict] = {}
        years: set[int] = set()
        for record in data:
            if query.start_year is not None and record["year"] < query.start_year:
                continue
            if query.end_year is not None and record["year"] > query.end_year:
                continue
            if states is not None and record["state"] not in states:
                continue
            if sizes is not None and record["size_of_operation"] not in sizes:
                continue
            if categories is not None and record["category"] not in categories:
                continue
            if items is not None and record["item"] not in items:
                continue
            group = record.get("state") or record.get("size_of_operation") or ""
            key = (group, record["category"], record["item"], record["unit"])
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_group_index": (
                        group_order.index(group)
                        if group in group_order
                        else len(group_order)
                    ),
                    "_category_index": (
                        category_order.index(record["category"])
                        if record["category"] in category_order
                        else len(category_order)
                    ),
                    "_total_last": 1 if record["item"].startswith("Total,") else 0,
                    "group": group,
                    "category": record["category"],
                    "item": record["item"],
                    "unit": record["unit"],
                }
                pivoted[key] = row
            years.add(record["year"])
            row[str(record["year"])] = record["value"]
        if not pivoted:
            raise EmptyDataError("No records match the given filters.")
        columns = [str(year) for year in sorted(years)]
        results = sorted(
            pivoted.values(),
            key=lambda row: (
                row["_group_index"],
                row["_category_index"],
                row["_total_last"],
                row["item"],
            ),
        )
        validated: list[MilkCostOfProductionData] = []
        for row in results:
            payload = {key: row[key] for key in ("group", "category", "item", "unit")}
            for column in columns:
                payload[column] = row.get(column)
            validated.append(MilkCostOfProductionData.model_validate(payload))
        return validated
