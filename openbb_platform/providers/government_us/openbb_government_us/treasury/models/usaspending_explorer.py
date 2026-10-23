"""USAspending Spending Explorer Model."""

from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, model_validator

from openbb_government_us.treasury.utils.spending import (
    EARLIEST_FISCAL_YEAR,
    period_options,
)

api_prefix = SystemService().system_settings.api_settings.prefix

ExplorerType = Literal[
    "budget_function",
    "budget_subfunction",
    "agency",
    "federal_account",
    "program_activity",
    "object_class",
    "recipient",
    "award",
    "award_category",
]

ENTRY_TYPES = {
    "budget_function",
    "budget_subfunction",
    "agency",
    "federal_account",
    "object_class",
}

SCOPE_ONLY_TYPES = ("program_activity", "recipient", "award", "award_category")

DRILL_FIELDS = (
    "budget_function",
    "budget_subfunction",
    "agency",
    "federal_account",
    "program_activity",
    "object_class",
    "recipient",
)

TYPE_LABELS: dict[str, str] = {
    "budget_function": "Budget Function",
    "budget_subfunction": "Budget Sub-Function",
    "agency": "Agency",
    "federal_account": "Federal Account",
    "program_activity": "Program Activity",
    "object_class": "Object Class",
    "recipient": "Recipient",
    "award": "Award",
    "award_category": "Award Category",
}


class UsSpendingExplorerQueryParams(QueryParams):
    """USAspending Spending Explorer Query Parameters.

    Source: https://api.usaspending.gov/api/v2/spending/
    """

    __json_schema_extra__ = {
        "explorer_type": {
            "x-widget_config": {
                "label": "Breakdown By",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/ustreasury/explorer_types",
                "optionsParams": {
                    "budget_function": "$budget_function",
                    "budget_subfunction": "$budget_subfunction",
                    "agency": "$agency",
                    "federal_account": "$federal_account",
                    "program_activity": "$program_activity",
                    "object_class": "$object_class",
                    "recipient": "$recipient",
                },
                "style": {"popupWidth": 380},
            },
        },
        "fiscal_year": {
            "x-widget_config": {"label": "Fiscal Year", "type": "number"},
        },
        "period": {
            "x-widget_config": {
                "label": "Reporting Period",
                "multiSelect": False,
                "multiple": False,
                "options": period_options(),
                "style": {"popupWidth": 300},
            },
        },
        **{
            dimension: {
                "x-widget_config": {
                    "label": label,
                    "type": "endpoint",
                    "multiSelect": False,
                    "multiple": False,
                    "optionsEndpoint": f"{api_prefix}/ustreasury/spending_options",
                    "optionsParams": {"dimension": dimension},
                    "style": {"popupWidth": 520},
                },
            }
            for dimension, label in (
                ("object_class", "Object Class"),
                ("budget_function", "Budget Function"),
                ("budget_subfunction", "Budget Subfunction"),
                ("agency", "Agency"),
            )
        },
        "federal_account": {
            "x-widget_config": {
                "label": "Federal Account",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/ustreasury/spending_options",
                "optionsParams": {
                    "dimension": "federal_account",
                    "agency": "$agency",
                },
                "style": {"popupWidth": 560},
            },
        },
    }

    explorer_type: ExplorerType = Field(
        default="object_class",
        description="Dimension to break the spending down by. Every dimension"
        + " works on its own except "
        + ", ".join(f"'{name}'" for name in SCOPE_ONLY_TYPES)
        + ", which are too large to enumerate government-wide and need a"
        + " scoping filter. A scope on the dimension being broken down is"
        + " ignored, since breaking down by a dimension means showing every"
        + " one of its entries.",
    )
    fiscal_year: int | None = Field(
        default=None,
        description="Federal fiscal year. When None, the most recent year the"
        + " source has published is used. Data begins in FY"
        + f"{EARLIEST_FISCAL_YEAR} Q2.",
        ge=EARLIEST_FISCAL_YEAR,
    )
    period: str = Field(
        default="latest",
        description="Federal fiscal period to report through. Amounts are"
        + " cumulative from the start of the fiscal year, so 'Through March'"
        + " covers October through March. 'latest' resolves to the most recent"
        + " period the source has published, because a period that has not"
        + " closed yet is rejected.",
    )
    budget_function: str | None = Field(
        default=None,
        description="Scope the breakdown to one budget function, by its code.",
    )
    budget_subfunction: str | None = Field(
        default=None,
        description="Scope the breakdown to one budget sub-function, by its code.",
    )
    agency: str | None = Field(
        default=None,
        description="Scope the breakdown to one agency, by the id returned for"
        + " an 'agency' breakdown.",
    )
    federal_account: str | None = Field(
        default=None,
        description="Scope the breakdown to one federal account, by the id"
        + " returned for a 'federal_account' breakdown.",
    )
    program_activity: str | None = Field(
        default=None,
        description="Scope the breakdown to one program activity, by its id.",
    )
    object_class: str | None = Field(
        default=None,
        description="Scope the breakdown to one object class, by its code, e.g."
        + " '30' for Acquisition of assets.",
    )
    recipient: str | None = Field(
        default=None,
        description="Scope the breakdown to one recipient, by its id.",
    )

    @model_validator(mode="after")
    def validate_query(self):
        """Validate the breakdown against its scope.

        Raises
        ------
        OpenBBError
            If a non-entry-point breakdown is requested without any scope.
        """
        from openbb_core.app.model.abstract.error import OpenBBError

        scoped = any(
            getattr(self, field)
            for field in DRILL_FIELDS
            if field != self.explorer_type
        )

        if not scoped and self.explorer_type not in ENTRY_TYPES:
            raise OpenBBError(
                f"A '{self.explorer_type}' breakdown is too large to return"
                " government-wide, so it needs a scope. Set one of: "
                + ", ".join(DRILL_FIELDS)
                + "; or choose a dimension that stands alone: "
                + ", ".join(sorted(ENTRY_TYPES))
                + "."
            )

        return self


