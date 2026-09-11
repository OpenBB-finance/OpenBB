"""Urban Influence Codes Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.ers_urban_influence_codes import (
    STATE_LABELS,
    VINTAGE_LABELS,
    VINTAGES,
    allowed_states,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_VINTAGE = "2024"


class UrbanInfluenceCodesQueryParams(QueryParams):
    """Urban Influence Codes Query Parameters.

    Source: https://www.ers.usda.gov/data-products/urban-influence-codes
    """

    __json_schema_extra__ = {
        "vintage": {
            "x-widget_config": {
                "label": "Vintage",
                "value": DEFAULT_VINTAGE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in VINTAGE_LABELS.items()
                ],
                "style": {"popupWidth": 320},
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/urban_influence_code_states",
                "optionsParams": {"vintage": "$vintage"},
                "style": {"popupWidth": 280},
            },
        },
    }

    vintage: str = Field(
        default=DEFAULT_VINTAGE,
        description="Classification vintage to retrieve; each vintage is a"
        + " separate published file. The 2024 revision uses a nine-code scheme,"
        + " 2013 and 2003 use a twelve-code scheme, and 1993 uses a different"
        + " nine-code scheme. Valid vintages are:\n    "
        + ", ".join(VINTAGES)
        + "\n",
    )
    state: str | None = Field(
        default=None,
        description="State to retrieve, as a two-letter code, scoping the rows"
        + " to one state's counties. If None, every county in the vintage is"
        + " returned. The published state set varies by vintage: the 2024"
        + " revision adds the American Samoa, Guam, Northern Mariana Islands,"
        + " Puerto Rico, and U.S. Virgin Islands territories, 2013 and 2003 add"
        + " Puerto Rico, and 1993 covers the states and the District of Columbia"
        + " only.",
    )

    @field_validator("vintage", mode="before", check_fields=False)
    @classmethod
    def _validate_vintage(cls, v):
        """Validate vintage."""
        if not v:
            return DEFAULT_VINTAGE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in VINTAGES:
            raise OpenBBError(
                f"Invalid vintage: {value}. Valid vintages are: " + ", ".join(VINTAGES)
            )
        return value

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate state."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().upper()
        if not value:
            return None
        if value not in STATE_LABELS:
            raise OpenBBError(
                f"Invalid state: {value}. Valid states are: " + ", ".join(STATE_LABELS)
            )
        return value

    @model_validator(mode="after")
    def _validate_state_for_vintage(self):
        """Validate that the state is published for the selected vintage."""
        if self.state is not None and self.state not in allowed_states(self.vintage):
            raise OpenBBError(
                f"Invalid state '{self.state}' for vintage '{self.vintage}'."
                f" This vintage is published for: "
                + ", ".join(allowed_states(self.vintage))
            )
        return self


class UrbanInfluenceCodesData(NullTokenMixin, Data):
    """Urban Influence Codes Data.

    A county-level lookup classifying every U.S. county by metropolitan status,
    size, and adjacency, published by USDA ERS. Each row is one county FIPS,
    carrying its classification code, the code's published description, and the
    published population and population density.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Urban Influence Codes",
                "$.description": "A county-level classification of U.S. counties"
                " by metropolitan status, size, and adjacency to metro and micro"
                " areas, published in the 1993, 2003, 2013, and 2024 vintages by"
                " the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    fips: str = Field(
        description="Five-digit county FIPS code, zero-padded.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FIPS",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 110,
            }
        },
    )
    state: str = Field(
        description="Two-letter state or territory postal code of the county.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    county_name: str = Field(
        description="County or municipio name, as published.",
        json_schema_extra={
            "x-widget_config": {"headerName": "County", "pinned": "left"}
        },
    )
    urban_influence_code: str | None = Field(
        default=None,
        description="Urban Influence Code of the county, as an ordinal string:"
        + " one to nine for the 2024 and 1993 vintages, one to twelve for the"
        + " 2013 and 2003 vintages.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "UIC",
                "cellDataType": "text",
                "maxWidth": 90,
            }
        },
    )
    description: str | None = Field(
        default=None,
        description="Published description of the county's Urban Influence Code.",
        json_schema_extra={"x-widget_config": {"headerName": "Description"}},
    )
    population: int | float | None = Field(
        default=None,
        description="Published population count of the county; the 2020 census"
        + " for the 2024 vintage, the 2010 census for 2013, and the 2000 census"
        + " for the 2003 and 1993 vintages.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Population", "cellDataType": "number"}
        },
    )
    population_density: float | None = Field(
        default=None,
        description="Published population density in persons per square mile,"
        + " from the 2000 census. Populated only for the 2003 and 1993 vintages;"
        + " the 2024 and 2013 files carry no density.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Persons per sq. mile",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )


class UrbanInfluenceCodesFetcher(
    Fetcher[
        UrbanInfluenceCodesQueryParams,
        list[UrbanInfluenceCodesData],
    ]
):
    """Fetch USDA ERS Urban Influence Codes."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> UrbanInfluenceCodesQueryParams:
        """Transform the query params."""
        return UrbanInfluenceCodesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UrbanInfluenceCodesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected vintage's county records."""
        from openbb_government_us.usda.utils import ers_urban_influence_codes

        return await ers_urban_influence_codes.afetch_vintage(query.vintage)

    @staticmethod
    def transform_data(
        query: UrbanInfluenceCodesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[UrbanInfluenceCodesData]:
        """Filter the lookup to the selected state and sort by county FIPS."""
        rows = (
            data
            if query.state is None
            else [row for row in data if row["state"] == query.state]
        )
        if not rows:
            raise EmptyDataError("No records match the given filters.")
        rows = sorted(rows, key=lambda row: row["fips"])
        return [UrbanInfluenceCodesData.model_validate(row) for row in rows]
