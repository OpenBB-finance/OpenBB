"""Congress Amendment Info Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field


class CongressAmendmentInfoQueryParams(QueryParams):
    """Congress Amendment Info Query."""

    __json_schema_extra__ = {
        "amendment_id": {
            "x-widget_config": {
                "label": "Amendment ID",
                "description": "Enter an amendment id (e.g., '119-hamdt-2'). Or group"
                + " the 'Congressional Amendments' widget by 'Amendment ID' and click"
                + " a cell to view this amendment's details.",
                "value": "119-hamdt-2",
            },
        }
    }

    amendment_id: str = Field(
        description="The amendment id, e.g. '119-hamdt-2' (congress-type-number)."
    )


class CongressAmendmentInfoData(Data):
    """Congress Amendment Info Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "markdown",
                "$.name": "Congressional Amendment Info",
                "$.description": "Metadata and details for a U.S. Congressional Amendment.",
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
        description="Aggregated metadata for the amendment in Markdown format."
    )
    raw_data: dict[str, Any] = Field(
        description="Raw JSON data from the collected amendment information.",
        json_schema_extra={
            "x-widget_config": {
                "exclude": True,
            }
        },
    )


class CongressAmendmentInfoFetcher(
    Fetcher[CongressAmendmentInfoQueryParams, CongressAmendmentInfoData]
):
    """Congress Amendment Info Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CongressAmendmentInfoQueryParams:
        """Transform the query parameters."""
        return CongressAmendmentInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressAmendmentInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract a single amendment's full record from the BILLSTATUS archives."""
        from openbb_congress_gov.utils.bulk import load_amendment_record

        return await load_amendment_record(query.amendment_id)

    @staticmethod
    def transform_data(
        query: CongressAmendmentInfoQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> CongressAmendmentInfoData:
        """Transform the data into the model."""
        number = data.get("number", "")
        amendment_type = data.get("type", "")
        congress = data.get("congress", "")
        description = data.get("description", "")
        purpose = data.get("purpose", "")
        header = (
            description or purpose or f"Amendment {congress} {amendment_type} {number}"
        )

        markdown_content = f"# {header}\n\n"
        if purpose and purpose != description:
            markdown_content += f"> {purpose}\n\n"
        markdown_content += f"- **Congress**: {congress}\n"
        markdown_content += f"- **Number**: {number}\n"
        markdown_content += f"- **Type**: {amendment_type}\n"
        markdown_content += f"- **Chamber**: {data.get('chamber', '')}\n"

        submitted_at = data.get("submittedDate") or data.get("proposedDate")
        if submitted_at:
            markdown_content += f"- **Submitted**: {submitted_at}\n"

        markdown_content += f"- **Last Updated**: {data.get('updateDate', '')}\n"

        latest_action = data.get("latestAction", {})
        if latest_action and (
            latest_action.get("actionDate") or latest_action.get("text")
        ):
            markdown_content += (
                f"- **Latest Action**: {latest_action.get('actionDate', '')} - "
                f"{latest_action.get('text', '')}\n"
            )

        amended_bill = data.get("amendedBill", {})
        if amended_bill:
            bill_congress = amended_bill.get("congress", "")
            bill_type = amended_bill.get("type", "")
            bill_number = amended_bill.get("number", "")
            bill_title = amended_bill.get("title", "")
            markdown_content += (
                f"\n### Amended Bill\n\n"
                f"- **{bill_congress} {bill_type} {bill_number}**: {bill_title}\n"
            )

        amended_amendment = data.get("amendedAmendment", {})
        if amended_amendment:
            aa_congress = amended_amendment.get("congress", "")
            aa_type = amended_amendment.get("type", "")
            aa_number = amended_amendment.get("number", "")
            markdown_content += (
                f"\n### Amends Amendment\n\n- **{aa_congress} {aa_type} {aa_number}**\n"
            )

        sponsors = data.get("sponsors", [])
        if sponsors:
            markdown_content += "\n### Sponsors\n\n"
            for sponsor in sponsors:
                markdown_content += f"- **{sponsor.get('fullName', '')}**"
                if sponsor.get("party"):
                    markdown_content += f" ({sponsor.get('party', '')})"
                markdown_content += "\n"

        cosponsors = data.get("cosponsors", {})
        if isinstance(cosponsors, list) and cosponsors:
            markdown_content += "\n### Cosponsors\n\n"
            for cosponsor in cosponsors:
                cosponsor_name = cosponsor.get("fullName", "")
                markdown_content += f"- **{cosponsor_name}**"
                if cosponsor.get("party"):
                    markdown_content += f" ({cosponsor.get('party', '')})"
                markdown_content += "\n"
        elif isinstance(cosponsors, dict) and cosponsors.get("count", 0):
            markdown_content += (
                f"\n### Cosponsors\n\n- **Count**: {cosponsors['count']}\n"
            )

        text_versions = data.get("textVersions", [])
        if text_versions and isinstance(text_versions, list):
            markdown_content += "\n### Text Versions\n\n"
            for version in text_versions:
                version_date = version.get("date", "")
                version_type = version.get("type", "")
                markdown_content += f"- **{version_type}** ({version_date})\n"
                for fmt in version.get("formats", []):
                    fmt_type = fmt.get("type", "")
                    fmt_url = fmt.get("url", "")
                    markdown_content += f"  - [{fmt_type}]({fmt_url})\n"

        actions = data.get("actions", [])
        if actions and isinstance(actions, list):
            markdown_content += "\n### Actions\n\n"
            for action in actions:
                action_date = action.get("actionDate", "")
                action_text = action.get("text", "")
                action_type = action.get("type", "")
                markdown_content += f"\n- **{action_date}**: ({action_type})"
                markdown_content += f"\n  - {action_text}"

        return CongressAmendmentInfoData(
            markdown_content=markdown_content, raw_data=data
        )
