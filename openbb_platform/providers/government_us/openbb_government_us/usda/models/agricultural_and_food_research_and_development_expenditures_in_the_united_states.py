"""USDA ERS Agricultural and Food R&D Expenditures Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_agricultural_and_food_research_and_development_expenditures_in_the_united_states import (  # noqa: E501
    MEASURES,
    SERIES_ORDER,
)
from openbb_government_us.utils.serializers import NullTokenMixin

Measure = Literal["nominal", "real"]

DEFAULT_MEASURE = "real"


def _number(header: str) -> dict:
    """Build a numeric column config for one series field."""
    return {"x-widget_config": {"headerName": header, "cellDataType": "number"}}


class AgriculturalAndFoodRdExpendituresQueryParams(QueryParams):
    """USDA ERS Agricultural and Food R&D Expenditures Query Parameters.

    Source: https://www.ers.usda.gov/data-products/agricultural-and-food-research-and-development-expenditures-in-the-united-states
    """

    __json_schema_extra__ = {
        "measure": {
            "x-widget_config": {
                "label": "Measure",
                "multiSelect": False,
                "multiple": False,
                "value": DEFAULT_MEASURE,
                "options": [
                    {"label": "Real (constant 2022 dollars)", "value": "real"},
                    {"label": "Nominal (current dollars)", "value": "nominal"},
                ],
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    measure: Measure = Field(
        default=DEFAULT_MEASURE,
        description="Measure to retrieve, selecting which values fill the R&D"
        + " series columns. 'real' is inflation-adjusted constant 2022 U.S."
        + " dollars; 'nominal' is current U.S. dollars. Both are in millions."
        + " The R&D price index column is the same under either measure.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " observation year. If None, returns from 1970.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " observation year. If None, returns up to the most recent year.",
    )

    @field_validator("measure", mode="before", check_fields=False)
    @classmethod
    def _validate_measure(cls, v):
        """Validate measure."""
        if not v:
            return DEFAULT_MEASURE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().lower()
        if value not in MEASURES:
            raise OpenBBError(
                f"Invalid measure: {value}. Valid measures are: " + ", ".join(MEASURES)
            )
        return value


class AgriculturalAndFoodRdExpendituresData(NullTokenMixin, Data):
    """USDA ERS Agricultural and Food R&D Expenditures Data.

    One row per year, with the public and private agricultural and food R&D
    series spread into a fixed set of value columns filled by the selected
    measure, alongside the measure-agnostic R&D price index.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Agricultural and Food R&D Expenditures",
                "$.description": "Public and private agricultural and food"
                " research and development expenditures in the United States,"
                " in current and constant dollars with the R&D price index,"
                " published by the USDA Economic Research Service.",
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
    public_total: float | None = Field(
        default=None,
        description="Total public agricultural and food R&D expenditures, in"
        + " millions of dollars under the selected measure.",
        json_schema_extra=_number("Public total"),
    )
    public_usda_intramural: float | None = Field(
        default=None,
        description="Public agricultural and food R&D performed by USDA"
        + " intramural agencies, in millions of dollars under the selected"
        + " measure.",
        json_schema_extra=_number("USDA intramural"),
    )
    public_state_universities: float | None = Field(
        default=None,
        description="Public agricultural and food R&D performed by State"
        + " universities and cooperating institutions, in millions of dollars"
        + " under the selected measure.",
        json_schema_extra=_number("State universities"),
    )
    private_input_industries: float | None = Field(
        default=None,
        description="Private agriculture input industries R&D, in millions of"
        + " dollars under the selected measure. Discontinued after 2014.",
        json_schema_extra=_number("Private input industries"),
    )
    private_food_industry: float | None = Field(
        default=None,
        description="Private food industry R&D, in millions of dollars under"
        + " the selected measure.",
        json_schema_extra=_number("Private food industry"),
    )
    rd_price_index: float | None = Field(
        default=None,
        description="R&D price index (2022 = 100) used to deflate the nominal"
        + " series, the same under either measure.",
        json_schema_extra=_number("R&D price index"),
    )


class AgriculturalAndFoodRdExpendituresFetcher(
    Fetcher[
        AgriculturalAndFoodRdExpendituresQueryParams,
        list[AgriculturalAndFoodRdExpendituresData],
    ]
):
    """Fetch USDA ERS Agricultural and Food R&D Expenditures."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> AgriculturalAndFoodRdExpendituresQueryParams:
        """Transform the query params."""
        return AgriculturalAndFoodRdExpendituresQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AgriculturalAndFoodRdExpendituresQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the long-format R&D expenditure records."""
        from openbb_government_us.usda.utils import (
            ers_agricultural_and_food_research_and_development_expenditures_in_the_united_states as util,
        )

        return await util.afetch_records()

    @staticmethod
    def transform_data(
        query: AgriculturalAndFoodRdExpendituresQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AgriculturalAndFoodRdExpendituresData]:
        """Pivot the selected measure's series into columns, one row per year."""
        pivoted: dict[int, dict] = {}
        for record in data:
            if record["measure"] not in (query.measure, None):
                continue
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            row = pivoted.setdefault(year, {"year": year})
            row[record["series"]] = record["value"]
        if not pivoted:
            raise EmptyDataError("No records match the given filters.")
        results: list[AgriculturalAndFoodRdExpendituresData] = []
        for year in sorted(pivoted):
            row = pivoted[year]
            ordered = {"year": year}
            for series in SERIES_ORDER:
                if series in row:
                    ordered[series] = row[series]
            results.append(
                AgriculturalAndFoodRdExpendituresData.model_validate(ordered)
            )
        return results
