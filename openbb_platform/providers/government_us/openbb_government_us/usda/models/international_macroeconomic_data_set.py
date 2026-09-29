"""USDA ERS International Macroeconomic Data Set Model."""

from collections import OrderedDict
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_international_macroeconomic_data_set import (
    DEFAULT_MEASURE,
    DEFAULT_VARIABLE,
    INTERNATIONAL_MACRO_FILES,
    MEASURES,
    is_growth_unit,
)
from openbb_government_us.utils.serializers import NullTokenMixin

VARIABLE_OPTIONS = [
    {"label": config["label"], "value": key}
    for key, config in INTERNATIONAL_MACRO_FILES.items()
]

MEASURE_OPTIONS = [{"label": label, "value": key} for key, label in MEASURES.items()]


class InternationalMacroeconomicDataSetQueryParams(QueryParams):
    """USDA ERS International Macroeconomic Data Set Query Parameters.

    Source: https://www.ers.usda.gov/data-products/international-macroeconomic-data-set
    """

    __json_schema_extra__ = {
        "variable": {
            "x-widget_config": {
                "label": "Variable",
                "value": DEFAULT_VARIABLE,
                "multiSelect": False,
                "multiple": False,
                "options": VARIABLE_OPTIONS,
                "style": {"popupWidth": 360},
            },
        },
        "measure": {
            "x-widget_config": {
                "label": "Measure",
                "value": DEFAULT_MEASURE,
                "multiSelect": False,
                "multiple": False,
                "options": MEASURE_OPTIONS,
                "style": {"popupWidth": 280},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    variable: str = Field(
        default=DEFAULT_VARIABLE,
        description="Macroeconomic variable to retrieve. Each variable is a"
        + " separate file whose baseline countries and regions spread into the"
        + " wide columns while the years stay in the rows, running from 1970"
        + " through the 2035 projection horizon. Valid variables are:\n    "
        + ", ".join(INTERNATIONAL_MACRO_FILES)
        + "\n",
    )
    measure: str = Field(
        default=DEFAULT_MEASURE,
        description="Measure to spread. 'level' returns the variable's level"
        + " unit; 'growth' returns its year-to-year percent change."
        + " Valid measures are:\n    "
        + ", ".join(MEASURES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from 1970, the first year of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns through 2035, the last projection year.",
    )

    @field_validator("variable", mode="before", check_fields=False)
    @classmethod
    def _validate_variable(cls, v):
        """Validate variable."""
        if not v:
            return DEFAULT_VARIABLE
        variable = v.strip() if isinstance(v, str) else v
        if variable not in INTERNATIONAL_MACRO_FILES:
            raise OpenBBError(
                f"Invalid variable: {variable}. Valid variables are: "
                + ", ".join(INTERNATIONAL_MACRO_FILES)
            )
        return variable

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


class InternationalMacroeconomicDataSetData(NullTokenMixin, Data):
    """USDA ERS International Macroeconomic Data Set Data.

    One selected variable and measure pivoted to a wide layout: the years stay
    in the rows while the baseline countries and regions spread into value
    columns, whose set varies slightly by variable. A single unit applies to
    the whole table for a given variable and measure.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS International Macroeconomic Data Set",
                "$.description": "Historical and projected real GDP, GDP per"
                " capita, GDP deflator, real GDP shares, real exchange rates,"
                " consumer price indices, and population for baseline countries"
                " and regions from 1970 through 2035, published by the USDA"
                " Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: int = Field(
        description="Calendar year of the observation, from 1970 through the"
        + " 2035 projection horizon.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "number",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    unit: str | None = Field(
        default=None,
        description="Unit shared by every value column for the selected"
        + " variable and measure, as published.",
        json_schema_extra={"x-widget_config": {"headerName": "Unit", "hide": True}},
    )


class InternationalMacroeconomicDataSetFetcher(
    Fetcher[
        InternationalMacroeconomicDataSetQueryParams,
        list[InternationalMacroeconomicDataSetData],
    ]
):
    """Fetch USDA ERS International Macroeconomic Data Set."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> InternationalMacroeconomicDataSetQueryParams:
        """Transform the query params."""
        return InternationalMacroeconomicDataSetQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: InternationalMacroeconomicDataSetQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected variable's long-format rows."""
        from openbb_government_us.usda.utils import (
            ers_international_macroeconomic_data_set,
        )

        return await ers_international_macroeconomic_data_set.afetch_records(
            query.variable
        )

    @staticmethod
    def transform_data(
        query: InternationalMacroeconomicDataSetQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[InternationalMacroeconomicDataSetData]:
        """Pivot the long-format rows into the country-by-year wide table."""
        growth = query.measure == "growth"
        selected = [
            record for record in data if is_growth_unit(record["unit"]) == growth
        ]
        column_order: OrderedDict[str, None] = OrderedDict()
        unit: str | None = None
        for record in selected:
            column_order.setdefault(record["observation"], None)
            if unit is None:
                unit = record["unit"]
        by_year: dict[int, dict] = {}
        for record in selected:
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            row = by_year.get(year)
            if row is None:
                row = {"year": year, "unit": unit}
                by_year[year] = row
            row[record["observation"]] = record["value"]
        results: list[InternationalMacroeconomicDataSetData] = []
        for year in sorted(by_year):
            source = by_year[year]
            row = {"year": source["year"], "unit": source["unit"]}
            for column in column_order:
                row[column] = source.get(column)
            results.append(InternationalMacroeconomicDataSetData.model_validate(row))
        return results
