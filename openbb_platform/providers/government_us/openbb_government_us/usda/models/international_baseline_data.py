"""USDA ERS International Baseline Data Model."""

from collections import OrderedDict
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_international_baseline_data import (
    COMMODITIES,
    DEFAULT_ATTRIBUTE,
    DEFAULT_COMMODITY,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

COMMODITY_OPTIONS = [{"label": name, "value": name} for name in COMMODITIES]


class InternationalBaselineDataQueryParams(QueryParams):
    """USDA ERS International Baseline Data Query Parameters.

    Source: https://www.ers.usda.gov/data-products/international-baseline-data
    """

    __json_schema_extra__ = {
        "commodity": {
            "x-widget_config": {
                "label": "Commodity",
                "value": DEFAULT_COMMODITY,
                "multiSelect": False,
                "multiple": False,
                "options": COMMODITY_OPTIONS,
                "style": {"popupWidth": 260},
            },
        },
        "attribute": {
            "x-widget_config": {
                "label": "Measure",
                "type": "endpoint",
                "value": DEFAULT_ATTRIBUTE,
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/intl_baseline_attributes",
                "optionsParams": {"commodity": "$commodity"},
                "style": {"popupWidth": 300},
            },
        },
        "country": {
            "x-widget_config": {
                "label": "Country or region",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/intl_baseline_countries",
                "optionsParams": {"commodity": "$commodity"},
                "style": {"popupWidth": 320},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    commodity: str = Field(
        default=DEFAULT_COMMODITY,
        description="Commodity to retrieve. The commodity and measure select one"
        + " projection series whose countries and regions spread into the wide"
        + " columns while the years stay in the rows. Valid commodities are:\n    "
        + ", ".join(COMMODITIES)
        + "\n",
    )
    attribute: str = Field(
        default=DEFAULT_ATTRIBUTE,
        description="Measure to spread into the country columns, e.g."
        + " 'Production', 'Exports', or 'Ending stocks'. The available measures"
        + " depend on the commodity.",
    )
    country: str | None = Field(
        default=None,
        description="Filter to a single country or region column, e.g. 'China'."
        + " If None, every country and region is spread into the columns.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " first four digits of the crop or calendar year."
        + " If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " first four digits of the crop or calendar year."
        + " If None, returns through the last projection year.",
    )

    @field_validator("commodity", mode="before", check_fields=False)
    @classmethod
    def _validate_commodity(cls, v):
        """Validate commodity."""
        if not v:
            return DEFAULT_COMMODITY
        commodity = v.strip() if isinstance(v, str) else v
        if commodity not in COMMODITIES:
            raise OpenBBError(
                f"Invalid commodity: {commodity}. Valid commodities are: "
                + ", ".join(COMMODITIES)
            )
        return commodity

    @field_validator("attribute", mode="before", check_fields=False)
    @classmethod
    def _validate_attribute(cls, v):
        """Normalize attribute to a stripped string, defaulting to Production."""
        if not v:
            return DEFAULT_ATTRIBUTE
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip() or DEFAULT_ATTRIBUTE

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def _validate_country(cls, v):
        """Normalize country to a stripped string or None."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip() or None


class InternationalBaselineDataData(NullTokenMixin, Data):
    """USDA ERS International Baseline Data.

    One selected commodity and measure pivoted to a wide layout: the crop or
    calendar years stay in the rows while the countries and regions spread into
    value columns, whose set varies by commodity and measure. The commodity,
    measure, unit, year type, and topic are constant for a selection and are
    carried as hidden context dimensions rather than visible columns.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS International Baseline Data",
                "$.description": "Historical and projected area, yield,"
                " production, supply, use, and trade for grains, oilseeds,"
                " cotton, and livestock by country and region through the"
                " long-term projection horizon, published by the USDA Economic"
                " Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: str = Field(
        description="Crop or calendar year of the observation, as published,"
        + " e.g. '2024/25' for crops or '2024' for livestock.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "pinned": "left",
                "maxWidth": 110,
            }
        },
    )
    commodity: str | None = Field(
        default=None,
        description="Commodity of the selection, as published.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Commodity", "hide": True}
        },
    )
    attribute: str | None = Field(
        default=None,
        description="Measure spread into the country columns, as published.",
        json_schema_extra={"x-widget_config": {"headerName": "Measure", "hide": True}},
    )
    unit: str | None = Field(
        default=None,
        description="Unit shared by every value column for the selection,"
        + " as published, e.g. 'Thousand metric tons'.",
        json_schema_extra={"x-widget_config": {"headerName": "Unit", "hide": True}},
    )
    year_type: str | None = Field(
        default=None,
        description="Year basis of the selection: 'Crop year' for crops or"
        + " 'Calendar year' for livestock.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Year type", "hide": True}
        },
    )
    topic: str | None = Field(
        default=None,
        description="Topic of the commodity: 'Crops' or 'Livestock'.",
        json_schema_extra={"x-widget_config": {"headerName": "Topic", "hide": True}},
    )


class InternationalBaselineDataFetcher(
    Fetcher[
        InternationalBaselineDataQueryParams,
        list[InternationalBaselineDataData],
    ]
):
    """Fetch USDA ERS International Baseline Data."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> InternationalBaselineDataQueryParams:
        """Transform the query params."""
        return InternationalBaselineDataQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: InternationalBaselineDataQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the projection file's long-format rows."""
        from openbb_government_us.usda.utils import ers_international_baseline_data

        return await ers_international_baseline_data.afetch_records()

    @staticmethod
    def transform_data(
        query: InternationalBaselineDataQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[InternationalBaselineDataData]:
        """Pivot the long-format rows into the country-by-year wide table."""
        column_order: OrderedDict[str, None] = OrderedDict()
        by_year: dict[int, dict] = {}
        for record in data:
            if record["commodity"] != query.commodity:
                continue
            if record["attribute"] != query.attribute:
                continue
            if query.country is not None and record["country"] != query.country:
                continue
            amount = record["amount"]
            if amount is None:
                continue
            year_label = record["year"]
            if not year_label[:4].isdigit():
                continue
            year_sort = int(year_label[:4])
            if query.start_year is not None and year_sort < query.start_year:
                continue
            if query.end_year is not None and year_sort > query.end_year:
                continue
            country = record["country"]
            column_order.setdefault(country, None)
            row = by_year.get(year_sort)
            if row is None:
                row = {
                    "_year": year_sort,
                    "year": year_label,
                    "commodity": record["commodity"],
                    "attribute": record["attribute"],
                    "unit": record["unit"],
                    "year_type": record["year_type"],
                    "topic": record["topic"],
                }
                by_year[year_sort] = row
            row[country] = amount
        results: list[InternationalBaselineDataData] = []
        for year_sort in sorted(by_year):
            source = by_year[year_sort]
            row = {
                "year": source["year"],
                "commodity": source["commodity"],
                "attribute": source["attribute"],
                "unit": source["unit"],
                "year_type": source["year_type"],
                "topic": source["topic"],
            }
            for column in column_order:
                row[column] = source.get(column)
            results.append(InternationalBaselineDataData.model_validate(row))
        return results
