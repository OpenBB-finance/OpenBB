"""Congress Committee Info Model - Widget 2: Metadata and Members for a Single Committee."""

# pylint: disable=unused-argument

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
        """Extract data from the Congress API."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        from openbb_congress_gov.utils.committees import get_committee_members
        from openbb_core.provider.utils.helpers import amake_request

        api_key = credentials.get("congress_gov_api_key", "") if credentials else ""
        system_code = (
            query.subcommittee if query.subcommittee else query.committee
        ).lower()
        chamber = query.chamber.lower()
        detail_url = (
            f"https://api.congress.gov/v3/committee/{chamber}/{system_code}"
            f"?format=json&api_key={api_key}"
        )

        detail_resp, members = await asyncio.gather(
            amake_request(detail_url),
            get_committee_members(system_code),
            return_exceptions=True,
        )
        detail = {} if isinstance(detail_resp, Exception) else detail_resp.get("committee", {})  # type: ignore

        if isinstance(members, Exception):
            members = []

        return {
            "chamber": chamber,
            "system_code": system_code,
            "detail": detail,
            "members": members,
        }

    @staticmethod
    def transform_data(
        query: CongressCommitteeInfoQueryParams,
        data: dict,
        **kwargs,
    ) -> CongressCommitteeInfoData:
        """Transform the raw data into a CongressCommitteeInfoData instance."""
        chamber = data.get("chamber", "")
        system_code = data.get("system_code", "")
        detail = data.get("detail", {})
        members = data.get("members", [])
        history = detail.get("history", [])
        name = ""

        for h in reversed(history):
            candidate = h.get("officialName") or h.get("libraryOfCongressName") or ""
            if candidate:
                name = candidate
                break

        if not name:
            name = system_code.upper()

        committee_type = detail.get("type", "")
        website = detail.get("committeeWebsiteUrl") or ""
        is_current = detail.get("isCurrent", True)
        update_date = (detail.get("updateDate") or "")[:10]
        reports_info = detail.get("reports") or {}
        bills_info = detail.get("bills") or {}
        nominations_info = detail.get("nominations") or {}
        comms_info = detail.get("communications") or {}
        subcommittees = detail.get("subcommittees") or []
        md = f"# {name}\n\n"
        meta_rows = [
            ("Chamber", chamber.title()),
            ("Type", committee_type),
            ("System Code", f"`{system_code}`"),
            ("Current", "Yes" if is_current else "No"),
            ("Last Updated", update_date),
        ]

        if website:
            meta_rows.append(("Website", f"[{website}]({website})"))

        md += "## Overview\n\n"
        md += "| Field | Value |\n|---|---|\n"

        for label, val in meta_rows:
            md += f"| {label} | {val} |\n"

        md += "\n## Activity Counts\n\n"
        md += "| Type | Count |\n|---|---|\n"

        for label, info in [
            ("Reports", reports_info),
            ("Bills Referred", bills_info),
            ("Nominations", nominations_info),
            ("Communications", comms_info),
        ]:
            if isinstance(info, dict):
                count = info.get("count", 0)

                if count:
                    md += f"| {label} | {count:,} |\n"

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

        if history:
            md += "\n## Historical Names\n\n"

            for h in history:
                official = h.get("officialName") or h.get("libraryOfCongressName") or ""
                start = (h.get("startDate") or "")[:10]
                end = (h.get("endDate") or "present")[:10]
                if official:
                    md += f"- {official} ({start} – {end})\n"

        return CongressCommitteeInfoData(
            markdown_content=md,
            raw_data=data,
        )
