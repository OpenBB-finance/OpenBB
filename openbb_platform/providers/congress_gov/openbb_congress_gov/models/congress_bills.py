"""Congress Bills Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal, Optional

from openbb_congress_gov.utils.constants import (
    BillTypes,
    base_url,
    bill_type_docstring,
    bill_type_options,
)
from openbb_congress_gov.utils.helpers import year_to_congress
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import ConfigDict, Field, model_validator


class CongressBillsQueryParams(QueryParams):
    """Congress Bills Query Parameters."""

    __json_schema_extra__ = {
        "bill_type": {
            "x-widget_config": {
                "options": bill_type_options,
                "value": None,
                "style": {"popupWidth": 300},
                "paramName": "bill_type",
                "label": "Bill Type",
            },
        },
        "offset": {
            "x-widget_config": {
                "type": "number",
            }
        },
        "congress": {
            "x-widget_config": {
                "type": "number",
            },
        },
    }
    congress: Optional[int] = Field(
        default=None,
        description="Congress number (e.g., 118 for the 118th Congress)."
        + " The 103rd Congress started in 1993,"
        + " which is the earliest date supporting full text versions."
        + " Each Congress spans two years,"
        + " starting in odd-numbered years.",
    )
    bill_type: Optional[str] = Field(
        default=None,
        description=bill_type_docstring,
        examples=["hr", "s", "hjres", "sjres", "hconres", "sconres", "hres", "sres"],
    )
    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Filters bills by the last updated date.",
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " Filters bills by the last updated date.",
    )
    limit: Optional[int] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + " When None, default sets to 100 (max 250)."
        + " Set to 0 for no limit (must be used with 'bill_type' and 'congress').",
    )
    offset: Optional[int] = Field(
        default=None, description="The starting record returned. 0 is the first record."
    )
    sort_by: Literal["asc", "desc"] = Field(
        default="desc", description="Sort by update date. Default is latest first."
    )

    @model_validator(mode="after")
    @classmethod
    def validate_query(cls, values):
        """Validate the query parameters."""

        if values.congress is not None and values.bill_type is None:
            raise ValueError(
                "'bill_type' must be specified when 'congress' is provided."
            )

        if values.bill_type is not None and values.bill_type not in BillTypes:
            raise ValueError(
                f"Invalid bill_type: {values.bill_type}. Must be one of: {', '.join(BillTypes)}."
            )

        if values.limit == 0 and values.bill_type is None:
            raise ValueError(
                "'limit' cannot be set to 0 without 'bill_type' and 'congress'."
            )

        if (
            values.bill_type is not None
            and values.start_date is not None
            and values.end_date is not None
        ):
            start_year = values.start_date.year
            end_year = values.end_date.year
            congress_start = year_to_congress(start_year)
            congress_end = year_to_congress(end_year)
            if congress_start != congress_end:
                raise ValueError(
                    "Start and end dates must be in the same Congress session."
                )

        return values


class CongressBillsData(Data):
    """Congress Bills Data."""

    __alias_dict__ = {
        "bill_type": "type",
        "bill_number": "number",
        "bill_url": "url",
    }

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Congressional Bills",
                "$.category": "Government",
                "$.subcategory": "Congress",
                "$.searchCategory": "Government",
                "$.description": "Current and historical U.S. Congressional Bills.",
                "$.label": "Congress Bills",
                "$.params": [
                    {
                        "paramName": "bill_url",
                        "label": "Bill URL",
                        "description": "Ghost parameter to group by the bill URL."
                        + " Create a group and use the 'Congressional Bills Viewer' widget to view the bill.",
                        "type": "text",
                        "value": None,
                        "show": True,
                    },
                ],
            },
        }
    )
    update_date: dateType = Field(description="The date the bill was last updated.")
    latest_action_date: Optional[dateType] = Field(
        default=None, description="The date of the latest action on the bill."
    )
    bill_url: str = Field(
        description="Base URL to the bill for the congress.gov API.",
        json_schema_extra={
            "x-widget_config": {
                "headerTooltip": "Click to change the documents in the Congressional Bills Viewer widget.",
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "bill_url",
                },
            },
        },
    )
    congress: int = Field(
        description="The congress session number.",
        json_schema_extra={
            "x-widget_config": {"formatterFn": "none"},
        },
    )
    bill_number: int = Field(
        description="The bill number.",
        json_schema_extra={
            "x-widget_config": {"formatterFn": "none"},
        },
    )
    origin_chamber: str = Field(description="The chamber where the bill originated.")
    origin_chamber_code: str = Field(
        description="The chamber code where the bill originated.",
        json_schema_extra={
            "x-widget_config": {
                "hide": True,
            },
        },
    )
    bill_type: str = Field(
        description="The type of bill (e.g., HR, S).",
    )
    title: str = Field(description="The title of the bill.")
    latest_action: Optional[str] = Field(
        default=None, description="Latest action information for the bill."
    )
    update_date_including_text: Optional[datetime] = Field(
        default=None,
        description="The date and time the bill text was last updated.",
        json_schema_extra={"x-widget_config": {"label": "Text Update Date"}},
    )


class CongressBillsFetcher(
    Fetcher[
        CongressBillsQueryParams,
        list[CongressBillsData],
    ]
):
    """Transform the query, extract and transform the data from the Congress API."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CongressBillsQueryParams:
        """Transform the query params."""
        return CongressBillsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressBillsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list:
        """Extract data from the Congress API."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request  # noqa
        from openbb_congress_gov.utils.helpers import (
            get_all_bills_by_type,
            year_to_congress,
        )

        api_key = credentials.get("congress_gov_api_key") if credentials else ""

        if (
            query.bill_type is not None
            and query.start_date is None
            and query.end_date is None
            and query.congress is None
        ):
            congress = year_to_congress(datetime.now().year)
        elif (
            query.bill_type is not None
            and query.congress is None
            and query.start_date is not None
        ):
            congress = year_to_congress(query.start_date.year)
        elif (
            query.bill_type is not None
            and query.congress is None
            and query.end_date is not None
            and query.start_date is None
        ):
            congress = year_to_congress(query.end_date.year)
        elif (
            query.bill_type is not None
            and query.start_date is not None
            and query.end_date is not None
        ):
            end_year = query.end_date.year
            congress_end = year_to_congress(end_year)
            congress = congress_end
        elif query.bill_type is not None and query.congress is None:
            congress = year_to_congress(datetime.now().year)
        else:
            congress = None

        url = (
            (
                f"{base_url}bill/{congress}/{query.bill_type}"
                if congress is not None
                else f"{base_url}bill"
            )
            + (
                f"?fromDateTime={query.start_date.strftime('%Y-%m-%d') + 'T00:00:00Z'}"
                if query.start_date
                else ""
            )
            + (
                f"&toDateTime={query.end_date.strftime('%Y-%m-%d') + 'T23:59:59Z'}"
                if query.end_date
                else ""
            )
        )
        url += (
            f"{'?' if '?' not in url else '&'}"
            + f"limit={query.limit if query.limit is not None else '100'}"
            + (f"&offset={query.offset if query.offset else '0'}")
            + f"&sort=updateDate+{query.sort_by}"
            + f"&format=json&api_key={api_key}"
        )

        if query.limit == 0 and query.bill_type and congress:
            # If limit is 0, we fetch all bills of the specified type for the congress
            return await get_all_bills_by_type(
                bill_type=query.bill_type,
                congress=congress,
                start_date=(
                    query.start_date.strftime("%Y-%m-%d") if query.start_date else None
                ),
                end_date=(
                    query.end_date.strftime("%Y-%m-%d") if query.end_date else None
                ),
            )
        try:
            response = await amake_request(url=url)
        except Exception as e:
            # Handle exceptions
            raise OpenBBError(e) from e

        return response.get("bills", [])  # type: ignore

    @staticmethod
    def transform_data(
        query: CongressBillsQueryParams, data: list, **kwargs: Any
    ) -> list[CongressBillsData]:
        """Transform raw data into CongressBillsData models."""
        transformed_data: list[CongressBillsData] = []

        for bill in sorted(
            data,
            key=lambda x: x.get("updateDate"),
            reverse=query.sort_by == "desc",
        ):
            latest_action = bill.pop("latestAction", {})

            if latest_action:
                bill["latest_action_date"] = latest_action.get("actionDate")
                bill["latest_action"] = latest_action.get("text")

            transformed_data.append(CongressBillsData(**bill))

        return transformed_data
