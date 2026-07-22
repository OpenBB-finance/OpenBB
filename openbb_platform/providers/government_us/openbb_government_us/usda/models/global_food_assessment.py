"""USDA ERS Global Food Assessment Model."""

from collections import OrderedDict
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_global_food_assessment import (
    DEFAULT_ELEMENT,
    ELEMENTS,
    REGIONS,
    UNIT,
)
from openbb_government_us.utils.serializers import NullTokenMixin

ELEMENT_OPTIONS = [{"label": name, "value": name} for name in ELEMENTS]
REGION_OPTIONS = [{"label": name, "value": name} for name in REGIONS]


class GlobalFoodAssessmentQueryParams(QueryParams):
    """USDA ERS Global Food Assessment Query Parameters.

    Source: https://www.ers.usda.gov/data-products/global-food-assessment
    """

    __json_schema_extra__ = {
        "element": {
            "x-widget_config": {
                "label": "Measure",
                "value": DEFAULT_ELEMENT,
                "multiSelect": False,
                "multiple": False,
                "options": ELEMENT_OPTIONS,
                "style": {"popupWidth": 320},
            },
        },
        "region": {
            "x-widget_config": {
                "label": "Region",
                "multiSelect": False,
                "multiple": False,
                "options": REGION_OPTIONS,
                "style": {"popupWidth": 320},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    element: str = Field(
        default=DEFAULT_ELEMENT,
        description="Measure to retrieve. The measure selects one series whose"
        + " subregions spread into the wide columns while the base year and the"
        + " ten-year projection horizon stay in the rows. Valid measures are:\n    "
        + ", ".join(ELEMENTS)
        + "\n",
    )
    region: str | None = Field(
        default=None,
        description="Filter to a single region's subregions, e.g."
        + " 'Sub-Saharan Africa'. If None, every subregion is spread into the"
        + " columns. Valid regions are:\n    "
        + ", ".join(REGIONS)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " observation year. If None, returns from the base year.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " observation year. If None, returns through the projection horizon.",
    )

    @field_validator("element", mode="before", check_fields=False)
    @classmethod
    def _validate_element(cls, v):
        """Validate element, defaulting a blank value."""
        if not v:
            return DEFAULT_ELEMENT
        value = v[0] if isinstance(v, (list, tuple)) else v
        element = str(value).strip()
        if element not in ELEMENTS:
            raise OpenBBError(
                f"Invalid measure: {element}. Valid measures are: "
                + ", ".join(ELEMENTS)
            )
        return element

    @field_validator("region", mode="before", check_fields=False)
    @classmethod
    def _validate_region(cls, v):
        """Normalize region to a stripped string or None, validating membership."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        region = str(value).strip()
        if not region:
            return None
        if region not in REGIONS:
            raise OpenBBError(
                f"Invalid region: {region}. Valid regions are: " + ", ".join(REGIONS)
            )
        return region


class GlobalFoodAssessmentData(NullTokenMixin, Data):
    """USDA ERS Global Food Assessment Data.

    One selected measure pivoted to a wide layout: the base year and the
    ten-year projection horizon stay in the rows while the subregions spread
    into value columns, whose set narrows with the optional region filter. The
    measure and its shared unit are constant for a selection and are carried as
    hidden context dimensions rather than visible columns.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Global Food Assessment",
                "$.description": "Grain food demand, other demand, total demand,"
                " production, and the implied additional supply required to close"
                " the food gap, for global food assessment regions and subregions"
                " in the base year and the ten-year projection horizon, published"
                " by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: str = Field(
        description="Year of the observation: the base year or the ten-year"
        + " projection horizon, e.g. '2025' or '2035'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 110,
            }
        },
    )
    element: str | None = Field(
        default=None,
        description="Measure spread into the subregion columns, as published.",
        json_schema_extra={"x-widget_config": {"headerName": "Measure", "hide": True}},
    )
    unit: str | None = Field(
        default=None,
        description="Unit shared by every value column for the selection, as"
        + " published in the source value-column header: 'Millions of metric"
        + " tons'.",
        json_schema_extra={"x-widget_config": {"headerName": "Unit", "hide": True}},
    )


class GlobalFoodAssessmentFetcher(
    Fetcher[
        GlobalFoodAssessmentQueryParams,
        list[GlobalFoodAssessmentData],
    ]
):
    """Fetch USDA ERS Global Food Assessment Data."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> GlobalFoodAssessmentQueryParams:
        """Transform the query params."""
        return GlobalFoodAssessmentQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: GlobalFoodAssessmentQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the file's long-format rows."""
        from openbb_government_us.usda.utils import ers_global_food_assessment

        return await ers_global_food_assessment.afetch_records()

    @staticmethod
    def transform_data(
        query: GlobalFoodAssessmentQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[GlobalFoodAssessmentData]:
        """Pivot the long-format rows into the subregion-by-year wide table."""
        column_order: OrderedDict[str, None] = OrderedDict()
        by_year: dict[int, dict] = {}
        for record in data:
            if record["element"] != query.element:
                continue
            if query.region is not None and record["region"] != query.region:
                continue
            amount = record["amount"]
            if amount is None:
                continue
            year_label = record["year"]
            if not year_label.isdigit():
                continue
            year_sort = int(year_label)
            if query.start_year is not None and year_sort < query.start_year:
                continue
            if query.end_year is not None and year_sort > query.end_year:
                continue
            subregion = record["subregion"]
            column_order.setdefault(subregion, None)
            row = by_year.get(year_sort)
            if row is None:
                row = {
                    "year": year_label,
                    "element": record["element"],
                    "unit": UNIT,
                }
                by_year[year_sort] = row
            row[subregion] = amount
        results: list[GlobalFoodAssessmentData] = []
        for year_sort in sorted(by_year):
            source = by_year[year_sort]
            row = {
                "year": source["year"],
                "element": source["element"],
                "unit": source["unit"],
            }
            for column in column_order:
                row[column] = source.get(column)
            results.append(GlobalFoodAssessmentData.model_validate(row))
        return results
