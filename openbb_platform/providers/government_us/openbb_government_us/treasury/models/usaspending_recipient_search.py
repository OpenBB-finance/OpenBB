"""USAspending Recipient Search Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import ConfigDict, Field, field_validator

AwardType = Literal[
    "all",
    "contracts",
    "grants",
    "direct_payments",
    "loans",
    "other_financial_assistance",
]

RecipientSort = Literal["amount", "name", "uei", "duns"]

LEVEL_LABELS: dict[str, str] = {
    "P": "Parent",
    "C": "Child",
    "R": "Recipient",
}


class UsSpendingRecipientSearchQueryParams(QueryParams):
    """USAspending Recipient Search Query Parameters.

    Source: https://api.usaspending.gov/api/v2/recipient/duns/
    """

    __json_schema_extra__ = {
        "award_type": {
            "x-widget_config": {
                "label": "Award Type",
                "multiSelect": False,
                "multiple": False,
                "style": {"popupWidth": 300},
            },
        },
        "sort": {
            "x-widget_config": {
                "label": "Sort By",
                "multiSelect": False,
                "multiple": False,
            },
        },
        "order": {"x-widget_config": {"label": "Order", "multiSelect": False}},
        "keyword": {"x-widget_config": {"label": "Search"}},
    }

    keyword: str | None = Field(
        default=None,
        description="Search text matched against the recipient name, UEI, or"
        + " legacy DUNS. Matching is case-insensitive and by prefix, so a"
        + " partial name or identifier is accepted. When None, the entire"
        + " recipient list is returned, ordered by the sort parameters.",
    )
    award_type: AwardType = Field(
        default="all",
        description="Award category the recipient's amount is measured over."
        + " Changes both the set of recipients returned and the amount"
        + " reported for each.",
    )
    sort: RecipientSort = Field(
        default="amount",
        description="Field to sort the results by.",
    )
    order: Literal["desc", "asc"] = Field(
        default="desc",
        description="Sort order.",
    )
    limit: int = Field(
        default=100,
        description=QUERY_DESCRIPTIONS.get("limit", "The number of results.")
        + " Capped by the source at 1000.",
        ge=1,
        le=1000,
    )
    page: int = Field(
        default=1,
        description=QUERY_DESCRIPTIONS.get("page", "The page of results."),
        ge=1,
    )

    @field_validator("keyword", mode="before", check_fields=False)
    @classmethod
    def _validate_keyword(cls, v):
        """Normalize the keyword to a stripped string or None."""
        if not v:
            return None
        value = str(v).strip()
        if not value or value.lower() in {"none", "null"}:
            return None
        return value


class UsSpendingRecipientSearchData(Data):
    """USAspending Recipient Search Data.

    One row per recipient and recipient level. The same organization appears
    more than once when it is registered at multiple levels, each carrying its
    own amount, because the level is part of the recipient's identity.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Federal Recipient Search",
                "$.description": "Search every entity that has received federal"
                " contract or assistance money, by name, UEI, or legacy DUNS.",
                "$.category": "Government",
                "$.subCategory": "Federal Awards",
                "$.source": ["US Treasury", "USAspending"],
                "$.refetchInterval": False,
                "$.params": [
                    {
                        "paramName": "recipient_id",
                        "label": "Recipient ID",
                        "description": "Ghost parameter carrying the recipient id"
                        " clicked in this table, so the recipient widgets follow it.",
                        "type": "text",
                        "value": "none",
                        "show": False,
                    },
                ],
            },
        }
    )

    recipient_id: str = Field(
        description="Identifier of the recipient at this level, used to look up"
        + " the recipient's profile and awards.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "▸ Group: Recipient",
                "headerTooltip": "Click a cell here to group by this recipient and"
                + " drive the 'Federal Recipient Info' and 'Recipient Awards' widgets.",
                "pinned": "left",
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "recipient_id",
                },
            },
        },
    )
    name: str | None = Field(
        default=None,
        description="Name of the recipient.",
    )
    recipient_level: str | None = Field(
        default=None,
        description="Whether the recipient is a Parent, a Child, or neither.",
    )
    uei: str | None = Field(
        default=None,
        description="Unique Entity Identifier of the recipient.",
    )
    duns: str | None = Field(
        default=None,
        description="Legacy DUNS number of the recipient.",
    )
    amount: float | None = Field(
        default=None,
        description="Aggregate value of the recipient's transactions over the"
        + " trailing 12 months, in dollars. Negative when de-obligations"
        + " exceed obligations.",
    )


class UsSpendingRecipientSearchFetcher(
    Fetcher[
        UsSpendingRecipientSearchQueryParams,
        list[UsSpendingRecipientSearchData],
    ]
):
    """Search federal award recipients from USAspending."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> UsSpendingRecipientSearchQueryParams:
        """Transform the query params."""
        return UsSpendingRecipientSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UsSpendingRecipientSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the matching recipients.

        Raises
        ------
        EmptyDataError
            If no recipient matches the query.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_government_us.treasury.utils.recipient import REQUEST_TIMEOUT
        from openbb_government_us.treasury.utils.usaspending import post_usaspending

        payload: dict[str, Any] = {
            "award_type": query.award_type,
            "sort": query.sort,
            "order": query.order,
            "limit": query.limit,
            "page": query.page,
        }

        if query.keyword:
            payload["keyword"] = query.keyword

        response = await post_usaspending(
            "recipient/duns/", payload, timeout=REQUEST_TIMEOUT
        )
        results = response.get("results") or []

        if not results:
            raise EmptyDataError(
                "No recipients matched the query."
                + (f" Keyword: '{query.keyword}'." if query.keyword else "")
            )

        return results

    @staticmethod
    def transform_data(
        query: UsSpendingRecipientSearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[UsSpendingRecipientSearchData]:
        """Transform the data."""
        results: list[UsSpendingRecipientSearchData] = []

        for row in data:
            recipient_id = row.get("id")

            if not recipient_id:
                continue

            level = row.get("recipient_level")
            results.append(
                UsSpendingRecipientSearchData.model_validate(
                    {
                        "recipient_id": recipient_id,
                        "name": row.get("name"),
                        "recipient_level": LEVEL_LABELS.get(level or "", level),
                        "uei": row.get("uei"),
                        "duns": row.get("duns"),
                        "amount": row.get("amount"),
                    }
                )
            )

        return results
