"""Congress Laws Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import ConfigDict, Field

from openbb_congress_gov.utils.constants import law_type_docstring, law_type_options


class CongressLawsQueryParams(QueryParams):
    """Congress Laws Query Parameters."""

    __json_schema_extra__ = {
        "law_type": {
            "x-widget_config": {
                "options": law_type_options,
                "paramName": "law_type",
                "label": "Law Type",
            },
        },
        "congress": {
            "x-widget_config": {
                "type": "number",
            },
        },
        "offset": {
            "x-widget_config": {
                "type": "number",
            },
        },
    }

    congress: int | None = Field(
        default=None,
        description="Congress number (e.g., 119 for the 119th Congress)."
        + " When None, defaults to the current Congress.",
    )
    law_type: Literal["public", "private"] = Field(
        default="public",
        description=law_type_docstring,
    )
    limit: int | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + " When None, default sets to 100. Set to 0 for no limit.",
    )
    offset: int | None = Field(
        default=None,
        description="The starting record returned. 0 is the first record.",
    )
    sort_by: Literal["asc", "desc"] = Field(
        default="desc", description="Sort by law number. Default is highest first."
    )


class CongressLawsData(Data):
    """Congress Laws Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Congressional Laws",
                "$.category": "Government",
                "$.subCategory": "Congress",
                "$.description": "Public and private laws enacted by the U.S. Congress.",
                "$.params": [
                    {
                        "paramName": "law_id",
                        "label": "Law ID",
                        "description": "Ghost parameter to group by the law id."
                        + " Create a group and use the 'Congressional Law Viewer'"
                        + " widget to view the law text.",
                        "type": "text",
                        "value": None,
                        "show": True,
                    },
                ],
                "$.refetchInterval": False,
            },
        }
    )

    law_id: str = Field(
        description="The law identifier, e.g. '119-1'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "▸ Group: Law ID",
                "headerTooltip": "Click a cell here to group by this law and view it"
                + " in the 'Congressional Law Viewer' widget.",
                "pinned": "left",
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "law_id",
                },
            },
        },
    )
    law_number: int = Field(
        description="The law number within the Congress.",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    law_type: str = Field(description="The type of law (public or private).")
    congress: int = Field(
        description="The congress session number.",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    enacted_date: dateType | None = Field(
        default=None, description="The date the law was approved/enacted."
    )
    title: str = Field(description="The title of the law.")
    citation: str = Field(description="The public/private law citation.")
    statute_citation: str | None = Field(
        default=None, description="The Statutes at Large citation."
    )
    package_id: str = Field(
        description="The GovInfo package identifier for the law.",
    )
    pdf: str = Field(
        description="URL to the law text in PDF format.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    htm: str = Field(
        description="URL to the law text in HTML format.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    xml: str = Field(
        description="URL to the law text in XML format.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )


class CongressLawsFetcher(
    Fetcher[
        CongressLawsQueryParams,
        list[CongressLawsData],
    ]
):
    """Transform the query, extract and transform data from the GovInfo PLAW bulk data."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CongressLawsQueryParams:
        """Transform the query params."""
        return CongressLawsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressLawsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Extract enacted laws from the GovInfo PLAW bulk archive."""
        from openbb_congress_gov.utils.bulk import filter_laws, load_plaw
        from openbb_congress_gov.utils.helpers import year_to_congress

        congress = (
            query.congress
            if query.congress is not None
            else year_to_congress(datetime.now().year)
        )
        records = await load_plaw(congress, query.law_type)

        return filter_laws(
            records,
            limit=query.limit,
            offset=query.offset,
            sort_by=query.sort_by,
        )

    @staticmethod
    def transform_data(
        query: CongressLawsQueryParams, data: list, **kwargs: Any
    ) -> list[CongressLawsData]:
        """Transform raw law records into CongressLawsData models."""
        return [CongressLawsData(**record) for record in data]
