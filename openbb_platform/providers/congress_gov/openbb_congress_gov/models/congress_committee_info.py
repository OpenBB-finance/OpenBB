"""Congress Committee Info Model - Widget 2: Metadata and Members for a Single Committee."""

from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field

api_prefix = SystemService().system_settings.api_settings.prefix

chamber_options: list[dict] = [
    {"label": "Senate", "value": "senate"},
    {"label": "House", "value": "house"},
    {"label": "Joint", "value": "joint"},
]


class CongressCommitteeInfoQueryParams(QueryParams):
    """Congress Committee Info Query Parameters."""

    __json_schema_extra__ = {
        "chamber": {
            "x-widget_config": {
                "label": "Chamber",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/uscongress/committee_choices",
                "optionsParams": {
                    "congress": "$congress",
                    "is_workspace": True,
                },
            },
        },
        "committee": {
            "x-widget_config": {
                "label": "Committee",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/uscongress/committee_choices",
                "optionsParams": {
                    "chamber": "$chamber",
                    "congress": "$congress",
                    "is_workspace": True,
                },
                "style": {"popupWidth": 700},
                "row": 1,
            },
        },
        "subcommittee": {
            "x-widget_config": {
                "label": "Subcommittee",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/uscongress/committee_choices",
                "optionsParams": {
                    "chamber": "$chamber",
                    "committee": "$committee",
                    "subcommittees": True,
                    "is_workspace": True,
                },
                "style": {"popupWidth": 750},
                "row": 1,
            },
        },
    }

    chamber: Literal["house", "senate", "joint"] = Field(
        default="senate",
        description="Chamber: house, senate, or joint.",
    )
    committee: str = Field(
        default="ssaf00",
        description="System code of the committee (e.g., ssaf00, hsju00).",
    )
    subcommittee: str | None = Field(
        default=None,
        description="System code of a subcommittee (e.g., ssga22). Leave empty for parent committee.",
    )


class CongressCommitteeInfoData(Data):
    """Congress Committee Info Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "markdown",
                "$.name": "Congressional Committee Info",
                "$.description": "Membership, subcommittees, and metadata "
                + "for a U.S. Congressional Committee. Select a chamber and committee to view details.",
                "$.category": "Government",
                "$.subCategory": "Congress",
                "$.data": {
                    "dataKey": "results.markdown_content",
                },
                "$.refetchInterval": False,
            }
        }
    )

    markdown_content: str = Field(
        description="Committee metadata and membership formatted as Markdown."
    )
    raw_data: dict[str, Any] = Field(
        description="Raw JSON data from the committee detail and member lookups.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )


class CongressCommitteeInfoFetcher(
    Fetcher[CongressCommitteeInfoQueryParams, CongressCommitteeInfoData]
):
    """Congress Committee Info Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CongressCommitteeInfoQueryParams:
        """Transform the query params."""
        return CongressCommitteeInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressCommitteeInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs,
    ) -> dict:
        """Extract committee structure + members from keyless sources."""
        from openbb_congress_gov.utils.committees import get_committee_overview

        system_code = (
            query.subcommittee if query.subcommittee else query.committee
        ).lower()

        return await get_committee_overview(system_code, query.chamber.lower())

    @staticmethod
    def transform_data(
        query: CongressCommitteeInfoQueryParams,
        data: dict,
        **kwargs,
    ) -> CongressCommitteeInfoData:
        """Transform the raw data into a CongressCommitteeInfoData instance."""
        system_code = data.get("system_code", "")
        detail = data.get("detail", {})
        members = data.get("members", [])

        name = detail.get("name") or system_code.upper()
        md = f"# {name}\n\n## Overview\n\n| Field | Value |\n|---|---|\n"

        meta_rows = [
            ("Chamber", detail.get("chamber", "").title()),
            ("Type", detail.get("type", "")),
            ("System Code", f"`{system_code}`"),
        ]
        if detail.get("is_subcommittee") and detail.get("parent_name"):
            meta_rows.append(("Parent Committee", detail["parent_name"]))
        if detail.get("website"):
            website = detail["website"]
            meta_rows.append(("Website", f"[{website}]({website})"))

        for label, val in meta_rows:
            md += f"| {label} | {val} |\n"

        if detail.get("jurisdiction"):
            md += f"\n## Jurisdiction\n\n{detail['jurisdiction']}\n"

        subcommittees = detail.get("subcommittees") or []
        if subcommittees:
            md += f"\n## Subcommittees ({len(subcommittees)})\n\n"
            for sub in subcommittees:
                sub_name = sub.get("name", "")
                sub_code = sub.get("systemCode", "")
                if sub_name:
                    md += f"- **{sub_name}** (`{sub_code}`)\n"

        if members:
            chair = [
                m
                for m in members
                if m.get("title", "").lower()
                in ("chair", "chairman", "chairwoman", "chairperson")
            ]
            ranking = [m for m in members if "ranking" in m.get("title", "").lower()]
            rest = [m for m in members if m not in chair and m not in ranking]
            md += f"\n## Members ({len(members)})\n\n"
            md += "| Name | Party | Title |\n|---|---|---|\n"

            for m in chair + ranking + rest:
                name_val = m.get("name", "Unknown")
                party = m.get("party", "")
                title = m.get("title") or "Member"
                md += f"| {name_val} | {party} | {title} |\n"
        else:
            md += "\n*Member data not available for this committee.*\n"

        return CongressCommitteeInfoData(
            markdown_content=md,
            raw_data=data,
        )
