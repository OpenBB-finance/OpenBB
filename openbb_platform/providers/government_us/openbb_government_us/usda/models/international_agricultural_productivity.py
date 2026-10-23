"""USDA ERS International Agricultural Productivity Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_international_agricultural_productivity import (
    DEFAULT_COUNTRY,
    DEFAULT_GROUPING,
    DEFAULT_MEASURE,
    ENTITY_LABEL,
    GROUPINGS,
    MEASURES,
    grouping_options,
    measure_options,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix


class InternationalAgriculturalProductivityQueryParams(QueryParams):
    """International Agricultural Productivity Query Parameters.

    Source: https://www.ers.usda.gov/data-products/international-agricultural-productivity
    """

    __json_schema_extra__ = {
        "grouping": {
            "x-widget_config": {
                "label": "Grouping",
                "value": DEFAULT_GROUPING,
                "multiSelect": False,
                "multiple": False,
                "options": grouping_options(),
                "style": {"popupWidth": 320},
            },
        },
        "country": {
            "x-widget_config": {
                "label": "Country / territory",
                "type": "endpoint",
                "value": DEFAULT_COUNTRY,
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/ag_productivity_countries",
                "optionsParams": {"grouping": "$grouping"},
                "style": {"popupWidth": 360},
            },
        },
        "measure": {
            "x-widget_config": {
                "label": "Measure",
                "value": DEFAULT_MEASURE,
                "multiSelect": False,
                "multiple": False,
                "options": measure_options(),
                "style": {"popupWidth": 300},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    grouping: str = Field(
        default=DEFAULT_GROUPING,
        description="Grouping that scopes the country selector into buckets"
        + " derived from the entity's region, income level, or aggregate type."
        + " It scopes the dropdown only; the data is selected by country."
        + " Valid groupings are:\n    "
        + ", ".join(GROUPINGS)
        + "\n",
    )
    country: int = Field(
        default=DEFAULT_COUNTRY,
        description="Country, territory, region, income group, or aggregate to"
        + " retrieve, as its unique dataset order. The order disambiguates"
        + " entities sharing a name, e.g. the country 'China' (81) from the"
        + " income aggregate 'China' (227). Defaults to 220, the world.",
    )
    measure: str = Field(
        default=DEFAULT_MEASURE,
        description="Measure family spread into the wide value columns."
        + " 'productivity_indices' emits the seven 2015=100 indices;"
        + " 'physical_quantities' emits the twelve output and input quantities"
        + " in their published units. Valid measures are:\n    "
        + ", ".join(MEASURES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, from 1961."
        + " If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, up to 2023."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("grouping", mode="before", check_fields=False)
    @classmethod
    def _validate_grouping(cls, v):
        """Validate grouping."""
        if not v:
            return DEFAULT_GROUPING
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in GROUPINGS:
            raise OpenBBError(
                f"Invalid grouping: {value}. Valid groupings are: "
                + ", ".join(GROUPINGS)
            )
        return value

    @field_validator("measure", mode="before", check_fields=False)
    @classmethod
    def _validate_measure(cls, v):
        """Validate measure."""
        if not v:
            return DEFAULT_MEASURE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in MEASURES:
            raise OpenBBError(
                f"Invalid measure: {value}. Valid measures are: " + ", ".join(MEASURES)
            )
        return value

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def _validate_country(cls, v):
        """Validate country."""
        if v is None or v == "":
            return DEFAULT_COUNTRY
        value = v[0] if isinstance(v, (list, tuple)) else v
        try:
            order = int(str(value).strip())
        except (TypeError, ValueError) as error:
            raise OpenBBError(f"Invalid country: {value}.") from error
        if order not in ENTITY_LABEL:
            raise OpenBBError(
                f"Invalid country order: {order}. It is not a published entity."
            )
        return order


class InternationalAgriculturalProductivityData(NullTokenMixin, Data):
    """International Agricultural Productivity Data.

    One selected entity pivoted to the ERS wide layout: each row is a year and
    the selected measure family spreads into value columns, either the seven
    2015=100 productivity indices or the twelve physical output and input
    quantities, whose set depends on the measure.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS International Agricultural Productivity",
                "$.description": "Agricultural total factor productivity indices,"
                " output and input quantity indices, and the underlying physical"
                " output and input quantities for countries, territories, regions,"
                " income groups, and the world, published by the USDA Economic"
                " Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: int = Field(
        description="Year of the observation.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )


class InternationalAgriculturalProductivityFetcher(
    Fetcher[
        InternationalAgriculturalProductivityQueryParams,
        list[InternationalAgriculturalProductivityData],
    ]
):
    """Fetch USDA ERS International Agricultural Productivity."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> InternationalAgriculturalProductivityQueryParams:
        """Transform the query params."""
        return InternationalAgriculturalProductivityQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: InternationalAgriculturalProductivityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected entity's long-format observation records."""
        from openbb_government_us.usda.utils import (
            ers_international_agricultural_productivity,
        )

        return await ers_international_agricultural_productivity.afetch_entity(
            query.country
        )

    @staticmethod
    def transform_data(
        query: InternationalAgriculturalProductivityQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[InternationalAgriculturalProductivityData]:
        """Pivot the entity's records into the wide year-by-measure layout."""
        columns = MEASURES[query.measure]["columns"]
        header_by_variable = {variable: header for variable, header in columns}
        kept: list[dict] = []
        for record in data:
            if record["variable"] not in header_by_variable:
                continue
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            kept.append(record)
        if not kept:
            raise EmptyDataError("No records match the given filters.")
        present = {record["variable"] for record in kept}
        ordered_headers = [
            header for variable, header in columns if variable in present
        ]
        by_year: dict[int, dict] = {}
        for record in kept:
            row = by_year.setdefault(record["year"], {})
            row[header_by_variable[record["variable"]]] = record["value"]
        results: list[InternationalAgriculturalProductivityData] = []
        for year in sorted(by_year):
            values = by_year[year]
            row = {"year": year}
            for header in ordered_headers:
                row[header] = values.get(header)
            results.append(
                InternationalAgriculturalProductivityData.model_validate(row)
            )
        return results
