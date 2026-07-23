"""USAspending Recipient Awards Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import ConfigDict, Field

from openbb_government_us.treasury.models.usaspending_award_search import (
    AWARD_TYPE_CODES,
    AwardGroup,
)

CONTRACT_GROUPS = {"contracts", "idvs"}

BASE_FIELDS = [
    "Award ID",
    "Recipient Name",
    "Recipient UEI",
    "Award Amount",
    "Total Outlays",
    "Description",
    "Awarding Agency",
    "Awarding Sub Agency",
    "Start Date",
    "End Date",
]


class UsSpendingRecipientAwardsQueryParams(QueryParams):
    """USAspending Recipient Awards Query Parameters.

    Source: https://api.usaspending.gov/api/v2/search/spending_by_award/
    """

    __json_schema_extra__ = {
        "award_group": {
            "x-widget_config": {
                "label": "Award Group",
                "multiSelect": False,
                "multiple": False,
                "style": {"popupWidth": 300},
            },
        },
        "recipient_id": {"x-widget_config": {"label": "Recipient ID"}},
    }

    recipient_id: str = Field(
        description="Identifier of the recipient, as returned by the recipient"
        + " search, e.g. 'ab4b0d9e-2a56-a67b-1fb7-b54a68b680ed-P'. A parent"
        + " level identifier rolls up the awards of every subsidiary.",
    )
    award_group: AwardGroup = Field(
        default="contracts",
        description="Award category to list.",
    )
    limit: int = Field(
        default=100,
        description=QUERY_DESCRIPTIONS.get("limit", "The number of results.")
        + " Capped by the source at 100.",
        ge=1,
        le=100,
    )
    page: int = Field(
        default=1,
        description=QUERY_DESCRIPTIONS.get("page", "The page of results."),
        ge=1,
    )


class UsSpendingRecipientAwardsData(Data):
    """USAspending Recipient Awards Data.

    The prime awards belonging to one recipient. Amounts are raw USD, as
    reported by the source.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Recipient Awards",
                "$.description": "Federal contract and assistance awards belonging"
                " to a single recipient, from USAspending.gov.",
                "$.category": "Government",
                "$.subCategory": "Federal Awards",
                "$.source": ["US Treasury", "USAspending"],
                "$.refetchInterval": False,
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
        description="Identifier of the award, used to look up the award detail.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "▸ Group: Award ID",
                "headerTooltip": "Click a cell here to group by this award and drive"
                + " the 'Federal Award Info' widget.",
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
        description="The award's public identifier, its PIID, FAIN, or URI.",
    )
    recipient_name: str | None = Field(
        default=None,
        description="Name of the recipient on the award.",
    )
    recipient_uei: str | None = Field(
        default=None,
        description="Unique Entity Identifier of the recipient on the award.",
    )
    award_type: str | None = Field(
        default=None,
        description="Human readable award type.",
    )
    award_amount: float | None = Field(
        default=None,
        description="Current total value of the award, in dollars.",
    )
    total_outlays: float | None = Field(
        default=None,
        description="Total outlayed against the award, in dollars.",
    )
    awarding_agency: str | None = Field(
        default=None,
        description="Name of the awarding top-tier agency.",
    )
    awarding_subagency: str | None = Field(
        default=None,
        description="Name of the awarding sub-tier agency.",
    )
    start_date: dateType | None = Field(
        default=None,
        description="Start date of the period of performance.",
    )
    end_date: dateType | None = Field(
        default=None,
        description="End date of the period of performance.",
    )
    description: str | None = Field(
        default=None,
        description="Description of the award.",
    )


class UsSpendingRecipientAwardsFetcher(
    Fetcher[
        UsSpendingRecipientAwardsQueryParams,
        list[UsSpendingRecipientAwardsData],
    ]
):
    """List one recipient's awards from USAspending."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> UsSpendingRecipientAwardsQueryParams:
        """Transform the query params."""
        return UsSpendingRecipientAwardsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UsSpendingRecipientAwardsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the recipient's awards.

        The award search discards a recipient_id filter, so the recipient's UEI
        is resolved from its profile and matched as search text instead.

        Raises
        ------
        OpenBBError
            If the recipient has no UEI to search on.
        EmptyDataError
            If the recipient has no awards in the requested group.
        """
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_government_us.treasury.utils.recipient import (
            REQUEST_TIMEOUT,
            get_profile,
        )
        from openbb_government_us.treasury.utils.usaspending import post_usaspending

        profile = await get_profile(query.recipient_id)
        uei = profile.get("uei")

        if not uei:
            raise OpenBBError(
                f"Recipient '{query.recipient_id}'"
                f" ({profile.get('name') or 'unnamed'}) has no UEI registered,"
                " so its awards cannot be looked up."
            )

        fields = [
            *BASE_FIELDS,
            (
                "Contract Award Type"
                if query.award_group in CONTRACT_GROUPS
                else "Award Type"
            ),
        ]
        response = await post_usaspending(
            "search/spending_by_award/",
            {
                "filters": {
                    "award_type_codes": AWARD_TYPE_CODES[query.award_group],
                    "recipient_search_text": [uei],
                },
                "fields": fields,
                "sort": "Award Amount",
                "order": "desc",
                "limit": query.limit,
                "page": query.page,
            },
            timeout=REQUEST_TIMEOUT,
        )
        results = response.get("results") or []

        if not results:
            raise EmptyDataError(
                f"No '{query.award_group}' awards were found for"
                f" {profile.get('name') or query.recipient_id}."
            )

        return results

    @staticmethod
    def transform_data(
        query: UsSpendingRecipientAwardsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[UsSpendingRecipientAwardsData]:
        """Transform the data."""
        results: list[UsSpendingRecipientAwardsData] = []

        for row in data:
            award_id = row.get("generated_internal_id")

            if not award_id:
                continue

            results.append(
                UsSpendingRecipientAwardsData.model_validate(
                    {
                        "award_id": award_id,
                        "award_number": row.get("Award ID"),
                        "recipient_name": row.get("Recipient Name"),
                        "recipient_uei": row.get("Recipient UEI"),
                        "award_type": row.get("Contract Award Type")
                        or row.get("Award Type"),
                        "award_amount": row.get("Award Amount"),
                        "total_outlays": row.get("Total Outlays"),
                        "description": row.get("Description"),
                        "awarding_agency": row.get("Awarding Agency"),
                        "awarding_subagency": row.get("Awarding Sub Agency"),
                        "start_date": row.get("Start Date"),
                        "end_date": row.get("End Date"),
                    }
                )
            )

        return results
