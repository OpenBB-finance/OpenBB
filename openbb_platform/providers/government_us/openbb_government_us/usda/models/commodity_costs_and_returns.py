"""Commodity Costs and Returns Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.ers_commodity_costs_and_returns import (
    CATEGORY_CHOICES,
    COMMODITY_FILES,
    COMMODITY_REGIONS,
    category_order,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix


class CommodityCostsAndReturnsQueryParams(QueryParams):
    """Commodity Costs and Returns Query Parameters.

    Source: https://www.ers.usda.gov/data-products/commodity-costs-and-returns
    """

    __json_schema_extra__ = {
        "commodity": {
            "x-widget_config": {
                "label": "Commodity",
                "multiSelect": False,
                "multiple": False,
                "value": "corn",
                "options": [
                    {"label": entry["label"], "value": key}
                    for key, entry in COMMODITY_FILES.items()
                ],
                "style": {"popupWidth": 320},
            },
        },
        "region": {
            "x-widget_config": {
                "label": "Region",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "value": "U.S. total",
                "optionsEndpoint": f"{api_prefix}/usda/commodity_cost_regions",
                "optionsParams": {"commodity": "$commodity"},
                "style": {"popupWidth": 320},
            },
        },
        "category": {
            "x-widget_config": {
                "label": "Budget section",
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in CATEGORY_CHOICES.items()
                ],
                "style": {"popupWidth": 300},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    commodity: str = Field(
        default="corn",
        description="Commodity budget to retrieve; selects the per-commodity"
        + " cost-and-return file. Valid commodities are:\n    "
        + ", ".join(COMMODITY_FILES)
        + "\n",
    )
    region: str | None = Field(
        default=None,
        description="ERS Farm Resource Region to retrieve, as the published"
        + " region label. The region set varies per commodity. If None, every"
        + " region in the commodity's budget is returned, with 'U.S. total'"
        + " the national aggregate.",
    )
    category: str | None = Field(
        default=None,
        description="Budget section to retrieve. If None, all sections are"
        + " returned. Valid sections are:\n    "
        + ", ".join(CATEGORY_CHOICES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " None returns from the commodity's first available year.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("commodity", mode="before", check_fields=False)
    @classmethod
    def _validate_commodity(cls, v):
        """Validate commodity."""
        if not v:
            return "corn"
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in COMMODITY_FILES:
            raise OpenBBError(
                f"Invalid commodity: {value}. Valid commodities are: "
                + ", ".join(COMMODITY_FILES)
            )
        return value

    @field_validator("region", mode="before", check_fields=False)
    @classmethod
    def _validate_region(cls, v):
        """Validate region."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        return value or None

    @field_validator("category", mode="before", check_fields=False)
    @classmethod
    def _validate_category(cls, v):
        """Validate category."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in CATEGORY_CHOICES:
            raise OpenBBError(
                f"Invalid category: {value}. Valid categories are: "
                + ", ".join(CATEGORY_CHOICES)
            )
        return value

    @model_validator(mode="after")
    def _validate_region_for_commodity(self):
        """Validate that the region belongs to the selected commodity."""
        if self.region is not None and self.region not in COMMODITY_REGIONS.get(
            self.commodity, []
        ):
            raise OpenBBError(
                f"Invalid region '{self.region}' for commodity"
                f" '{self.commodity}'. Valid regions are: "
                + ", ".join(COMMODITY_REGIONS.get(self.commodity, []))
            )
        return self


class CommodityCostsAndReturnsData(NullTokenMixin, Data):
    """Commodity Costs and Returns Data.

    Annual per-acre or per-unit cost-and-return budgets for major U.S. field
    crops and livestock enterprises, published by USDA ERS. Each row is one
    budget line for a region, with one value column per year.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Commodity Costs & Returns",
                "$.description": "Per-acre and per-unit cost-and-return budgets for"
                " major U.S. field crops and livestock enterprises, published by"
                " the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    commodity: str = Field(
        description="Commodity name, as published.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Commodity", "hide": True}
        },
    )
    region: str = Field(
        description="ERS Farm Resource Region of the budget, or 'U.S. total'"
        + " for the national aggregate.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Region", "pinned": "left"}
        },
    )
    category: str = Field(
        description="Budget section of the line, as published, e.g. 'Operating"
        + " costs' or 'Gross value of production'.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Budget section", "pinned": "left"}
        },
    )
    item: str = Field(
        description="Budget line item, as published, with footnote"
        + " superscripts and stray whitespace stripped.",
        json_schema_extra={"x-widget_config": {"headerName": "Item", "pinned": "left"}},
    )
    units: str = Field(
        description="Unit of the line's values, as published, e.g. 'dollars"
        + " per planted acre' or 'bushels per planted acre'.",
        json_schema_extra={"x-widget_config": {"headerName": "Units"}},
    )
    survey_base_year: str | None = Field(
        default=None,
        description="Survey base of the most recent year in the row, as"
        + " published, e.g. 'Base survey of 2021'.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Survey base", "hide": True}
        },
    )


