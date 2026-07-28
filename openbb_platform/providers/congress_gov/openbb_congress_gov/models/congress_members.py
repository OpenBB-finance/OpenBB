"""Congress Members Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field

from openbb_congress_gov.utils.constants import state_options


class CongressMembersQueryParams(QueryParams):
    """Congress Members Query Parameters."""

    __json_schema_extra__ = {
        "chamber": {
            "x-widget_config": {
                "options": [
                    {"label": "House", "value": "house"},
                    {"label": "Senate", "value": "senate"},
                ],
                "paramName": "chamber",
                "label": "Chamber",
            },
        },
        "party": {
            "x-widget_config": {
                "options": [
                    {"label": "Democrat", "value": "Democrat"},
                    {"label": "Republican", "value": "Republican"},
                    {"label": "Independent", "value": "Independent"},
                ],
                "paramName": "party",
                "label": "Party",
            },
        },
        "state": {
            "x-widget_config": {
                "options": state_options,
                "paramName": "state",
                "label": "State",
            },
        },
    }

    chamber: Literal["house", "senate"] | None = Field(
        default=None,
        description="Filter members by chamber. When None, returns both chambers.",
    )
    state: str | None = Field(
        default=None,
        description="Filter members by two-letter state/territory code (e.g., 'OH').",
    )
    party: str | None = Field(
        default=None,
        description="Filter members by party (Democrat, Republican, Independent).",
    )


class CongressMembersData(Data):
    """Congress Members Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Congressional Members",
                "$.category": "Government",
                "$.subCategory": "Congress",
                "$.description": "Current members of the U.S. Congress.",
                "$.params": [
                    {
                        "paramName": "bioguide_id",
                        "label": "Bioguide ID",
                        "description": "Ghost parameter to group by the bioguide id."
                        + " Create a group and use the 'Member Info', 'Member Votes',"
                        + " and 'Member Legislation' widgets to view the member.",
                        "type": "text",
                        "value": None,
                        "show": True,
                    },
                ],
                "$.refetchInterval": False,
            },
        }
    )

    bioguide_id: str = Field(
        description="The member's Biographical Directory (bioguide) identifier.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "▸ Group: Bioguide ID",
                "headerTooltip": "Click a cell here to group by this member and view"
                + " them in the 'Member Info' / 'Member Votes' / 'Member Legislation'"
                + " widgets.",
                "pinned": "left",
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "bioguide_id",
                },
            },
        },
    )
    name: str = Field(description="The member's full name.")
    chamber: str = Field(description="The chamber the member serves in.")
    party: str = Field(description="The member's party.")
    state: str = Field(description="The member's state or territory.")
    district: int | None = Field(
        default=None,
        description="The House district number (None for senators).",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    term_start: dateType | None = Field(
        default=None, description="The start date of the member's current term."
    )
    term_end: dateType | None = Field(
        default=None, description="The end date of the member's current term."
    )
    website: str | None = Field(
        default=None, description="The member's official website."
    )


class CongressMembersFetcher(
    Fetcher[CongressMembersQueryParams, list[CongressMembersData]]
):
    """Transform the query, extract and transform data from the unitedstates dataset."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CongressMembersQueryParams:
        """Transform the query params."""
        return CongressMembersQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressMembersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Extract the current members from the unitedstates legislators dataset."""
        from openbb_congress_gov.utils.bulk import (
            filter_members,
            load_members,
            to_member_list_item,
        )

        members = await load_members()
        items = [to_member_list_item(m) for m in members]

        return filter_members(
            items,
            chamber=query.chamber,
            state=query.state,
            party=query.party,
        )

    @staticmethod
    def transform_data(
        query: CongressMembersQueryParams, data: list, **kwargs: Any
    ) -> list[CongressMembersData]:
        """Transform raw member records into CongressMembersData models."""
        return [CongressMembersData(**record) for record in data]
