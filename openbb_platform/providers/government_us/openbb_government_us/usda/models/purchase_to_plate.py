"""Purchase to Plate National Average Prices Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_purchase_to_plate import (
    CYCLE_HEADERS,
    CYCLE_ORDER,
    DEFAULT_FOOD_GROUP,
    FOOD_GROUPS,
    group_options,
)
from openbb_government_us.utils.serializers import NullTokenMixin


def _cycle(field: str) -> dict:
    """Build the numeric column config for one survey-cycle price field."""
    return {
        "x-widget_config": {
            "headerName": CYCLE_HEADERS[field],
            "cellDataType": "number",
        }
    }


class PurchaseToPlateQueryParams(QueryParams):
    """Purchase to Plate National Average Prices Query Parameters.

    Source: https://www.ers.usda.gov/data-products/purchase-to-plate
    """

    __json_schema_extra__ = {
        "food_group": {
            "x-widget_config": {
                "label": "Food group",
                "value": DEFAULT_FOOD_GROUP,
                "multiSelect": False,
                "multiple": False,
                "options": group_options(),
                "style": {"popupWidth": 320},
            },
        },
    }

    food_group: str = Field(
        default=DEFAULT_FOOD_GROUP,
        description="Food group to retrieve, derived from the FNDDS food-code"
        + " leading digit. Valid food groups are:\n    "
        + ", ".join(FOOD_GROUPS)
        + "\n",
    )

    @field_validator("food_group", mode="before", check_fields=False)
    @classmethod
    def _validate_food_group(cls, v):
        """Validate food group."""
        if not v:
            return DEFAULT_FOOD_GROUP
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        canonical = {slug.casefold(): slug for slug in FOOD_GROUPS}.get(
            value.casefold()
        )
        if canonical is None:
            raise OpenBBError(
                f"Invalid food_group: {value}. Valid food groups are: "
                + ", ".join(FOOD_GROUPS)
            )
        return canonical


class PurchaseToPlateData(NullTokenMixin, Data):
    """Purchase to Plate National Average Prices Data.

    One row per food item, with the USDA ERS Purchase to Plate national
    average price, in nominal dollars per 100 edible grams, spread across the
    four biennial survey cycles as columns.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Purchase to Plate National Average Prices",
                "$.description": "Estimated national average prices, in nominal"
                " dollars per 100 edible grams, for foods reported in NHANES,"
                " across the 2011/2012 through 2017/2018 survey cycles,"
                " published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    food_code: str = Field(
        description="Eight-digit FNDDS food code identifying the food item.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Food code",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 130,
            }
        },
    )
    mod_code: str | None = Field(
        default=None,
        description="Recipe modification code, '0' for an unmodified item."
        + " Non-zero only on the 2011/2012 recipe-modification rows.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Modification code", "hide": True}
        },
    )
    food_description: str = Field(
        description="Food description, as published in the most recent survey"
        + " cycle the item appears in.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Food description", "pinned": "left"}
        },
    )
    method_description: str | None = Field(
        default=None,
        description="Price-estimation method, as published in the most recent"
        + " survey cycle the item appears in.",
        json_schema_extra={"x-widget_config": {"headerName": "Method", "hide": True}},
    )
    nhanes: str | None = Field(
        default=None,
        description="NHANES reporting flag, as published in the most recent"
        + " survey cycle the item appears in.",
        json_schema_extra={"x-widget_config": {"headerName": "NHANES", "hide": True}},
    )
    cycle_2011_2012: float | None = Field(
        default=None,
        description="National average price for the 2011/2012 survey cycle,"
        + " in nominal U.S. dollars per 100 edible grams.",
        json_schema_extra=_cycle("cycle_2011_2012"),
    )
    cycle_2013_2014: float | None = Field(
        default=None,
        description="National average price for the 2013/2014 survey cycle,"
        + " in nominal U.S. dollars per 100 edible grams.",
        json_schema_extra=_cycle("cycle_2013_2014"),
    )
    cycle_2015_2016: float | None = Field(
        default=None,
        description="National average price for the 2015/2016 survey cycle,"
        + " in nominal U.S. dollars per 100 edible grams.",
        json_schema_extra=_cycle("cycle_2015_2016"),
    )
    cycle_2017_2018: float | None = Field(
        default=None,
        description="National average price for the 2017/2018 survey cycle,"
        + " in nominal U.S. dollars per 100 edible grams.",
        json_schema_extra=_cycle("cycle_2017_2018"),
    )


class PurchaseToPlateFetcher(
    Fetcher[
        PurchaseToPlateQueryParams,
        list[PurchaseToPlateData],
    ]
):
    """Fetch USDA ERS Purchase to Plate National Average Prices."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> PurchaseToPlateQueryParams:
        """Transform the query params."""
        return PurchaseToPlateQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: PurchaseToPlateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the long national-average-prices records."""
        from openbb_government_us.usda.utils import ers_purchase_to_plate

        return await ers_purchase_to_plate.afetch_table()

    @staticmethod
    def transform_data(
        query: PurchaseToPlateQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[PurchaseToPlateData]:
        """Pivot the selected food group's rows to one wide row per food item."""
        groups: dict[tuple, dict] = {}
        order: list[tuple] = []
        for record in data:
            if record["food_group"] != query.food_group:
                continue
            key = (record["food_code"], record["mod_code"])
            row = groups.get(key)
            if row is None:
                row = {
                    "_order": len(order),
                    "_recent": -1,
                    "food_code": record["food_code"],
                    "mod_code": record["mod_code"],
                    "food_description": None,
                    "method_description": None,
                    "nhanes": None,
                }
                groups[key] = row
                order.append(key)
            row[record["cycle"]] = record["price"]
            if record["cycle_index"] >= row["_recent"]:
                row["_recent"] = record["cycle_index"]
                row["food_description"] = record["food_description"]
                row["method_description"] = record["method_description"]
                row["nhanes"] = record["nhanes"]
        kept = [
            groups[key]
            for key in order
            if any(groups[key].get(cycle) is not None for cycle in CYCLE_ORDER)
        ]
        if not kept:
            raise EmptyDataError("No records match the given filters.")
        kept.sort(key=lambda row: (row["food_code"], row["mod_code"]))
        return [
            PurchaseToPlateData.model_validate(
                {k: v for k, v in row.items() if not k.startswith("_")}
            )
            for row in kept
        ]
