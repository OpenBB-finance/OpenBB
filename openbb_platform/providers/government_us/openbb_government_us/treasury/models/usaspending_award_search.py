"""USAspending Award Search Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import ConfigDict, Field, field_validator

AwardGroup = Literal[
    "contracts",
    "idvs",
    "grants",
    "direct_payments",
    "loans",
    "other_assistance",
]

SortField = Literal[
    "Award Amount",
    "Total Outlays",
    "Start Date",
    "End Date",
    "Recipient Name",
    "Award ID",
]

AWARD_TYPE_CODES: dict[str, list[str]] = {
    "contracts": ["A", "B", "C", "D"],
    "idvs": [
        "IDV_A",
        "IDV_B",
        "IDV_B_A",
        "IDV_B_B",
        "IDV_B_C",
        "IDV_C",
        "IDV_D",
        "IDV_E",
    ],
    "grants": ["02", "03", "04", "05"],
    "direct_payments": ["06", "10"],
    "loans": ["07", "08"],
    "other_assistance": ["09", "11"],
}

CONTRACT_GROUPS = frozenset({"contracts", "idvs"})

BASE_FIELDS = [
    "Award ID",
    "Recipient Name",
    "Recipient UEI",
    "Award Amount",
    "Total Outlays",
    "Awarding Agency",
    "Awarding Sub Agency",
    "Start Date",
    "End Date",
    "Description",
    "generated_internal_id",
    "recipient_id",
]

FIELD_MAP = {
    "generated_internal_id": "award_id",
    "Award ID": "award_number",
    "Recipient Name": "recipient_name",
    "Recipient UEI": "recipient_uei",
    "Award Amount": "award_amount",
    "Total Outlays": "total_outlays",
    "Awarding Agency": "awarding_agency",
    "Awarding Sub Agency": "awarding_sub_agency",
    "Start Date": "start_date",
    "End Date": "end_date",
    "Description": "description",
    "recipient_id": "recipient_id",
    "internal_id": "internal_id",
    "Contract Award Type": "award_type",
    "Award Type": "award_type",
}

DATE_FIELDS = frozenset({"start_date", "end_date"})

api_prefix = SystemService().system_settings.api_settings.prefix


def _code_param(field: str, label: str) -> dict:
    """Build the widget config for a fixed code-list filter."""
    from openbb_government_us.treasury.utils.award_filters import code_options

    return {
        "x-widget_config": {
            "label": label,
            "multiSelect": True,
            "options": [{"label": label, "value": "none"}, *code_options(field)],
            "style": {"popupWidth": 460},
        },
    }


class UsSpendingAwardSearchQueryParams(QueryParams):
    """USAspending Award Search Query Parameters.

    Source: https://api.usaspending.gov/docs/endpoints
    """

    __json_schema_extra__ = {
        "contract_pricing": _code_param("contract_pricing", "Contract Pricing"),
        "set_aside": _code_param("set_aside", "Set Aside"),
        "extent_competed": _code_param("extent_competed", "Extent Competed"),
        "defc": {
            "x-widget_config": {
                "label": "DEFC",
                "multiSelect": True,
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/ustreasury/def_codes",
                "options": [{"label": "DEFC", "value": "none"}],
                "style": {"popupWidth": 520},
            },
        },
        "agency": {
            "x-widget_config": {
                "label": "Awarding Agency",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/ustreasury/awarding_agencies",
                "options": [{"label": "Awarding Agency", "value": "none"}],
                "style": {"popupWidth": 520},
            },
        },
        "award_group": {
            "x-widget_config": {
                "label": "Award Group",
                "multiSelect": False,
                "multiple": False,
            },
        },
        "award_number": {"x-widget_config": {"label": "Award Number (PIID/FAIN)"}},
        "description": {"x-widget_config": {"label": "Award Description"}},
        "naics": {"x-widget_config": {"label": "NAICS"}},
        "psc": {"x-widget_config": {"label": "PSC"}},
        "assistance_listing": {"x-widget_config": {"label": "Assistance Listing"}},
    }

    award_group: AwardGroup = Field(
        default="contracts",
        description="Award family to search: 'contracts', 'idvs' (indefinite"
        + " delivery vehicles), 'grants', 'direct_payments', 'loans', or"
        + " 'other_assistance'. Sets the underlying award-type codes.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Filters on the award action period. When None, defaults to the"
        + " trailing 365 days rather than all of history.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " Filters on the award action period.",
    )
    keywords: str | None = Field(
        default=None,
        description="Free-text search over award descriptions and identifiers."
        + " Accepts a comma-separated list; awards matching any term are kept.",
    )
    recipient: str | None = Field(
        default=None,
        description="Recipient name search text, e.g. 'Boeing'.",
    )
    agency: str | None = Field(
        default=None,
        description="Awarding top-tier agency name, exactly as published, e.g."
        + " 'Department of Defense'.",
    )
    min_amount: float | None = Field(
        default=None,
        description="Minimum award amount, in dollars.",
    )
    max_amount: float | None = Field(
        default=None,
        description="Maximum award amount, in dollars.",
    )
    award_number: str | None = Field(
        default=None,
        description="Award number, its PIID, FAIN, or URI, e.g."
        + " 'SPE30018FLGFZ'. Accepts a comma-separated list. Matching is fuzzy;"
        + " wrap a value in double quotes for an exact match, which is needed"
        + " for identifiers containing spaces.",
    )
    description: str | None = Field(
        default=None,
        description="Search text matched against the award description only,"
        + " unlike 'keywords', which also searches identifiers.",
    )
    naics: str | None = Field(
        default=None,
        description="North American Industry Classification System code, e.g."
        + " '541519'. Accepts a comma-separated list. Validated against the"
        + " source's reference list.",
    )
    psc: str | None = Field(
        default=None,
        description="Product or Service Code, e.g. 'R425'. Accepts a"
        + " comma-separated list. Validated against the source's reference list.",
    )
    assistance_listing: str | None = Field(
        default=None,
        description="Assistance Listing (CFDA) program number, e.g. '10.331'."
        + " Accepts a comma-separated list. Validated against the source's"
        + " reference list. Assistance awards only.",
    )
    defc: str | None = Field(
        default=None,
        description="Disaster Emergency Fund Code, e.g. 'L' for COVID-19 or 'Z'"
        + " for infrastructure. Accepts a comma-separated list.",
    )
    contract_pricing: str | None = Field(
        default=None,
        description="Type of contract pricing, by code, e.g. 'J' for Firm Fixed"
        + " Price. Accepts a comma-separated list. Contracts and IDVs only.",
    )
    set_aside: str | None = Field(
        default=None,
        description="Type of set aside, by code, e.g. 'SBA' for Small Business"
        + " Set Aside - Total. Accepts a comma-separated list. Contracts and"
        + " IDVs only.",
    )
    extent_competed: str | None = Field(
        default=None,
        description="Extent competed, by code, e.g. 'A' for Full and Open"
        + " Competition. Accepts a comma-separated list. Contracts and IDVs only.",
    )
    sort: SortField = Field(
        default="Award Amount",
        description="Field to sort by.",
    )
    order: Literal["desc", "asc"] = Field(
        default="desc",
        description="Sort order.",
    )
    page: int = Field(
        default=1,
        description=QUERY_DESCRIPTIONS.get("page", "The page of results to return."),
        ge=1,
    )
    limit: int = Field(
        default=100,
        description=QUERY_DESCRIPTIONS.get("limit", "The number of results to return.")
        + " Capped by the source at 100.",
        ge=1,
        le=100,
    )

    @field_validator(
        "keywords",
        "recipient",
        "agency",
        "award_number",
        "description",
        "naics",
        "psc",
        "assistance_listing",
        "defc",
        "contract_pricing",
        "set_aside",
        "extent_competed",
        mode="before",
    )
    @classmethod
    def _strip_optional(cls, v):
        """Strip an optional text filter to None when empty."""
        if not isinstance(v, str):
            return v
        value = v.strip()
        if not value or value.lower() in {"none", "null"}:
            return None
        return value


class UsSpendingAwardSearchData(Data):
    """USAspending Award Search Data.

    One row per prime award matching the search, newest or largest first.
    The award_id is the usaspending.gov identifier that the award drill-down
    widget accepts, so a row selects directly into the award detail.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.params": [
                    {
                        "paramName": "award_id",
                        "label": "Award ID",
                        "description": "Ghost parameter carrying the award id"
                        " clicked in this table, so the award widgets follow it.",
                        "type": "text",
                        "value": "none",
                        "show": False,
                    },
                ],
            },
        }
    )

    award_id: str = Field(
        description="USAspending award identifier, as used by the award"
        + " drill-down, e.g. 'CONT_AWD_HT940216C0001_9700_-NONE-_-NONE-'."
        + " Click it to open the award in the drill-down widgets.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Award ID",
                "pinned": "left",
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "award_id",
                },
            },
        },
    )
    award_number: str | None = Field(
        default=None,
        description="Published award number: the contract PIID, or the"
        + " assistance FAIN or URI.",
    )
    recipient_name: str | None = Field(
        default=None,
        description="Name of the award recipient.",
    )
    recipient_uei: str | None = Field(
        default=None,
        description="Unique Entity Identifier of the recipient.",
    )
    award_type: str | None = Field(
        default=None,
        description="Award type, e.g. 'DEFINITIVE CONTRACT' or 'BLOCK GRANT (A)'.",
    )
    award_amount: float | None = Field(
        default=None,
        description="Current total award amount, in dollars.",
    )
    total_outlays: float | None = Field(
        default=None,
        description="Total outlays paid against the award, in dollars.",
    )
    awarding_agency: str | None = Field(
        default=None,
        description="Awarding top-tier agency.",
    )
    awarding_sub_agency: str | None = Field(
        default=None,
        description="Awarding sub-agency.",
    )
    start_date: dateType | None = Field(
        default=None,
        description="Period-of-performance start date.",
    )
    end_date: dateType | None = Field(
        default=None,
        description="Period-of-performance current end date.",
    )
    description: str | None = Field(
        default=None,
        description="Award description.",
    )
    recipient_id: str | None = Field(
        default=None,
        description="Internal recipient identifier.",
    )
    internal_id: int | None = Field(
        default=None,
        description="Internal award identifier.",
    )


