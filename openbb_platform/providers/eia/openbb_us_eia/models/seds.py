"""State Energy Data System (SEDS) model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_us_eia.utils.api_query import (
    EiaApiData,
    EiaApiQueryParams,
    extract_dataset_data,
    transform_dataset_data,
    transform_dataset_query,
)


class EiaSedsQueryParams(EiaApiQueryParams):
    """State Energy Data System (SEDS). Estimated production, consumption, price, and expenditure data for all energy sources by state and sector. Source: https://www.eia.gov/state/seds/seds-technical-notes-complete.php Product: SEDS (https://www.eia.gov/state/seds/)

    Source: https://www.eia.gov/opendata/browser/seds
    """

    __group__ = "seds"
    __dataset__ = "seds"
    __json_schema_extra__ = {
        "series": {"multiple_items_allowed": True},
        "state": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama",
                "alaska",
                "arizona",
                "arkansas",
                "california",
                "colorado",
                "connecticut",
                "delaware",
                "district_of_columbia",
                "federal_offshore_gulf_of_america",
                "federal_offshore_pacific",
                "florida",
                "georgia",
                "hawaii",
                "idaho",
                "illinois",
                "indiana",
                "iowa",
                "kansas",
                "kentucky",
                "louisiana",
                "maine",
                "maryland",
                "massachusetts",
                "michigan",
                "minnesota",
                "mississippi",
                "missouri",
                "montana",
                "nebraska",
                "nevada",
                "new_hampshire",
                "new_jersey",
                "new_mexico",
                "new_york",
                "north_carolina",
                "north_dakota",
                "ohio",
                "oklahoma",
                "oregon",
                "pennsylvania",
                "rhode_island",
                "south_carolina",
                "south_dakota",
                "tennessee",
                "texas",
                "united_states",
                "utah",
                "vermont",
                "virginia",
                "washington",
                "west_virginia",
                "wisconsin",
                "wyoming",
            ],
        },
    }

    series: str | None = Field(
        default=None,
        description="Unique series identifier filter. Accepts a comma-separated list of values. There are 968 valid values - use the `facet_options` endpoint to list them.",
    )
    state: str | None = Field(
        default=None,
        description="State name filter. Accepts a comma-separated list of values.",
    )


class EiaSedsData(EiaApiData):
    """State Energy Data System (SEDS). Estimated production, consumption, price, and expenditure data for all energy sources by state and sector. Source: https://www.eia.gov/state/seds/seds-technical-notes-complete.php Product: SEDS (https://www.eia.gov/state/seds/)"""

    series: str | None = Field(
        default=None,
        description="Unique series identifier code.",
    )
    series_name: str | None = Field(
        default=None,
        description="Unique series identifier name.",
    )
    state: str | None = Field(
        default=None,
        description="State name code.",
    )
    state_name: str | None = Field(
        default=None,
        description="State name name.",
    )
    value: float | None = Field(
        default=None,
        description="Value. Withheld or unavailable values return as null.",
    )
    unit: str | None = Field(
        default=None,
        description="Unit of the value.",
    )


class EiaSedsFetcher(Fetcher[EiaSedsQueryParams, list[EiaSedsData]]):
    """State Energy Data System (SEDS) fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaSedsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaSedsQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaSedsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaSedsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaSedsData]:
        """Transform the data."""
        return transform_dataset_data(EiaSedsData, query, data)
