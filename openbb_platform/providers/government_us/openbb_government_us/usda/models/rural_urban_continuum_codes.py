"""USDA ERS Rural-Urban Continuum Codes Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_rural_urban_continuum_codes import (
    DEFAULT_VINTAGE,
    STATE_NAMES,
    VINTAGE_OPTIONS,
    VINTAGES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix


class RuralUrbanContinuumCodesQueryParams(QueryParams):
    """USDA ERS Rural-Urban Continuum Codes Query Parameters.

    Source: https://www.ers.usda.gov/data-products/rural-urban-continuum-codes
    """

    __json_schema_extra__ = {
        "vintage": {
            "x-widget_config": {
                "label": "Vintage",
                "value": DEFAULT_VINTAGE,
                "multiSelect": False,
                "multiple": False,
                "options": VINTAGE_OPTIONS,
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/rural_urban_continuum_states",
                "optionsParams": {"vintage": "$vintage"},
                "style": {"popupWidth": 280},
            },
        },
    }

    vintage: str = Field(
        default=DEFAULT_VINTAGE,
        description="Classification vintage to retrieve. Each vintage is a"
        + " separate county lookup published in that year, carrying the RUCC"
        + " code, its vintage-specific description, and the county population;"
        + " codes and descriptions are vintage-specific because the"
        + " urbanization thresholds changed over time. Valid vintages are:\n    "
        + ", ".join(VINTAGES)
        + "\n",
    )
    state: str | None = Field(
        default=None,
        description="Two-letter state or territory code to scope the county"
        + " rows to a single state. If None, returns every county of the"
        + " vintage. The available states vary by vintage: the 2023 and 2013"
        + " vintages include the AS, GU, MP, VI, PR, and DC territories, and the"
        + " 2003 vintage adds PR to the fifty states and DC.",
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
        """Validate and normalize the optional state filter."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().upper()
        if value not in STATE_NAMES:
            raise OpenBBError(
                f"Invalid state: {value}. Valid states are: " + ", ".join(STATE_NAMES)
            )
        return value


class RuralUrbanContinuumCodesData(NullTokenMixin, Data):
    """USDA ERS Rural-Urban Continuum Codes Data.

    One selected vintage as a county lookup: each row is a county or
    county-equivalent area, carrying its FIPS code, state, name, RUCC
    classification code, the code's vintage-specific description, and the
    published population.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Rural-Urban Continuum Codes",
                "$.description": "County-level Rural-Urban Continuum Codes"
                " (RUCC) classifying U.S. counties by metropolitan status and"
                " degree of urbanization, published in vintages by the USDA"
                " Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    fips: str = Field(
        description="Five-digit county FIPS code, with leading zeros preserved.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FIPS",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 100,
            }
        },
    )
    state: str | None = Field(
        default=None,
        description="Two-letter state or territory postal code.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    county_name: str | None = Field(
        default=None,
        description="County or county-equivalent area name, as published.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "County / area",
                "pinned": "left",
                "minWidth": 200,
            }
        },
    )
    rucc_code: str | None = Field(
        default=None,
        description="Rural-Urban Continuum Code for the vintage: 1 to 3 for"
        + " metro counties and 4 to 9 for nonmetro counties.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "RUCC code",
                "cellDataType": "text",
                "maxWidth": 120,
            }
        },
    )
    description: str | None = Field(
        default=None,
        description="Vintage-specific description of the RUCC code, carried per"
        + " row from the source.",
        json_schema_extra={"x-widget_config": {"headerName": "Description"}},
    )
    population: int | None = Field(
        default=None,
        description="Published county population for the vintage's reference"
        + " census, as a full count.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Population",
                "cellDataType": "number",
                "maxWidth": 140,
            }
        },
    )


class RuralUrbanContinuumCodesFetcher(
    Fetcher[
        RuralUrbanContinuumCodesQueryParams,
        list[RuralUrbanContinuumCodesData],
    ]
):
    """Fetch USDA ERS Rural-Urban Continuum Codes."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> RuralUrbanContinuumCodesQueryParams:
        """Transform the query params."""
        return RuralUrbanContinuumCodesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: RuralUrbanContinuumCodesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected vintage's county-lookup records."""
        from openbb_government_us.usda.utils import ers_rural_urban_continuum_codes

        return await ers_rural_urban_continuum_codes.afetch_vintage(query.vintage)

    @staticmethod
    def transform_data(
        query: RuralUrbanContinuumCodesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[RuralUrbanContinuumCodesData]:
        """Filter the records to the chosen state and sort them by FIPS code."""
        rows = [
            record
            for record in data
            if query.state is None or record["state"] == query.state
        ]
        if not rows:
            raise EmptyDataError("No records match the given filters.")
        rows.sort(key=lambda record: record["fips"])
        return [
            RuralUrbanContinuumCodesData.model_validate(
                {
                    "fips": record["fips"],
                    "state": record["state"],
                    "county_name": record["county_name"],
                    "rucc_code": record["rucc_code"],
                    "description": record["description"],
                    "population": record["population"],
                }
            )
            for record in rows
        ]
