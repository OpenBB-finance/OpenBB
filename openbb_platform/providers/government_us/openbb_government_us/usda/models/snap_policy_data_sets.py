"""SNAP Policy Data Sets Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_snap_policy_data_sets import (
    POLICY_FIELDS,
    STATE_LABELS,
    state_options,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_STATE = "CA"


def _policy(header: str, hide: bool = False) -> dict:
    """Build a numeric policy field's widget config.

    Parameters
    ----------
    header : str
        Column header shown for the field.
    hide : bool
        Whether to hide the column by default, for sparse fields that apply to
        only a few states.

    Returns
    -------
    dict
        The json_schema_extra carrying the field's x-widget_config.
    """
    config: dict[str, Any] = {"headerName": header, "cellDataType": "number"}
    if hide:
        config["hide"] = True
    return {"x-widget_config": config}


class SnapPolicyDataSetsQueryParams(QueryParams):
    """SNAP Policy Data Sets Query Parameters.

    Source: https://www.ers.usda.gov/data-products/snap-policy-data-sets
    """

    __json_schema_extra__ = {
        "state": {
            "x-widget_config": {
                "label": "State",
                "value": DEFAULT_STATE,
                "multiSelect": False,
                "multiple": False,
                "options": state_options(),
                "style": {"popupWidth": 280},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    state: str = Field(
        default=DEFAULT_STATE,
        description="State to retrieve, as a two-letter postal code. The SNAP"
        + " Policy Database is published for the fifty states and the District"
        + " of Columbia; each state is one monthly time series of its forty-five"
        + " policy variables.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from January 1996.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns through December 2020.",
    )

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate state."""
        if not v:
            return DEFAULT_STATE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().upper()
        if value not in STATE_LABELS:
            raise OpenBBError(
                f"Invalid state: {value}. Valid states are: " + ", ".join(STATE_LABELS)
            )
        return value


