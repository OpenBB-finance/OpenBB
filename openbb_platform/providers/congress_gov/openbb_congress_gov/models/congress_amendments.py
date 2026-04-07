"""Congress Amendments Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Literal

from openbb_congress_gov.utils.constants import (
    AmendmentTypes,
    amendment_type_docstring,
    amendment_type_options,
    base_url,
)
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, model_validator


class CongressAmendmentsQueryParams(QueryParams):
    """Congress Amendments Query Parameters."""

    __json_schema_extra__ = {
        "amendment_type": {
            "x-widget_config": {
                "options": amendment_type_options,
                "value": None,
                "style": {"popupWidth": 200},
                "paramName": "amendment_type",
                "label": "Amendment Type",
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
            }
        },
    }

    congress: int | None = Field(
        default=None,
        description="Congress number (e.g., 119 for the 119th Congress)."
        + " When None, returns amendments across all congresses (requires amendment_type).",
    )
    amendment_type: str | None = Field(
        default=None,
        description=amendment_type_docstring,
        examples=["hamdt", "samdt"],
    )
    start_date: dateType | None = Field(
        default=None,
        description="Filter amendments updated on or after this date.",
    )
    end_date: dateType | None = Field(
        default=None, description="Filter amendments updated on or before this date."
    )
    limit: int | None = Field(
        default=None,
        description="Maximum number of results to return. When None, defaults to 100 (max 250)."
        + " Set to 0 for no limit (must be used with 'amendment_type').",
    )
    offset: int | None = Field(
        default=None, description="The starting record returned. 0 is the first record."
    )
    sort_by: Literal["asc", "desc"] = Field(
        default="desc", description="Sort by update date. Default is latest first."
    )

    @model_validator(mode="after")
    @classmethod
    def validate_query(cls, values):
        """Validate the query parameters."""
        if (
            values.amendment_type is not None
            and values.amendment_type not in AmendmentTypes
        ):
            raise OpenBBError(
                ValueError(
                    f"Invalid amendment_type: {values.amendment_type}."
                    f" Must be one of: {', '.join(AmendmentTypes)}."
                )
            )
        if values.limit == 0 and values.amendment_type is None:
            raise OpenBBError(
                ValueError("'limit' cannot be set to 0 without 'amendment_type'.")
            )
        return values


class CongressAmendmentsData(Data):
    """Congress Amendments Data."""

    __alias_dict__ = {
        "amendment_type": "type",
        "amendment_url": "url",
    }

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Congressional Amendments",
                "$.category": "Government",
                "$.subCategory": "Congress",
                "$.description": "Current and historical U.S. Congressional Amendments.",
                "$.params": [
                    {
                        "paramName": "amendment_url",
                        "label": "Amendment URL",
                        "description": "Ghost parameter to group by the amendment URL."
                        + " Create a group and use the 'Congressional Amendment Info' widget to view details."
                        + " The 'Congressional Amendment Text Viewer' widget can also be grouped by this field.",
                        "type": "text",
                        "value": None,
                        "show": True,
                    },
                ],
                "$.refetchInterval": False,
            },
        }
    )

    congress: int = Field(
        description="The congress session number.",
        json_schema_extra={"x-widget_config": {"formatterFn": "none"}},
    )
    amendment_type: str = Field(
        description="The type of amendment (e.g., HAMDT, SAMDT).",
        json_schema_extra={"x-widget_config": {"label": "Type"}},
    )
    number: str = Field(
        description="The amendment number.",
        json_schema_extra={
            "x-widget_config": {"formatterFn": "none", "label": "Amendment No."},
        },
    )
    amended_bill: str | None = Field(
        default=None,
        description="The bill being amended (e.g., 'HR 1234' or 'S 456').",
        json_schema_extra={"x-widget_config": {"label": "Amended Bill"}},
    )
    amended_bill_title: str | None = Field(
        default=None,
        description="The title of the bill being amended.",
        json_schema_extra={"x-widget_config": {"label": "Bill Title"}},
    )
    description: str | None = Field(
        default=None,
        description="A short description of the amendment.",
    )
    purpose: str | None = Field(
        default=None,
        description="The purpose of the amendment.",
    )
    latest_action_date: dateType | None = Field(
        default=None, description="The date of the latest action."
    )
    latest_action: str | None = Field(default=None, description="Latest action text.")
    latest_action_time: str | None = Field(
        default=None,
        description="The time of the latest action.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    sponsor: str | None = Field(
        default=None,
        description="The primary sponsor of the amendment.",
        json_schema_extra={"x-widget_config": {"label": "Sponsor"}},
    )
    submitted_date: dateType | None = Field(
        default=None,
        description="The date the amendment was submitted.",
        json_schema_extra={"x-widget_config": {"label": "Submitted"}},
    )
    update_date: dateType | None = Field(
        default=None, description="The date the record was last updated."
    )
    amendment_url: str = Field(
        description="Base URL to the amendment for the congress.gov API.",
        json_schema_extra={
            "x-widget_config": {
                "headerTooltip": "Create a group for the 'amendment_url' parameter and then"
                + " click in the cell to change the documents in the"
                + " 'Congressional Amendment Info' or 'Congressional Amendment Text Viewer' widgets.",
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "amendment_url",
                },
            },
        },
    )


class CongressAmendmentsFetcher(
    Fetcher[
        CongressAmendmentsQueryParams,
        list[CongressAmendmentsData],
    ]
):
    """Transform the query, extract and transform the data from the Congress API."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CongressAmendmentsQueryParams:
        """Transform the query params."""
        return CongressAmendmentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressAmendmentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Extract data from the Congress API."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        from openbb_congress_gov.utils.helpers import get_all_amendments_by_type
        from openbb_core.provider.utils.errors import UnauthorizedError
        from openbb_core.provider.utils.helpers import amake_request

        api_key = credentials.get("congress_gov_api_key") if credentials else ""

        if query.limit == 0 and query.amendment_type is not None:
            if query.congress is None:
                raise OpenBBError(
                    ValueError("'congress' is required when 'limit' is set to 0.")
                )

            return await get_all_amendments_by_type(
                congress=query.congress,
                amendment_type=query.amendment_type,
            )

        url = f"{base_url}amendment"

        if query.congress is not None:
            url += f"/{query.congress}"

            if query.amendment_type is not None:
                url += f"/{query.amendment_type}"

        url += f"?limit={query.limit if query.limit is not None else 100}"
        url += f"&offset={query.offset if query.offset else 0}"
        url += f"&sort=updateDate+{query.sort_by}"

        if query.start_date:
            url += f"&fromDateTime={query.start_date}T00:00:00Z"

        if query.end_date:
            url += f"&toDateTime={query.end_date}T23:59:59Z"

        url += f"&format=json&api_key={api_key}"

        try:
            response = await amake_request(url=url)

            if isinstance(response, dict) and (error := response.get("error", {})):
                if "API_KEY" in error.get("code", ""):
                    raise UnauthorizedError(
                        f"{error.get('code', '')} -> {error.get('message', '')}"
                    )
                raise OpenBBError(  # noqa: TRY301
                    f"{error.get('code', '')} -> {error.get('message', '')}"
                )
        except OpenBBError:
            raise
        except Exception as e:
            raise OpenBBError(e) from e

        amendments = response.get("amendments", [])  # type: ignore

        if not amendments:
            return []

        detail_urls = [
            a["url"].split("?")[0] + f"?format=json&api_key={api_key}"
            for a in amendments
            if "url" in a
        ]
        detail_responses = await asyncio.gather(
            *[amake_request(u) for u in detail_urls],
            return_exceptions=True,
        )

        for amendment, detail_resp in zip(amendments, detail_responses):
            if not isinstance(detail_resp, dict):
                continue

            detail = detail_resp.get("amendment", {})

            for field in (
                "amendedBill",
                "amendedAmendment",
                "sponsors",
                "submittedDate",
                "purpose",
            ):
                if field in detail and field not in amendment:
                    amendment[field] = detail[field]

            for field in ("latestAction", "description"):
                if field not in amendment and field in detail:
                    amendment[field] = detail[field]

        return amendments

    @staticmethod
    def transform_data(
        query: CongressAmendmentsQueryParams, data: list, **kwargs: Any
    ) -> list[CongressAmendmentsData]:
        """Transform raw data into CongressAmendmentsData models."""
        transformed_data: list[CongressAmendmentsData] = []

        for amendment in sorted(
            data,
            key=lambda x: x.get("latestAction", {}).get("actionDate")
            or x.get("updateDate"),
            reverse=query.sort_by == "desc",
        ):
            latest_action = amendment.pop("latestAction", {})

            if latest_action:
                amendment["latest_action_date"] = latest_action.get("actionDate")
                amendment["latest_action_time"] = latest_action.get("actionTime")
                amendment["latest_action"] = latest_action.get("text")

            amended_bill = amendment.pop("amendedBill", {}) or {}

            if amended_bill:
                bill_type = amended_bill.get("type", "")
                bill_number = amended_bill.get("number", "")
                amendment["amended_bill"] = f"{bill_type} {bill_number}".strip() or None
                amendment["amended_bill_title"] = amended_bill.get("title") or None

            amended_amendment = amendment.pop("amendedAmendment", {}) or {}

            if amended_amendment and not amendment.get("amended_bill"):
                aa_type = amended_amendment.get("type", "")
                aa_number = amended_amendment.get("number", "")
                amendment["amended_bill"] = (
                    f"Amdt. {aa_type} {aa_number}".strip() or None
                )

            sponsors = amendment.pop("sponsors", []) or []

            if sponsors:
                amendment["sponsor"] = sponsors[0].get("fullName") or None

            if submitted := amendment.pop("submittedDate", None):
                amendment["submitted_date"] = submitted[:10]

            if update_date := amendment.get("updateDate"):
                amendment["updateDate"] = update_date[:10]

            transformed_data.append(CongressAmendmentsData(**amendment))

        return transformed_data