class UsSpendingAwardSearchFetcher(
    Fetcher[
        UsSpendingAwardSearchQueryParams,
        list[UsSpendingAwardSearchData],
    ]
):
    """Search prime awards from the USAspending API."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> UsSpendingAwardSearchQueryParams:
        """Transform the query params."""
        return UsSpendingAwardSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UsSpendingAwardSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the USAspending spending-by-award endpoint.

        Raises
        ------
        EmptyDataError
            If the search returns no rows.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_government_us.treasury.utils.award_filters import (
            apply_filters,
            split_codes,
            validate_reference_codes,
        )
        from openbb_government_us.treasury.utils.fiscal_data import default_start_date
        from openbb_government_us.treasury.utils.recipient import REQUEST_TIMEOUT
        from openbb_government_us.treasury.utils.usaspending import post_usaspending

        start = default_start_date(query.start_date, query.end_date, 365)
        end = query.end_date or dateType.today()
        type_field = (
            "Contract Award Type"
            if query.award_group in CONTRACT_GROUPS
            else "Award Type"
        )

        filters: dict[str, Any] = {
            "award_type_codes": AWARD_TYPE_CODES[query.award_group],
            "time_period": [{"start_date": str(start), "end_date": str(end)}],
        }
        if query.keywords:
            filters["keywords"] = [
                term.strip() for term in query.keywords.split(",") if term.strip()
            ]
        if query.recipient:
            filters["recipient_search_text"] = [query.recipient]
        if query.agency:
            filters["agencies"] = [
                {"type": "awarding", "tier": "toptier", "name": query.agency}
            ]
        amount: dict[str, float] = {}
        if query.min_amount is not None:
            amount["lower_bound"] = query.min_amount
        if query.max_amount is not None:
            amount["upper_bound"] = query.max_amount
        if amount:
            filters["award_amounts"] = [amount]
        if query.award_number:
            filters["award_ids"] = split_codes(query.award_number)
        if query.description:
            filters["description"] = query.description
        if query.defc:
            filters["def_codes"] = split_codes(query.defc)
        for field, target in (
            ("naics", "naics_codes"),
            ("psc", "psc_codes"),
            ("assistance_listing", "program_numbers"),
        ):
            codes = await validate_reference_codes(field, getattr(query, field))
            if codes:
                filters[target] = codes
        apply_filters(query, filters)

        payload = {
            "filters": filters,
            "fields": [*BASE_FIELDS, type_field],
            "page": query.page,
            "limit": query.limit,
            "sort": query.sort,
            "order": query.order,
            "subawards": False,
        }

        response = await post_usaspending(
            "search/spending_by_award/", payload, timeout=REQUEST_TIMEOUT
        )
        results = response.get("results") or []
        if not results:
            raise EmptyDataError(
                "The request was returned empty. No awards matched the search"
                f" at page {query.page}."
            )
        return results

    @staticmethod
    def transform_data(
        query: UsSpendingAwardSearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[UsSpendingAwardSearchData]:
        """Transform the data."""
        from datetime import datetime

        results: list[UsSpendingAwardSearchData] = []
        for row in data:
            record: dict[str, Any] = {}
            for source, target in FIELD_MAP.items():
                if source not in row:
                    continue
                value = row[source]
                if target in DATE_FIELDS and value:
                    value = datetime.strptime(value, "%Y-%m-%d").date()
                record[target] = value
            if record.get("award_id"):
                results.append(UsSpendingAwardSearchData.model_validate(record))
        return results
