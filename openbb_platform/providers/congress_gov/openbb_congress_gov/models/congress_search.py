"""Congress Full-Text Search Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import ConfigDict, Field

CollectionType = Literal["BILLS", "CRPT", "CHRG", "CPRT", "CREC", "CCAL", "CMR", "PLAW"]


class CongressSearchQueryParams(QueryParams):
    """Congress Search Query Parameters."""

    __json_schema_extra__ = {
        "collection": {
            "x-widget_config": {
                "options": [
                    {"label": "All Collections", "value": ""},
                    {"label": "Bills", "value": "BILLS"},
                    {"label": "Committee Reports", "value": "CRPT"},
                    {"label": "Hearings", "value": "CHRG"},
                    {"label": "Committee Prints", "value": "CPRT"},
                    {"label": "Congressional Record", "value": "CREC"},
                    {"label": "Calendars", "value": "CCAL"},
                    {"label": "Mandated Reports", "value": "CMR"},
                    {"label": "Public Laws", "value": "PLAW"},
                ],
                "label": "Collection",
            },
        },
        "congress": {"x-widget_config": {"type": "number"}},
    }

    query: str = Field(description="The full-text search query.")
    collection: CollectionType | None = Field(
        default=None,
        description="Restrict to a single GovInfo collection."
        + " When None, searches all congressional collections.",
    )
    congress: int | None = Field(
        default=None,
        description="Restrict results to a specific Congress number.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Filters by publish date.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " Filters by publish date.",
    )
    limit: int | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", "") + " When None, defaults to 20.",
    )
    offset: int | None = Field(
        default=None,
        description="The starting record returned. 0 is the first record.",
    )


class CongressSearchData(Data):
    """Congress Search Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Congressional Search",
                "$.category": "Government",
                "$.subCategory": "Congress",
                "$.description": "Full-text search across congressional GovInfo collections.",
                "$.params": [
                    {
                        "paramName": "package_id",
                        "label": "Package ID",
                        "description": "Ghost parameter to group by the document package."
                        + " Create a group and use the 'Congressional Search Viewer'"
                        + " widget to view the document.",
                        "type": "text",
                        "value": None,
                        "show": True,
                    },
                ],
                "$.refetchInterval": False,
            },
        }
    )

    package_id: str = Field(
        description="The GovInfo package identifier.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "▸ Group: Package ID",
                "headerTooltip": "Click a cell here to group by this document and view"
                + " it in the 'Congressional Search Viewer' widget.",
                "pinned": "left",
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "package_id",
                },
            },
        },
    )
    date: dateType | None = Field(
        default=None, description="The document publish date."
    )
    collection: str = Field(description="The GovInfo collection code.")
    congress: int | None = Field(
        default=None,
        description="The congress session number.",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    citation: str | None = Field(default=None, description="The document citation.")
    title: str = Field(description="The document title.")
    doc_url: str = Field(
        description="Direct URL to the document PDF.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )


class CongressSearchFetcher(
    Fetcher[
        CongressSearchQueryParams,
        list[CongressSearchData],
    ]
):
    """Transform the query, extract and transform data from the GovInfo search service."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CongressSearchQueryParams:
        """Transform the query params."""
        return CongressSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Search the congressional GovInfo collections (keyless)."""
        from openbb_congress_gov.utils.bulk import search_govinfo

        return await search_govinfo(
            query.query,
            collection=query.collection,
            congress=query.congress,
            start_date=query.start_date.isoformat() if query.start_date else None,
            end_date=query.end_date.isoformat() if query.end_date else None,
            limit=query.limit if query.limit else 20,
            offset=query.offset or 0,
        )

    @staticmethod
    def transform_data(
        query: CongressSearchQueryParams, data: list, **kwargs: Any
    ) -> list[CongressSearchData]:
        """Transform raw search records into CongressSearchData models."""
        return [CongressSearchData.model_validate(record) for record in data]