class UsSpendingExplorerData(Data):
    """USAspending Spending Explorer Data.

    One row per entry of the requested breakdown, descending by obligated
    amount. Amounts are cumulative through the requested period.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Federal Spending Explorer",
                "$.description": "All federal spending for a fiscal year, broken"
                " down by budget function, agency, federal account, program"
                " activity, object class, recipient, or award, and drillable"
                " into any combination of them.",
                "$.category": "Government",
                "$.subCategory": "Federal Spending",
                "$.source": ["US Treasury", "USAspending"],
                "$.refetchInterval": False,
            },
        }
    )

    name: str | None = Field(
        default=None,
        description="Name of the breakdown entry.",
        json_schema_extra={"x-widget_config": {"pinned": "left"}},
    )
    amount: float | None = Field(
        default=None,
        description="Obligated amount, in dollars, cumulative through the"
        + " requested period.",
    )
    percent_of_total: float | None = Field(
        default=None,
        description="The entry's share of the breakdown total, as a percentage.",
        json_schema_extra={"x-widget_config": {"suffix": "%"}},
    )
    code: str | None = Field(
        default=None,
        description="Code of the breakdown entry, where the dimension has one.",
    )
    account_number: str | None = Field(
        default=None,
        description="Federal account symbol, for a 'federal_account' breakdown.",
    )
    explorer_id: str | None = Field(
        default=None,
        description="Identifier of the entry within its dimension, as the"
        + " matching scope filter accepts it.",
        json_schema_extra={"x-widget_config": {"headerName": "ID"}},
    )
    as_of_date: str | None = Field(
        default=None,
        description="Date the reported data is current as of.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )


class UsSpendingExplorerFetcher(
    Fetcher[
        UsSpendingExplorerQueryParams,
        list[UsSpendingExplorerData],
    ]
):
    """Explore federal spending from USAspending."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> UsSpendingExplorerQueryParams:
        """Transform the query params."""
        return UsSpendingExplorerQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UsSpendingExplorerQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the requested spending breakdown.

        Raises
        ------
        EmptyDataError
            If the breakdown returns no rows.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_government_us.treasury.utils.recipient import REQUEST_TIMEOUT
        from openbb_government_us.treasury.utils.spending import latest_submission
        from openbb_government_us.treasury.utils.usaspending import post_usaspending

        fiscal_year = query.fiscal_year
        period = query.period

        if period == "latest" or fiscal_year is None:
            resolved_year, resolved_period = await latest_submission(fiscal_year)
            fiscal_year = fiscal_year or resolved_year
            period = resolved_period if period == "latest" else period

        filters: dict[str, Any] = {"fy": str(fiscal_year), "period": period}

        for field in DRILL_FIELDS:
            value = getattr(query, field)

            if value and field != query.explorer_type:
                filters[field] = value

        response = await post_usaspending(
            "spending/",
            {"type": query.explorer_type, "filters": filters},
            timeout=REQUEST_TIMEOUT,
        )

        if not response.get("results"):
            raise EmptyDataError(
                f"No '{query.explorer_type}' spending was returned for"
                f" FY{fiscal_year} period {period}."
            )

        return response

    @staticmethod
    def transform_data(
        query: UsSpendingExplorerQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[UsSpendingExplorerData]:
        """Transform the data, deriving each entry's share of the total."""
        total = data.get("total")
        as_of = (data.get("end_date") or "").split("T")[0] or None
        results: list[UsSpendingExplorerData] = []

        for row in data.get("results") or []:
            amount = row.get("amount")
            results.append(
                UsSpendingExplorerData.model_validate(
                    {
                        "name": row.get("name"),
                        "amount": amount,
                        "percent_of_total": (
                            amount / total * 100
                            if amount is not None and total
                            else None
                        ),
                        "code": row.get("code"),
                        "account_number": row.get("account_number"),
                        "explorer_id": (
                            str(row["id"])
                            if row.get("id") not in (None, "", "None")
                            else None
                        ),
                        "as_of_date": as_of,
                    }
                )
            )

        return results
