"""Congress Member Votes Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field

api_prefix = SystemService().system_settings.api_settings.prefix


class CongressMemberVotesQueryParams(QueryParams):
    """Congress Member Votes Query Parameters."""

    __json_schema_extra__ = {
        "bioguide_id": {
            "x-widget_config": {
                "label": "Member",
                "description": "Select a member, or group the 'Congressional Members'"
                + " widget by 'Bioguide ID' and click a cell to view their votes.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/uscongress/member_choices",
                "optionsParams": {"is_workspace": True},
                "value": "A000055",
                "style": {"popupWidth": 400},
            },
        },
        "congress": {"x-widget_config": {"type": "number"}},
        "limit": {"x-widget_config": {"type": "number"}},
    }

    bioguide_id: str = Field(
        description="The member's Biographical Directory (bioguide) identifier."
    )
    congress: int | None = Field(
        default=None,
        description="Restrict to a single Congress. When None, spans the member's"
        + " full voting history across both chambers (newest first).",
    )
    limit: int = Field(
        default=25,
        description="The number of most recent roll-call votes to return.",
    )


class CongressMemberVotesData(Data):
    """Congress Member Votes Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Congressional Member Votes",
                "$.category": "Government",
                "$.subCategory": "Congress",
                "$.description": "A member's roll-call votes on legislation (House and"
                + " Senate), sourced from Voteview.",
                "$.refetchInterval": False,
            },
        }
    )

    bill_id: str = Field(
        description="The bill or resolution voted on, e.g. '119-hr-2913'.",
        json_schema_extra={"x-widget_config": {"pinned": "left"}},
    )
    congress: int = Field(
        description="The Congress in which the vote was cast.",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    chamber: str = Field(description="The chamber the vote was cast in.")
    title: str | None = Field(
        default=None, description="The title/description of the measure voted on."
    )
    legislation: str | None = Field(
        default=None, description="The measure as identified by Voteview."
    )
    date: dateType | None = Field(default=None, description="The date of the vote.")
    position: str = Field(description="The member's recorded position.")
    rollnumber: int = Field(
        description="The roll-call number within the Congress/chamber.",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    question: str | None = Field(default=None, description="The vote question.")
    result: str | None = Field(default=None, description="The overall vote result.")


class CongressMemberVotesFetcher(
    Fetcher[CongressMemberVotesQueryParams, list[CongressMemberVotesData]]
):
    """Transform the query, extract and transform data from Voteview."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CongressMemberVotesQueryParams:
        """Transform the query params."""
        return CongressMemberVotesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressMemberVotesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Extract a member's roll-call votes on legislation from Voteview."""
        from openbb_congress_gov.utils.bulk import (
            load_member_record,
            member_service,
            member_votes,
        )

        record = await load_member_record(query.bioguide_id)
        service = member_service(record)
        if query.congress is not None:
            service = [(c, ch) for c, ch in service if c == query.congress]
        if not service:
            return []

        return await member_votes(query.bioguide_id, service, limit=query.limit)

    @staticmethod
    def transform_data(
        query: CongressMemberVotesQueryParams, data: list, **kwargs: Any
    ) -> list[CongressMemberVotesData]:
        """Transform raw vote records into CongressMemberVotesData models."""
        transformed: list[CongressMemberVotesData] = []
        for vote in data:
            record = {k: v for k, v in vote.items() if k != "cast_code"}
            record["date"] = record.get("date") or None
            transformed.append(CongressMemberVotesData(**record))
        return transformed