class SnapPolicyDataSetsData(NullTokenMixin, Data):
    """SNAP Policy Data Sets Data.

    One selected state's monthly SNAP policy record: each row is a month, with
    the forty-five policy variables as columns. The not-applicable ``-9``
    sentinel on the BBCE sub-fields (meaning the state does not use broad-based
    categorical eligibility, which the ``bbce`` flag already records) and blank
    missing cells are coerced to null; the ``-8`` and ``-7`` policy codes on the
    elderly/disabled income-limit field are meaningful and kept.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS SNAP Policy Data Sets",
                "$.description": "State-level monthly SNAP policy options -"
                " broad-based categorical eligibility, recertification periods,"
                " EBT issuance, interview waivers, fingerprinting, noncitizen"
                " eligibility, online application, outreach spending, and"
                " vehicle-asset rules - from January 1996 to December 2020,"
                " published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    date: dateType = Field(
        description="First day of the observation month.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Date",
                "cellDataType": "date",
                "pinned": "left",
                "maxWidth": 120,
            }
        },
    )
    state: str = Field(
        description="Name of the state of the observation.",
        json_schema_extra={"x-widget_config": {"headerName": "State", "hide": True}},
    )
    bbce: float | None = Field(
        default=None,
        description="Whether the state uses broad-based categorical eligibility"
        + " (BBCE): 0 = no, 1 = yes.",
        json_schema_extra=_policy("Uses BBCE"),
    )
    bbce_asset: float | None = Field(
        default=None,
        description="BBCE asset test: 0 = asset limit raised but not eliminated,"
        + " 1 = asset limit eliminated. Blank when the state does not use BBCE.",
        json_schema_extra=_policy("BBCE asset test (0=raised, 1=eliminated)"),
    )
    bbce_a_amt: float | None = Field(
        default=None,
        description="BBCE asset limit in thousands of dollars. Blank when the"
        + " state does not use BBCE or BBCE eliminates the asset test; applies"
        + " to only the few states that keep an asset limit, so hidden by"
        + " default.",
        json_schema_extra=_policy("BBCE asset limit ($000)", hide=True),
    )
    bbce_a_veh: float | None = Field(
        default=None,
        description="BBCE vehicle rule: 1 = exempt an amount, 2 = exclude at"
        + " least one, 3 = exclude all. Blank when the state does not use BBCE"
        + " or the asset test is eliminated; applies to only the few states that"
        + " keep an asset limit, so hidden by default.",
        json_schema_extra=_policy(
            "BBCE vehicle rule (1=amount, 2=one, 3=all)", hide=True
        ),
    )
    bbce_inclmt: float | None = Field(
        default=None,
        description="BBCE gross income limit as a percentage of the Federal"
        + " poverty level. Blank when the state does not use BBCE.",
        json_schema_extra=_policy("BBCE gross income limit (% FPL)"),
    )
    bbce_child: float | None = Field(
        default=None,
        description="Whether BBCE is limited to households with dependent"
        + " children: 0 = no, 1 = yes. Blank when the state does not use BBCE.",
        json_schema_extra=_policy("BBCE limited to households with children"),
    )
    bbce_elddisinclmt: float | None = Field(
        default=None,
        description="BBCE gross income limit (% FPL) for households with a"
        + " senior or disabled member; -8 = gross income test eliminated,"
        + " -7 = 200% FPL only for all-senior/disabled households. Blank when"
        + " the state does not use BBCE.",
        json_schema_extra=_policy("BBCE elderly/disabled income limit (% FPL)"),
    )
    bbce_multiple: float | None = Field(
        default=None,
        description="Whether multiple BBCE guidelines apply to different"
        + " household types: 0 = no, 1 = yes. Blank when the state does not use"
        + " BBCE.",
        json_schema_extra=_policy("Multiple BBCE guidelines"),
    )
    call_any: float | None = Field(
        default=None,
        description="Whether the state operates call centers in any part of the"
        + " state: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Call centers"),
    )
    cap: float | None = Field(
        default=None,
        description="Whether the state operates a Combined Application Project"
        + " for SSI recipients: 0 = no, 1 = yes.",
        json_schema_extra=_policy("SSI Combined Application Project"),
    )
    certearn_0103: float | None = Field(
        default=None,
        description="Proportion of SNAP units with earnings with 1-3 month"
        + " recertification periods.",
        json_schema_extra=_policy("Recert share, earners 1-3 mo"),
    )
    certearn_0406: float | None = Field(
        default=None,
        description="Proportion of SNAP units with earnings with 4-6 month"
        + " recertification periods.",
        json_schema_extra=_policy("Recert share, earners 4-6 mo"),
    )
    certearn_0712: float | None = Field(
        default=None,
        description="Proportion of SNAP units with earnings with 7-12 month"
        + " recertification periods.",
        json_schema_extra=_policy("Recert share, earners 7-12 mo"),
    )
    certearn_1399: float | None = Field(
        default=None,
        description="Proportion of SNAP units with earnings with 13+ month"
        + " recertification periods.",
        json_schema_extra=_policy("Recert share, earners 13+ mo"),
    )
    certearnavg: float | None = Field(
        default=None,
        description="Average recertification period in months for SNAP units"
        + " with earnings.",
        json_schema_extra=_policy("Avg recert months, earners"),
    )
    certearnmed: float | None = Field(
        default=None,
        description="Median recertification period in months for SNAP units"
        + " with earnings.",
        json_schema_extra=_policy("Median recert months, earners"),
    )
    certeld_0103: float | None = Field(
        default=None,
        description="Proportion of SNAP units with no earnings and a senior"
        + " member with 1-3 month recertification periods.",
        json_schema_extra=_policy("Recert share, no earnings w/ senior 1-3 mo"),
    )
    certeld_0406: float | None = Field(
        default=None,
        description="Proportion of SNAP units with no earnings and a senior"
        + " member with 4-6 month recertification periods.",
        json_schema_extra=_policy("Recert share, no earnings w/ senior 4-6 mo"),
    )
    certeld_0712: float | None = Field(
        default=None,
        description="Proportion of SNAP units with no earnings and a senior"
        + " member with 7-12 month recertification periods.",
        json_schema_extra=_policy("Recert share, no earnings w/ senior 7-12 mo"),
    )
    certeld_1399: float | None = Field(
        default=None,
        description="Proportion of SNAP units with no earnings and a senior"
        + " member with 13+ month recertification periods.",
        json_schema_extra=_policy("Recert share, no earnings w/ senior 13+ mo"),
    )
    certeldavg: float | None = Field(
        default=None,
        description="Average recertification period in months for SNAP units"
        + " with no earnings and a senior member.",
        json_schema_extra=_policy("Avg recert months, no earnings w/ senior"),
    )
    certeldmed: float | None = Field(
        default=None,
        description="Median recertification period in months for SNAP units"
        + " with no earnings and a senior member.",
        json_schema_extra=_policy("Median recert months, no earnings w/ senior"),
    )
    certnonearn_0103: float | None = Field(
        default=None,
        description="Proportion of SNAP units with no earnings and no senior"
        + " member with 1-3 month recertification periods.",
        json_schema_extra=_policy("Recert share, no earnings no senior 1-3 mo"),
    )
    certnonearn_0406: float | None = Field(
        default=None,
        description="Proportion of SNAP units with no earnings and no senior"
        + " member with 4-6 month recertification periods.",
        json_schema_extra=_policy("Recert share, no earnings no senior 4-6 mo"),
    )
    certnonearn_0712: float | None = Field(
        default=None,
        description="Proportion of SNAP units with no earnings and no senior"
        + " member with 7-12 month recertification periods.",
        json_schema_extra=_policy("Recert share, no earnings no senior 7-12 mo"),
    )
    certnonearn_1399: float | None = Field(
        default=None,
        description="Proportion of SNAP units with no earnings and no senior"
        + " member with 13+ month recertification periods.",
        json_schema_extra=_policy("Recert share, no earnings no senior 13+ mo"),
    )
    certnonearnavg: float | None = Field(
        default=None,
        description="Average recertification period in months for SNAP units"
        + " with no earnings and no senior member.",
        json_schema_extra=_policy("Avg recert months, no earnings no senior"),
    )
    certnonearnmed: float | None = Field(
        default=None,
        description="Median recertification period in months for SNAP units"
        + " with no earnings and no senior member.",
        json_schema_extra=_policy("Median recert months, no earnings no senior"),
    )
    ebtissuance: float | None = Field(
        default=None,
        description="Proportion of the dollar value of all SNAP benefits issued"
        + " via electronic benefit transfer (EBT).",
        json_schema_extra=_policy("Share of benefits via EBT"),
    )
    faceini: float | None = Field(
        default=None,
        description="Whether the state has a waiver to use a telephone"
        + " interview at initial certification: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Telephone-interview waiver at initial cert"),
    )
    facerec: float | None = Field(
        default=None,
        description="Whether the state has a waiver to use a telephone"
        + " interview at recertification: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Telephone-interview waiver at recert"),
    )
    fingerprint: float | None = Field(
        default=None,
        description="Whether the state requires fingerprinting of applicants:"
        + " 0 = no, 1 = statewide, 2 = select parts of the state.",
        json_schema_extra=_policy("Fingerprinting (0=no, 1=statewide, 2=partial)"),
    )
    noncitadultfull: float | None = Field(
        default=None,
        description="Whether all legal noncitizen adults meeting other"
        + " requirements are eligible: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Noncitizen adults eligible (full)"),
    )
    noncitadultpart: float | None = Field(
        default=None,
        description="Whether some, but not all, legal noncitizen adults meeting"
        + " other requirements are eligible: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Noncitizen adults eligible (partial)"),
    )
    noncitchildfull: float | None = Field(
        default=None,
        description="Whether all legal noncitizen children meeting other"
        + " requirements are eligible: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Noncitizen children eligible (full)"),
    )
    noncitchildpart: float | None = Field(
        default=None,
        description="Whether some, but not all, legal noncitizen children"
        + " meeting other requirements are eligible: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Noncitizen children eligible (partial)"),
    )
    nonciteldfull: float | None = Field(
        default=None,
        description="Whether all legal noncitizen seniors meeting other"
        + " requirements are eligible: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Noncitizen seniors eligible (full)"),
    )
    nonciteldpart: float | None = Field(
        default=None,
        description="Whether some, but not all, legal noncitizen seniors"
        + " meeting other requirements are eligible: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Noncitizen seniors eligible (partial)"),
    )
    oapp: float | None = Field(
        default=None,
        description="Whether the state allows online SNAP applications: 0 = no,"
        + " 1 = statewide, 2 = select parts of the state.",
        json_schema_extra=_policy("Online application (0=no, 1=statewide, 2=partial)"),
    )
    outreach: float | None = Field(
        default=None,
        description="Sum of Federal, State, and grant outreach spending in"
        + " nominal thousands of dollars, spread across the fiscal year.",
        json_schema_extra=_policy("Outreach spending ($000, nominal)"),
    )
    reportsimple: float | None = Field(
        default=None,
        description="Whether the state uses simplified reporting for households"
        + " with earnings: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Simplified reporting"),
    )
    transben: float | None = Field(
        default=None,
        description="Whether the state offers transitional SNAP benefits to"
        + " families leaving cash assistance: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Transitional benefits"),
    )
    vehexclall: float | None = Field(
        default=None,
        description="Whether the state excludes all vehicles from the asset"
        + " test: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Vehicle: exclude all"),
    )
    vehexclamt: float | None = Field(
        default=None,
        description="Whether the state exempts an amount above the standard"
        + " auto exemption from a vehicle's value: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Vehicle: exempt amount"),
    )
    vehexclone: float | None = Field(
        default=None,
        description="Whether the state excludes at least one, but not all,"
        + " vehicles from the asset test: 0 = no, 1 = yes.",
        json_schema_extra=_policy("Vehicle: exclude one"),
    )


class SnapPolicyDataSetsFetcher(
    Fetcher[
        SnapPolicyDataSetsQueryParams,
        list[SnapPolicyDataSetsData],
    ]
):
    """Fetch USDA ERS SNAP Policy Data Sets."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> SnapPolicyDataSetsQueryParams:
        """Transform the query params."""
        return SnapPolicyDataSetsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SnapPolicyDataSetsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected state's monthly policy records."""
        from openbb_government_us.usda.utils import ers_snap_policy_data_sets

        return await ers_snap_policy_data_sets.afetch_state(query.state)

    @staticmethod
    def transform_data(
        query: SnapPolicyDataSetsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SnapPolicyDataSetsData]:
        """Filter to the year range and emit one row per month, newest first."""
        rows = []
        for record in data:
            yearmonth = record["yearmonth"]
            year = yearmonth // 100
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            rows.append(record)
        if not rows:
            raise EmptyDataError("No records match the given filters.")
        rows.sort(key=lambda record: record["yearmonth"], reverse=True)
        validated: list[SnapPolicyDataSetsData] = []
        for record in rows:
            yearmonth = record["yearmonth"]
            values = {
                "date": dateType(yearmonth // 100, yearmonth % 100, 1),
                "state": record["state"],
            }
            for field in POLICY_FIELDS:
                values[field] = record[field]
            validated.append(SnapPolicyDataSetsData.model_validate(values))
        return validated
