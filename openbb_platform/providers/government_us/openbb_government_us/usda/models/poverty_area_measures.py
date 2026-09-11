"""USDA ERS Poverty Area Measures Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_poverty_area_measures import (
    DEFAULT_EDITION,
    EDITION_OPTIONS,
    EDITIONS,
    LEVEL_OPTIONS,
    LEVELS,
    STATE_NAMES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix


def _flag_config(header: str, hide: bool = False) -> dict:
    """Build a per-field widget config for a poverty-area classification flag."""
    config: dict[str, Any] = {"headerName": header, "cellDataType": "text"}
    if hide:
        config["hide"] = True
    return config


class PovertyAreaMeasuresQueryParams(QueryParams):
    """USDA ERS Poverty Area Measures Query Parameters.

    Source: https://www.ers.usda.gov/data-products/poverty-area-measures
    """

    __json_schema_extra__ = {
        "edition": {
            "x-widget_config": {
                "label": "Edition",
                "value": DEFAULT_EDITION,
                "multiSelect": False,
                "multiple": False,
                "options": EDITION_OPTIONS,
                "style": {"popupWidth": 300},
            },
        },
        "level": {
            "x-widget_config": {
                "label": "Geography Level",
                "value": "county",
                "multiSelect": False,
                "multiple": False,
                "options": LEVEL_OPTIONS,
                "style": {"popupWidth": 240},
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/poverty_area_measures_states",
                "optionsParams": {"edition": "$edition"},
                "style": {"popupWidth": 260},
            },
        },
    }

    edition: str = Field(
        default=DEFAULT_EDITION,
        description="Published edition to retrieve. Each edition is a separate"
        + " release of the poverty-area classification, differing in census-tract"
        + " geography, metro/Beale/RUCA vintage, and the most recent ACS"
        + " measurement periods carried. Valid editions are:\n    "
        + ", ".join(EDITIONS)
        + "\n",
    )
    level: str = Field(
        default="county",
        description="Geographic level of the lookup. 'county' returns one row"
        + " per county FIPS reading the county classification flags; 'tract'"
        + " returns one row per census tract reading the tract flags. Valid"
        + " levels are: "
        + ", ".join(LEVELS)
        + ".",
    )
    state: str | None = Field(
        default=None,
        description="Two-letter state postal abbreviation to scope the rows to a"
        + " single state. If None, returns every area in the edition. At tract"
        + " level the state filter is the primary usability lever.",
    )

    @field_validator("edition", mode="before", check_fields=False)
    @classmethod
    def _validate_edition(cls, v):
        """Validate the edition."""
        if not v:
            return DEFAULT_EDITION
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in EDITIONS:
            raise OpenBBError(
                f"Invalid edition: {value}. Valid editions are: " + ", ".join(EDITIONS)
            )
        return value

    @field_validator("level", mode="before", check_fields=False)
    @classmethod
    def _validate_level(cls, v):
        """Validate the geography level."""
        if not v:
            return "county"
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().lower()
        if value not in LEVELS:
            raise OpenBBError(
                f"Invalid level: {value}. Valid levels are: " + ", ".join(LEVELS)
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
        if not value:
            return None
        if value not in STATE_NAMES:
            raise OpenBBError(
                f"Invalid state: {value}. Valid states are: " + ", ".join(STATE_NAMES)
            )
        return value


class PovertyAreaMeasuresData(NullTokenMixin, Data):
    """USDA ERS Poverty Area Measures.

    One selected edition as a geographic lookup: each row is a county or census
    tract carrying the poverty-area classification flags (high-poverty,
    extreme-poverty, persistent-poverty, and enduring-poverty) across the
    measurement periods, plus the identity and geography columns. Flags are kept
    raw: -1 marks not available, 0 not classified, 1 classified; enduring
    poverty is a 0-3 category.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Poverty Area Measures",
                "$.description": "County- and census-tract-level poverty-area"
                " classifications (high-poverty, extreme-poverty,"
                " persistent-poverty, and enduring-poverty flags) for U.S. areas,"
                " published in successive editions by the USDA Economic Research"
                " Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    fips: str = Field(
        description="Area FIPS code of the row, with leading zeros preserved: the"
        + " five-digit county FIPS at the county level, or the eleven-digit"
        + " census-tract FIPS at the tract level.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "FIPS",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 130,
            }
        },
    )
    state: str | None = Field(
        default=None,
        description="Two-letter state postal abbreviation.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 80,
            }
        },
    )
    county_name: str | None = Field(
        default=None,
        description="County name with its state, as published.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "County",
                "cellDataType": "text",
                "pinned": "left",
                "minWidth": 200,
            }
        },
    )
    metro_nonmetro: int | None = Field(
        default=None,
        description="Metro-nonmetro status of the county: 1 metropolitan, 0"
        + " nonmetropolitan, under the edition's metro definition vintage.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Metro", "cellDataType": "text"}
        },
    )
    rucc_code: int | None = Field(
        default=None,
        description="Rural-Urban Continuum (Beale) code of the county, 1 to 9,"
        + " for the edition's Beale vintage.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Beale (RUCC)", "cellDataType": "text"}
        },
    )
    region: int | None = Field(
        default=None,
        description="Census region code: 1 Northeast, 2 Midwest, 3 South, 4 West.",
        json_schema_extra={"x-widget_config": _flag_config("Region", hide=True)},
    )
    subregion: int | None = Field(
        default=None,
        description="ERS subregion code, 1 to 9.",
        json_schema_extra={"x-widget_config": _flag_config("ERS Subregion", hide=True)},
    )
    tract_fips: str | None = Field(
        default=None,
        description="Eleven-digit census-tract FIPS code; populated at the tract"
        + " level only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Tract FIPS",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )
    tract: str | None = Field(
        default=None,
        description="Census-tract number as published; populated at the tract"
        + " level only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Tract",
                "cellDataType": "text",
                "hide": True,
            }
        },
    )
    tract_name: str | None = Field(
        default=None,
        description="Census-tract name; populated at the tract level only.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Tract Name",
                "cellDataType": "text",
                "hide": True,
                "minWidth": 200,
            }
        },
    )
    ruca_code: int | None = Field(
        default=None,
        description="Rural-Urban Commuting Area code of the tract for the"
        + " edition's RUCA vintage; populated at the tract level only.",
        json_schema_extra={"x-widget_config": _flag_config("RUCA", hide=True)},
    )
    bna: int | None = Field(
        default=None,
        description="Block-numbering-area flag: 1 if the tract is a"
        + " block-numbering area; populated at the tract level only.",
        json_schema_extra={"x-widget_config": _flag_config("BNA Tract", hide=True)},
    )
    high_poverty_1960: int | None = Field(
        default=None,
        description="High-poverty flag for 1960: 1 if the poverty rate was 20"
        + " percent or higher, 0 if below, -1 if not available.",
        json_schema_extra={
            "x-widget_config": _flag_config("High Poverty 1960", hide=True)
        },
    )
    high_poverty_1970: int | None = Field(
        default=None,
        description="High-poverty flag for 1970: 1 if the poverty rate was 20"
        + " percent or higher, 0 if below, -1 if not available.",
        json_schema_extra={"x-widget_config": _flag_config("High Poverty 1970")},
    )
    high_poverty_1980: int | None = Field(
        default=None,
        description="High-poverty flag for 1980: 1 if the poverty rate was 20"
        + " percent or higher, 0 if below, -1 if not available.",
        json_schema_extra={"x-widget_config": _flag_config("High Poverty 1980")},
    )
    high_poverty_1990: int | None = Field(
        default=None,
        description="High-poverty flag for 1990: 1 if the poverty rate was 20"
        + " percent or higher, 0 if below, -1 if not available.",
        json_schema_extra={"x-widget_config": _flag_config("High Poverty 1990")},
    )
    high_poverty_2000: int | None = Field(
        default=None,
        description="High-poverty flag for 2000: 1 if the poverty rate was 20"
        + " percent or higher, 0 if below, -1 if not available.",
        json_schema_extra={"x-widget_config": _flag_config("High Poverty 2000")},
    )
    high_poverty_2007_11: int | None = Field(
        default=None,
        description="High-poverty flag for the 2007-11 ACS period: 1 if the"
        + " poverty rate was 20 percent or higher, 0 if below, -1 if not"
        + " available.",
        json_schema_extra={"x-widget_config": _flag_config("High Poverty 2007-11")},
    )
    high_poverty_2015_19: int | None = Field(
        default=None,
        description="High-poverty flag for the 2015-19 ACS period: 1 if the"
        + " poverty rate was 20 percent or higher, 0 if below, -1 if not"
        + " available. Present in the 2022 and 2023 editions.",
        json_schema_extra={
            "x-widget_config": _flag_config("High Poverty 2015-19", hide=True)
        },
    )
    high_poverty_2017_21: int | None = Field(
        default=None,
        description="High-poverty flag for the 2017-21 ACS period: 1 if the"
        + " poverty rate was 20 percent or higher, 0 if below, -1 if not"
        + " available. Present in the 2023 and 2025 editions.",
        json_schema_extra={
            "x-widget_config": _flag_config("High Poverty 2017-21", hide=True)
        },
    )
    high_poverty_2018_22: int | None = Field(
        default=None,
        description="High-poverty flag for the 2018-22 ACS period: 1 if the"
        + " poverty rate was 20 percent or higher, 0 if below, -1 if not"
        + " available. Present in the 2025 edition.",
        json_schema_extra={
            "x-widget_config": _flag_config("High Poverty 2018-22", hide=True)
        },
    )
    high_poverty_2019_23: int | None = Field(
        default=None,
        description="High-poverty flag for the 2019-23 ACS period: 1 if the"
        + " poverty rate was 20 percent or higher, 0 if below, -1 if not"
        + " available. Present in the 2025 edition.",
        json_schema_extra={
            "x-widget_config": _flag_config("High Poverty 2019-23", hide=True)
        },
    )
    extreme_poverty_1960: int | None = Field(
        default=None,
        description="Extreme-poverty flag for 1960: 1 if the poverty rate was 40"
        + " percent or higher, 0 if below, -1 if not available.",
        json_schema_extra={
            "x-widget_config": _flag_config("Extreme Poverty 1960", hide=True)
        },
    )
    extreme_poverty_1970: int | None = Field(
        default=None,
        description="Extreme-poverty flag for 1970: 1 if the poverty rate was 40"
        + " percent or higher, 0 if below, -1 if not available.",
        json_schema_extra={"x-widget_config": _flag_config("Extreme Poverty 1970")},
    )
    extreme_poverty_1980: int | None = Field(
        default=None,
        description="Extreme-poverty flag for 1980: 1 if the poverty rate was 40"
        + " percent or higher, 0 if below, -1 if not available.",
        json_schema_extra={"x-widget_config": _flag_config("Extreme Poverty 1980")},
    )
    extreme_poverty_1990: int | None = Field(
        default=None,
        description="Extreme-poverty flag for 1990: 1 if the poverty rate was 40"
        + " percent or higher, 0 if below, -1 if not available.",
        json_schema_extra={"x-widget_config": _flag_config("Extreme Poverty 1990")},
    )
    extreme_poverty_2000: int | None = Field(
        default=None,
        description="Extreme-poverty flag for 2000: 1 if the poverty rate was 40"
        + " percent or higher, 0 if below, -1 if not available.",
        json_schema_extra={"x-widget_config": _flag_config("Extreme Poverty 2000")},
    )
    extreme_poverty_2007_11: int | None = Field(
        default=None,
        description="Extreme-poverty flag for the 2007-11 ACS period: 1 if the"
        + " poverty rate was 40 percent or higher, 0 if below, -1 if not"
        + " available.",
        json_schema_extra={"x-widget_config": _flag_config("Extreme Poverty 2007-11")},
    )
    extreme_poverty_2015_19: int | None = Field(
        default=None,
        description="Extreme-poverty flag for the 2015-19 ACS period: 1 if the"
        + " poverty rate was 40 percent or higher, 0 if below, -1 if not"
        + " available. Present in the 2022 and 2023 editions.",
        json_schema_extra={
            "x-widget_config": _flag_config("Extreme Poverty 2015-19", hide=True)
        },
    )
    extreme_poverty_2017_21: int | None = Field(
        default=None,
        description="Extreme-poverty flag for the 2017-21 ACS period: 1 if the"
        + " poverty rate was 40 percent or higher, 0 if below, -1 if not"
        + " available. Present in the 2023 and 2025 editions.",
        json_schema_extra={
            "x-widget_config": _flag_config("Extreme Poverty 2017-21", hide=True)
        },
    )
    extreme_poverty_2018_22: int | None = Field(
        default=None,
        description="Extreme-poverty flag for the 2018-22 ACS period: 1 if the"
        + " poverty rate was 40 percent or higher, 0 if below, -1 if not"
        + " available. Present in the 2025 edition.",
        json_schema_extra={
            "x-widget_config": _flag_config("Extreme Poverty 2018-22", hide=True)
        },
    )
    extreme_poverty_2019_23: int | None = Field(
        default=None,
        description="Extreme-poverty flag for the 2019-23 ACS period: 1 if the"
        + " poverty rate was 40 percent or higher, 0 if below, -1 if not"
        + " available. Present in the 2025 edition.",
        json_schema_extra={
            "x-widget_config": _flag_config("Extreme Poverty 2019-23", hide=True)
        },
    )
    persistent_poverty_1990: int | None = Field(
        default=None,
        description="Persistent-poverty flag anchored at 1990: 1 if the poverty"
        + " rate was 20 percent or higher across the four consecutive periods"
        + " spanning roughly thirty years, 0 otherwise, -1 if not available.",
        json_schema_extra={
            "x-widget_config": _flag_config("Persistent Poverty 1990", hide=True)
        },
    )
    persistent_poverty_2000: int | None = Field(
        default=None,
        description="Persistent-poverty flag anchored at 2000: 1 if the poverty"
        + " rate was 20 percent or higher across the four consecutive periods"
        + " spanning roughly thirty years, 0 otherwise, -1 if not available.",
        json_schema_extra={"x-widget_config": _flag_config("Persistent Poverty 2000")},
    )
    persistent_poverty_2007_11: int | None = Field(
        default=None,
        description="Persistent-poverty flag anchored at the 2007-11 ACS period:"
        + " 1 if the poverty rate was 20 percent or higher across the four"
        + " consecutive periods spanning roughly thirty years, 0 otherwise, -1"
        + " if not available.",
        json_schema_extra={
            "x-widget_config": _flag_config("Persistent Poverty 2007-11")
        },
    )
    persistent_poverty_2015_19: int | None = Field(
        default=None,
        description="Persistent-poverty flag anchored at the 2015-19 ACS period:"
        + " 1 if the poverty rate was 20 percent or higher across the four"
        + " consecutive periods spanning roughly thirty years, 0 otherwise, -1"
        + " if not available. Present in the 2022 and 2023 editions.",
        json_schema_extra={
            "x-widget_config": _flag_config("Persistent Poverty 2015-19", hide=True)
        },
    )
    persistent_poverty_2017_21: int | None = Field(
        default=None,
        description="Persistent-poverty flag anchored at the 2017-21 ACS period:"
        + " 1 if the poverty rate was 20 percent or higher across the four"
        + " consecutive periods spanning roughly thirty years, 0 otherwise, -1"
        + " if not available. Present in the 2023 and 2025 editions.",
        json_schema_extra={
            "x-widget_config": _flag_config("Persistent Poverty 2017-21", hide=True)
        },
    )
    enduring_poverty_2007_11: int | None = Field(
        default=None,
        description="Enduring-poverty classification anchored at the 2007-11 ACS"
        + " period: 0 not enduring, 1/2/3 enduring by the earliest qualifying"
        + " decade (poverty 20 percent or higher across five or more consecutive"
        + " periods over forty or more years), -1 if not available.",
        json_schema_extra={"x-widget_config": _flag_config("Enduring Poverty 2007-11")},
    )
    enduring_poverty_2015_19: int | None = Field(
        default=None,
        description="Enduring-poverty classification anchored at the 2015-19 ACS"
        + " period: 0 not enduring, 1/2/3 enduring by the earliest qualifying"
        + " decade, -1 if not available. Present in the 2022 and 2023 editions.",
        json_schema_extra={
            "x-widget_config": _flag_config("Enduring Poverty 2015-19", hide=True)
        },
    )
    enduring_poverty_2017_21: int | None = Field(
        default=None,
        description="Enduring-poverty classification anchored at the 2017-21 ACS"
        + " period: 0 not enduring, 1/2/3 enduring by the earliest qualifying"
        + " decade, -1 if not available. Present in the 2023 and 2025 editions.",
        json_schema_extra={
            "x-widget_config": _flag_config("Enduring Poverty 2017-21", hide=True)
        },
    )


class PovertyAreaMeasuresFetcher(
    Fetcher[
        PovertyAreaMeasuresQueryParams,
        list[PovertyAreaMeasuresData],
    ]
):
    """Fetch USDA ERS Poverty Area Measures."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> PovertyAreaMeasuresQueryParams:
        """Transform the query params."""
        return PovertyAreaMeasuresQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: PovertyAreaMeasuresQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected edition's records at the requested level."""
        from openbb_government_us.usda.utils import ers_poverty_area_measures

        return await ers_poverty_area_measures.afetch_edition(
            query.edition, query.level
        )

    @staticmethod
    def transform_data(
        query: PovertyAreaMeasuresQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[PovertyAreaMeasuresData]:
        """Scope the rows to the chosen state and sort by area FIPS."""
        rows = [
            record
            for record in data
            if query.state is None or record["state"] == query.state
        ]
        if not rows:
            raise EmptyDataError("No records match the given filters.")
        rows.sort(key=lambda record: (record["fips"], record.get("tract_fips") or ""))
        if query.level == "tract":
            for record in rows:
                if record.get("tract_fips"):
                    record["fips"] = record["tract_fips"]
        return [PovertyAreaMeasuresData.model_validate(record) for record in rows]
