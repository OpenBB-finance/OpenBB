"""USDA ERS County Typology Codes Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_county_typology_codes import (
    DEFAULT_VINTAGE,
    STATE_ABBRS,
    VINTAGES,
    state_options,
    vintage_options,
)
from openbb_government_us.utils.serializers import NullTokenMixin


def _code_config(header: str, hide: bool = True) -> dict:
    """Build a per-field widget config for a numeric classification code."""
    return {"headerName": header, "cellDataType": "text", "hide": hide}


class CountyTypologyCodesQueryParams(QueryParams):
    """USDA ERS County Typology Codes Query Parameters.

    Source: https://www.ers.usda.gov/data-products/county-typology-codes
    """

    __json_schema_extra__ = {
        "vintage": {
            "x-widget_config": {
                "label": "Edition",
                "value": DEFAULT_VINTAGE,
                "multiSelect": False,
                "multiple": False,
                "options": vintage_options(),
                "style": {"popupWidth": 360},
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "multiSelect": False,
                "multiple": False,
                "options": state_options(),
                "style": {"popupWidth": 260},
            },
        },
    }

    vintage: str = Field(
        default=DEFAULT_VINTAGE,
        description="Typology-codes edition to retrieve. Each edition is a"
        + " separate published vintage of the county classification, keyed by"
        + " county FIPS. Valid editions are:\n    "
        + ", ".join(VINTAGES)
        + "\n",
    )
    state: str | None = Field(
        default=None,
        description="Two-letter state postal abbreviation to scope the county"
        + " rows to a single state. If None, returns every county in the"
        + " edition. Alaska and Hawaii are absent from the 1979/1986 editions.",
    )

    @field_validator("vintage", mode="before", check_fields=False)
    @classmethod
    def _validate_vintage(cls, v):
        """Validate vintage."""
        if not v:
            return DEFAULT_VINTAGE
        vintage = v.strip() if isinstance(v, str) else v
        if vintage not in VINTAGES:
            raise OpenBBError(
                f"Invalid vintage: {vintage}. Valid vintages are: "
                + ", ".join(VINTAGES)
            )
        return vintage

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate the optional state filter."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        state = str(value).strip().upper()
        if not state:
            return None
        if state not in STATE_ABBRS:
            raise OpenBBError(
                f"Invalid state: {value}. Use a two-letter postal abbreviation,"
                + " e.g. 'TX'."
            )
        return state


class CountyTypologyCodesData(NullTokenMixin, Data):
    """USDA ERS County Typology Codes.

    One selected edition as a county lookup table: one row per county FIPS
    carrying its economic-dependence type and the metro, specialization, and
    policy classification codes published for that vintage.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS County Typology Codes",
                "$.description": "County-level economic-dependence and policy"
                " typology classifications for U.S. counties, published in"
                " successive vintages by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    fips: str = Field(
        description="County FIPS code, five digits with a leading zero.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FIPS",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    state: str | None = Field(
        default=None,
        description="Two-letter state postal abbreviation, from the FIPS prefix.",
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
        description="County name, as published in the edition.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "County",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 240,
            }
        },
    )
    metro: int | None = Field(
        default=None,
        description="Metro-nonmetro status: 1 for metropolitan, 0 for"
        + " nonmetropolitan, under the edition's own metro definition.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Metro", "cellDataType": "text"}
        },
    )
    economic_type: str | None = Field(
        default=None,
        description="Non-overlapping economic-dependence type of the county,"
        + " e.g. 'Farming', 'Mining', 'Manufacturing', 'Government',"
        + " 'Recreation', 'Services', or 'Nonspecialized'. Derived from the"
        + " edition's economic code or, for the flag-based 1989 and 1979/1986"
        + " editions, from the set economic flag.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Economic Type", "cellDataType": "text"}
        },
    )
    economic_type_code: int | None = Field(
        default=None,
        description="Numeric economic-dependence code as published, where the"
        + " edition assigns one (2025, 2015, and 2004 editions).",
        json_schema_extra={
            "x-widget_config": _code_config("Economic Type Code", hide=False)
        },
    )
    economic_type_label: str | None = Field(
        default=None,
        description="Economic-type label exactly as published, kept for the"
        + " 2015 edition (which carries a 'Maufacturing' source typo).",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Economic Type (published)",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )
    farming: int | None = Field(
        default=None,
        description="Farming specialization flag: a high-concentration flag in"
        + " the 2025 edition, a dependence flag in earlier editions."
        + " Sentinels are kept raw (99 = not available in 2025; 8/9 = metro"
        + " county in the 1989 and 1979/1986 editions).",
        json_schema_extra={"x-widget_config": _code_config("Farming", hide=False)},
    )
    mining: int | None = Field(
        default=None,
        description="Mining specialization flag, kept raw with the edition's"
        + " sentinels.",
        json_schema_extra={"x-widget_config": _code_config("Mining", hide=False)},
    )
    manufacturing: int | None = Field(
        default=None,
        description="Manufacturing specialization flag, kept raw with the"
        + " edition's sentinels.",
        json_schema_extra={
            "x-widget_config": _code_config("Manufacturing", hide=False)
        },
    )
    government: int | None = Field(
        default=None,
        description="Government specialization flag, kept raw with the"
        + " edition's sentinels.",
        json_schema_extra={"x-widget_config": _code_config("Government", hide=False)},
    )
    recreation: int | None = Field(
        default=None,
        description="Recreation flag: an economic specialization in the 2025"
        + " and 2015 editions, a nonmetro-recreation policy flag in the 2004"
        + " edition.",
        json_schema_extra={"x-widget_config": _code_config("Recreation", hide=False)},
    )
    services: int | None = Field(
        default=None,
        description="Services specialization flag, published in the 2004 and"
        + " 1989 editions.",
        json_schema_extra={"x-widget_config": _code_config("Services")},
    )
    nonspecialized: int | None = Field(
        default=None,
        description="Nonspecialized flag: the county is not dependent on any"
        + " single industry.",
        json_schema_extra={
            "x-widget_config": _code_config("Nonspecialized", hide=False)
        },
    )
    low_education: int | None = Field(
        default=None,
        description="Low-education policy flag, published in the 2025, 2015,"
        + " and 2004 editions.",
        json_schema_extra={
            "x-widget_config": _code_config("Low Education", hide=False)
        },
    )
    low_employment: int | None = Field(
        default=None,
        description="Low-employment policy flag, published in the 2025, 2015,"
        + " and 2004 editions.",
        json_schema_extra={
            "x-widget_config": _code_config("Low Employment", hide=False)
        },
    )
    population_loss: int | None = Field(
        default=None,
        description="Population-loss policy flag, published in the 2025, 2015,"
        + " and 2004 editions.",
        json_schema_extra={
            "x-widget_config": _code_config("Population Loss", hide=False)
        },
    )
    housing_stress: int | None = Field(
        default=None,
        description="Housing-stress policy flag, published in the 2025 and"
        + " 2004 editions.",
        json_schema_extra={
            "x-widget_config": _code_config("Housing Stress", hide=False)
        },
    )
    retirement_destination: int | None = Field(
        default=None,
        description="Retirement-destination policy flag, kept raw with the"
        + " edition's sentinels.",
        json_schema_extra={
            "x-widget_config": _code_config("Retirement Destination", hide=False)
        },
    )
    persistent_poverty: int | None = Field(
        default=None,
        description="Persistent-poverty policy flag, kept raw with the"
        + " edition's sentinels (-1 = not determined in the 2025 edition).",
        json_schema_extra={
            "x-widget_config": _code_config("Persistent Poverty", hide=False)
        },
    )
    persistent_child_poverty: int | None = Field(
        default=None,
        description="Persistent related-child-poverty policy flag, published"
        + " in the 2015 and 2004 editions.",
        json_schema_extra={"x-widget_config": _code_config("Persistent Child Poverty")},
    )
    federal_lands: int | None = Field(
        default=None,
        description="Federal-lands policy flag, published in the 1989 and"
        + " 1979/1986 editions.",
        json_schema_extra={"x-widget_config": _code_config("Federal Lands")},
    )
    commuting: int | None = Field(
        default=None,
        description="Commuting policy flag, published in the 1989 edition.",
        json_schema_extra={"x-widget_config": _code_config("Commuting")},
    )
    transfers_dependent: int | None = Field(
        default=None,
        description="Transfers-dependent policy flag, published in the 1989"
        + " edition.",
        json_schema_extra={"x-widget_config": _code_config("Transfers Dependent")},
    )
    rural_urban_continuum_code: int | None = Field(
        default=None,
        description="Rural-urban continuum (Beale) code, published in the"
        + " 2004, 1989, and 1979/1986 editions.",
        json_schema_extra={
            "x-widget_config": _code_config("Rural-Urban Continuum Code")
        },
    )
    urban_influence_code: int | None = Field(
        default=None,
        description="Urban-influence code, published in the 2004 edition.",
        json_schema_extra={"x-widget_config": _code_config("Urban Influence Code")},
    )
    farming_1986: int | None = Field(
        default=None,
        description="Farming specialization flag for the 1986 update carried"
        + " in the 1979/1986 editions, kept raw with sentinels.",
        json_schema_extra={"x-widget_config": _code_config("Farming (1986)")},
    )
    mining_1986: int | None = Field(
        default=None,
        description="Mining specialization flag for the 1986 update carried in"
        + " the 1979/1986 editions, kept raw with sentinels.",
        json_schema_extra={"x-widget_config": _code_config("Mining (1986)")},
    )
    manufacturing_1986: int | None = Field(
        default=None,
        description="Manufacturing specialization flag for the 1986 update"
        + " carried in the 1979/1986 editions, kept raw with sentinels.",
        json_schema_extra={"x-widget_config": _code_config("Manufacturing (1986)")},
    )
    government_1986: int | None = Field(
        default=None,
        description="Government specialization flag for the 1986 update"
        + " carried in the 1979/1986 editions, kept raw with sentinels.",
        json_schema_extra={"x-widget_config": _code_config("Government (1986)")},
    )
    nonspecialized_1986: int | None = Field(
        default=None,
        description="Nonspecialized flag for the 1986 update carried in the"
        + " 1979/1986 editions, kept raw with sentinels.",
        json_schema_extra={"x-widget_config": _code_config("Nonspecialized (1986)")},
    )


class CountyTypologyCodesFetcher(
    Fetcher[
        CountyTypologyCodesQueryParams,
        list[CountyTypologyCodesData],
    ]
):
    """Fetch USDA ERS County Typology Codes."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CountyTypologyCodesQueryParams:
        """Transform the query params."""
        return CountyTypologyCodesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CountyTypologyCodesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected edition's canonical county records."""
        from openbb_government_us.usda.utils import ers_county_typology_codes

        return await ers_county_typology_codes.afetch_vintage(query.vintage)

    @staticmethod
    def transform_data(
        query: CountyTypologyCodesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CountyTypologyCodesData]:
        """Scope the county rows to the selected state and sort by FIPS."""
        selected = [
            record
            for record in data
            if query.state is None or record.get("state") == query.state
        ]
        selected.sort(key=lambda record: record["fips"])
        return [CountyTypologyCodesData.model_validate(record) for record in selected]