class CommodityCostsAndReturnsFetcher(
    Fetcher[
        CommodityCostsAndReturnsQueryParams,
        list[CommodityCostsAndReturnsData],
    ]
):
    """Fetch USDA ERS Commodity Costs and Returns."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CommodityCostsAndReturnsQueryParams:
        """Transform the query params."""
        return CommodityCostsAndReturnsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CommodityCostsAndReturnsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected commodity's tidy CSV rows."""
        from openbb_government_us.usda.utils import ers_commodity_costs_and_returns

        return await ers_commodity_costs_and_returns.afetch_commodity(query.commodity)

    @staticmethod
    def transform_data(
        query: CommodityCostsAndReturnsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CommodityCostsAndReturnsData]:
        """Transform the data by pivoting each budget line's years into columns."""
        category = CATEGORY_CHOICES[query.category] if query.category else None
        region_order = COMMODITY_REGIONS.get(query.commodity, [])
        pivoted: dict[tuple, dict] = {}
        for record in data:
            if query.start_year is not None and record["year"] < query.start_year:
                continue
            if query.end_year is not None and record["year"] > query.end_year:
                continue
            if query.region is not None and record["region"] != query.region:
                continue
            if category is not None and record["category"] != category:
                continue
            key = (
                record["region"],
                record["category"],
                record["item"],
                record["units"],
            )
            row = pivoted.get(key)
            if row is None:
                region_index = (
                    region_order.index(record["region"])
                    if record["region"] in region_order
                    else len(region_order)
                )
                row = {
                    "_region_index": region_index,
                    "_category_order": category_order(record["category"]),
                    "_total_last": 1 if record["item"].startswith("Total,") else 0,
                    "_max_year": -1,
                    "commodity": record["commodity"],
                    "region": record["region"],
                    "category": record["category"],
                    "item": record["item"],
                    "units": record["units"],
                    "survey_base_year": None,
                }
                pivoted[key] = row
            row[str(record["year"])] = record["value"]
            if record["year"] > row["_max_year"]:
                row["_max_year"] = record["year"]
                row["survey_base_year"] = record["survey_base_year"]
        if not pivoted:
            raise EmptyDataError("No records match the given filters.")
        results = sorted(
            pivoted.values(),
            key=lambda row: (
                row["_region_index"],
                row["_category_order"],
                row["_total_last"],
                row["item"],
            ),
        )
        all_years = sorted(
            {int(k) for row in pivoted.values() for k in row if k.isdigit()}
        )
        validated: list = []
        for row in results:
            dimensions = {
                k: v
                for k, v in row.items()
                if not k.startswith("_") and not k.isdigit()
            }
            years = {str(year): row.get(str(year)) for year in all_years}
            validated.append(
                CommodityCostsAndReturnsData.model_validate({**dimensions, **years})
            )
        return validated
