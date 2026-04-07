"""Congress Committee Documents Model."""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_congress_gov.utils.constants import doc_type_options
from openbb_congress_gov.utils.helpers import year_to_congress
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import ConfigDict, Field

api_prefix = SystemService().system_settings.api_settings.prefix


class CongressCommitteeDocumentsQueryParams(QueryParams):
    """Congress Committee Documents Query Parameters."""

    __json_schema_extra__ = {
        "congress": {
            "x-widget_config": {
                "label": "Congress",
                "type": "number",
            },
        },
        "chamber": {
            "x-widget_config": {
                "label": "Chamber",
                "options": [
                    {"label": "Senate", "value": "senate"},
                    {"label": "House", "value": "house"},
                    {"label": "Joint", "value": "joint"},
                ],
                "value": "senate",
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
                "value": "ssaf00",
                "style": {"popupWidth": 750},
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
        "doc_type": {
            "x-widget_config": {
                "options": doc_type_options,
                "value": "all",
                "paramName": "doc_type",
                "label": "Document Type",
                "style": {"popupWidth": 220},
            },
        },
        "limit": {
            "x-widget_config": {"type": "number"},
        },
        "offset": {
            "x-widget_config": {"type": "number"},
        },
    }

    congress: int | None = Field(
        default=None,
        description="Congress number (e.g., 119). Defaults to the current Congress.",
    )
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
    doc_type: Literal["all", "report", "meeting", "publication", "legislation"] = Field(
        default="all",
        description=(
            "Type of committee document to retrieve. "
            "Options: all (default), report, meeting, publication, legislation."
        ),
    )
    limit: int = Field(
        default=250,
        description=QUERY_DESCRIPTIONS.get("limit", "") + " Maximum 250.",
        ge=1,
        le=250,
    )
    offset: int = Field(
        default=0,
        description="Pagination offset.",
        ge=0,
    )
    use_cache: bool = Field(
        default=True,
        description="Use cached API responses. Set to False to bypass the cache.",
    )


class CongressCommitteeDocumentsData(Data):
    """Congress Committee Documents Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "table",
                "$.name": "Congressional Committee Documents",
                "$.description": (
                    "Documents produced by a U.S. Congressional Committee "
                    "(reports, hearings, meetings, publications/prints) "
                    "sourced from the congress.gov unified search."
                ),
                "$.category": "Government",
                "$.subCategory": "Congress",
                "$.refetchInterval": False,
            }
        }
    )

    doc_type: str = Field(description="Document type (report, meeting, publication).")
    citation: str | None = Field(
        default=None,
        description="Official citation (e.g., 'H. Rept. 119-5' or 'S. Hrg. 119-74').",
    )
    title: str | None = Field(
        default=None,
        description="Document title.",
    )
    congress: int | None = Field(
        default=None,
        description="Congress session number.",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    chamber: str | None = Field(
        default=None,
        description="Chamber (House, Senate, Joint).",
    )


class CongressCommitteeDocumentsFetcher(
    Fetcher[
        CongressCommitteeDocumentsQueryParams,
        list[CongressCommitteeDocumentsData],
    ]
):
    """Transform the query, extract and transform the data from the Congress API."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CongressCommitteeDocumentsQueryParams:
        """Transform the query params."""
        return CongressCommitteeDocumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressCommitteeDocumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract data from the Congress API."""
        # pylint: disable=import-outside-toplevel
        from datetime import datetime

        from openbb_congress_gov.utils.committees import fetch_committee_documents

        api_key = credentials.get("congress_gov_api_key", "") if credentials else ""

        chamber = query.chamber.lower()
        system_code = (query.subcommittee or query.committee).lower()
        congress = query.congress

        if congress is None:
            congress = year_to_congress(datetime.now().year)

        try:
            return await fetch_committee_documents(
                chamber=chamber,
                system_code=system_code,
                congress=congress,
                doc_type=query.doc_type,
                api_key=api_key,
                use_cache=query.use_cache,
            )
        except OpenBBError as e:
            raise OpenBBError(e) from None

    @staticmethod
    def transform_data(
        query: CongressCommitteeDocumentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CongressCommitteeDocumentsData]:
        """Transform raw data into CongressCommitteeDocumentsData models."""
        return [CongressCommitteeDocumentsData.model_validate(d) for d in data]
