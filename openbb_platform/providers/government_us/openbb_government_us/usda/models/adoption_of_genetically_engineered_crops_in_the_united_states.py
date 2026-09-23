"""USDA ERS Adoption of Genetically Engineered Crops Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_adoption_of_genetically_engineered_crops_in_the_united_states import (  # noqa: E501
    CROP_STATES,
    CROPS,
    DEFAULT_CROP,
    DEFAULT_STATE,
    STATE_CANON,
    STATES_ALL,
    crop_options,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix


class AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesQueryParams(QueryParams):
    """USDA ERS Adoption of Genetically Engineered Crops Query Parameters.

    Source: https://www.ers.usda.gov/data-products/adoption-of-genetically-engineered-crops-in-the-united-states
    """

    __json_schema_extra__ = {
        "crop": {
            "x-widget_config": {
                "label": "Crop",
                "value": DEFAULT_CROP,
                "multiSelect": False,
                "multiple": False,
                "options": crop_options(),
            },
        },
        "state": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "State",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "value": DEFAULT_STATE,
                "optionsEndpoint": f"{api_prefix}/usda/ge_crop_states",
                "optionsParams": {"crop": "$crop"},
                "style": {"popupWidth": 300},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    crop: str = Field(
        default=DEFAULT_CROP,
        description="Crop whose sheet is retrieved. The crop selects the trait"
        + " columns and the state option list. Corn and cotton publish four"
        + " trait columns (Bt only, HT only, Stacked, All GE); soybeans publish"
        + " only HT only and All GE. Valid crops are:\n    "
        + ", ".join(CROPS)
        + "\n",
    )
    state: str | None = Field(
        default=DEFAULT_STATE,
        description="State(s) to retrieve, as a comma-separated list of names."
        + " The published estimating-program states vary by crop; 'United"
        + " States' is the national total and 'Other States' is the residual"
        + " aggregate. If None, defaults to 'United States'.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " observation year. If None, returns from 2000, the first year of the"
        + " series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " observation year. If None, returns up to the most recent year.",
    )

    @field_validator("crop", mode="before", check_fields=False)
    @classmethod
    def _validate_crop(cls, v):
        """Validate crop."""
        if not v:
            return DEFAULT_CROP
        crop = v.strip() if isinstance(v, str) else v
        if crop not in CROPS:
            raise OpenBBError(
                f"Invalid crop: {crop}. Valid crops are: " + ", ".join(CROPS)
            )
        return crop

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate and canonicalize the state filter."""
        if not v:
            return DEFAULT_STATE
        tokens = v.split(",") if isinstance(v, str) else list(v)
        canonical: list[str] = []
        unknown: list[str] = []
        for token in tokens:
            text = str(token).strip()
            if not text:
                continue
            match = STATE_CANON.get(text.casefold())
            if match is None:
                unknown.append(text)
            else:
                canonical.append(match)
        if unknown:
            raise OpenBBError(
                f"Invalid state(s): {', '.join(unknown)}. Valid states are: "
                + ", ".join(STATES_ALL)
            )
        return ",".join(canonical) if canonical else DEFAULT_STATE


class AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesData(NullTokenMixin, Data):
    """USDA ERS Adoption of Genetically Engineered Crops Data.

    One crop's genetically engineered planting shares pivoted to a wide layout:
    the years stay in the rows while the crop's GE trait categories spread into
    percent columns, whose set is four for corn and upland cotton and two for
    soybeans.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Adoption of Genetically Engineered Crops",
                "$.description": "Annual share of planted acres in genetically"
                " engineered varieties of corn, upland cotton, and soybeans, by"
                " trait and by State, published by the USDA Economic Research"
                " Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    state: str = Field(
        description="State of the observation, or 'United States' for the"
        + " national total and 'Other States' for the residual aggregate.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State",
                "cellDataType": "text",
                "pinned": "left",
            }
        },
    )
    year: int = Field(
        description="Year of the observation.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "number",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )


class AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesFetcher(
    Fetcher[
        AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesQueryParams,
        list[AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesData],
    ]
):
    """Fetch USDA ERS Adoption of Genetically Engineered Crops in the United States."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesQueryParams:
        """Transform the query params."""
        return AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesQueryParams(
            **params
        )

    @staticmethod
    async def aextract_data(
        query: AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected crop's long-format rows."""
        from openbb_government_us.usda.utils import (
            ers_adoption_of_genetically_engineered_crops_in_the_united_states as ers,
        )

        return await ers.afetch_crop(query.crop)

    @staticmethod
    def transform_data(
        query: AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesData]:
        """Pivot the long-format rows into the wide trait-by-year layout."""
        traits = CROPS[query.crop]["traits"]
        selected = (
            set(query.state.split(",")) if query.state else set(CROP_STATES[query.crop])
        )
        grouped: dict[tuple, dict] = {}
        for record in data:
            state = record["state"]
            if state not in selected:
                continue
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            key = (state, year)
            cell = grouped.get(key)
            if cell is None:
                cell = {}
                grouped[key] = cell
            cell[record["trait"]] = record["value"]
        results: list[AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesData] = []
        for state, year in sorted(grouped):
            row = {"state": state, "year": year}
            for trait in traits:
                row[trait] = grouped[(state, year)].get(trait)
            results.append(
                AdoptionOfGeneticallyEngineeredCropsInTheUnitedStatesData.model_validate(
                    row
                )
            )
        return results
