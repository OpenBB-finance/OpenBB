"""Congress Member Legislation Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field

api_prefix = SystemService().system_settings.api_settings.prefix


class CongressMemberLegislationQueryParams(QueryParams):
    """Congress Member Legislation Query Parameters."""

    __json_schema_extra__ = {
        "bioguide_id": {
            "x-widget_config": {
                "label": "Member",
                "description": "Select a member, or group the 'Congressional Members'"
                + " widget by 'Bioguide ID' and click a cell to view legislation.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/uscongress/member_choices",
                "optionsParams": {"is_workspace": True},
                "value": "A000055",
                "style": {"popupWidth": 400},
            },
        },
        "congress": {"x-widget_config": {"type": "number"}},
    }

    bioguide_id: str = Field(
        description="The member's Biographical Directory (bioguide) identifier."
    )
    congress: int | None = Field(
        default=None,
        description="Restrict to a single Congress (e.g., 119). When None, spans the"
        + " member's full history across every Congress they served (back to the"
        + " 108th, the earliest with bulk data).",
    )


class CongressMemberLegislationData(Data):
    """Congress Member Legislation Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Congressional Member Legislation",
                "$.category": "Government",
                "$.subCategory": "Congress",
                "$.description": "Bills a member sponsored or cosponsored.",
                "$.refetchInterval": False,
            },
        }
    )

    bill_id: str = Field(description="The bill identifier, e.g. '119-hr-29'.")
    congress: int = Field(
        description="The Congress the bill belongs to.",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    role: str = Field(description="Whether the member is the sponsor or a cosponsor.")
    title: str | None = Field(default=None, description="The title of the bill.")
    introduced_date: dateType | None = Field(
        default=None, description="The date the bill was introduced."
    )
    latest_action_date: dateType | None = Field(
        default=None, description="The date of the latest action on the bill."
    )
    latest_action: str | None = Field(
        default=None, description="The latest action on the bill."
    )


class CongressMemberLegislationFetcher(
    Fetcher[
        CongressMemberLegislationQueryParams,
        list[CongressMemberLegislationData],
    ]
):
    """Transform the query, extract and transform data from the BILLSTATUS bulk."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CongressMemberLegislationQueryParams:
        """Transform the query params."""
        return CongressMemberLegislationQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressMemberLegislationQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Extract the bills a member sponsored or cosponsored from the bulk archives."""
        from openbb_congress_gov.utils.bulk import (
            load_member_record,
            member_legislation,
            member_served_congresses,
        )

        if query.congress is not None:
            congresses = [query.congress]
        else:
            record = await load_member_record(query.bioguide_id)
            congresses = member_served_congresses(record)

        return await member_legislation(query.bioguide_id, congresses)

    @staticmethod
    def transform_data(
        query: CongressMemberLegislationQueryParams, data: list, **kwargs: Any
    ) -> list[CongressMemberLegislationData]:
        """Transform raw legislation records into models."""
        return [CongressMemberLegislationData(**record) for record in data]
