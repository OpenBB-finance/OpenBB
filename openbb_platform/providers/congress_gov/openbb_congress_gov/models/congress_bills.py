"""Congress Bills Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import ConfigDict, Field, model_validator

from openbb_congress_gov.utils.constants import (
    BillTypes,
    bill_type_docstring,
    bill_type_options,
)
from openbb_congress_gov.utils.helpers import year_to_congress


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
    congress: int | None = Field(
        default=None,
        description="Congress number (e.g., 118 for the 118th Congress)."
        + " The 103rd Congress started in 1993,"
        + " which is the earliest date supporting full text versions."
        + " Each Congress spans two years,"
        + " starting in odd-numbered years.",
    )
    bill_type: str | None = Field(
        default=None,
        description=bill_type_docstring,
        examples=["hr", "s", "hjres", "sjres", "hconres", "sconres", "hres", "sres"],
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Filters bills by the last updated date.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " Filters bills by the last updated date.",
    )
    limit: int | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + " When None, default sets to 100 (max 250)."
        + " Set to 0 for no limit (must be used with 'bill_type' and 'congress')."
        + " Setting to 0 will nullify the start_date, end_date, and offset parameters.",
    )
    offset: int | None = Field(
        default=None, description="The starting record returned. 0 is the first record."
    )
    sort_by: Literal["asc", "desc"] = Field(
        default="desc", description="Sort by update date. Default is latest first."
    )

    @model_validator(mode="after")
    def validate_query(self):
        """Validate the query parameters."""
        if self.bill_type is not None and self.bill_type not in BillTypes:
            raise OpenBBError(
                ValueError(
                    f"Invalid bill_type: {self.bill_type}. Must be one of: {', '.join(BillTypes)}."
                )
            )
        if self.limit == 0 and self.bill_type is None:
            raise OpenBBError(
                ValueError(
                    "'limit' cannot be set to 0 without 'bill_type' and 'congress'."
                )
            )
        return self


class CongressBillsData(Data):
    """Congress Bills Data."""

    __alias_dict__ = {
        "bill_type": "type",
        "bill_number": "number",
    }

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "Congressional Bills",
                "$.category": "Government",
                "$.subCategory": "Congress",
                "$.description": "Current and historical U.S. Congressional Bills.",
                "$.params": [
                    {
                        "paramName": "bill_id",
                        "label": "Bill ID",
                        "description": "Ghost parameter to group by the bill id"
                        + " (e.g. '119-hr-29'). Create a group and use the"
                        + " 'Congressional Bill Viewer' / 'Congressional Bill Info'"
                        + " widgets to view the bill.",
                        "type": "text",
                        "value": None,
                        "show": True,
                    },
                ],
                "$.refetchInterval": False,
            },
        }
    )
    bill_id: str = Field(
        description="The bill identifier, e.g. '119-hr-29'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "▸ Group: Bill ID",
                "headerTooltip": "Click a cell here to group by this bill and view it"
                + " in the 'Congressional Bill Viewer' / 'Congressional Bill Info' widgets.",
                "pinned": "left",
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "bill_id",
                },
            },
        },
    )
    update_date: dateType = Field(description="The date the bill was last updated.")
    latest_action_date: dateType | None = Field(
        default=None, description="The date of the latest action on the bill."
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
    latest_action: str | None = Field(
        default=None, description="Latest action information for the bill."
    )
    update_date_including_text: datetime | None = Field(
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
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Extract bills for a Congress from the BILLSTATUS database."""
        from openbb_congress_gov.utils.bulk import list_bills

        if query.congress is not None:
            congress = query.congress
        elif query.start_date is not None:
            congress = year_to_congress(query.start_date.year)
        elif query.end_date is not None:
            congress = year_to_congress(query.end_date.year)
        else:
            congress = year_to_congress(datetime.now().year)

        bill_types = (
            [query.bill_type] if query.bill_type is not None else list(BillTypes)
        )

        return await list_bills(
            congress,
            bill_types,
            start_date=query.start_date,
            end_date=query.end_date,
            limit=query.limit,
            offset=query.offset,
            sort_by=query.sort_by,
        )

    @staticmethod
    def transform_data(
        query: CongressBillsQueryParams, data: list, **kwargs: Any
    ) -> list[CongressBillsData]:
        """Transform raw data into CongressBillsData models."""
        transformed_data: list[CongressBillsData] = []

        for bill in sorted(
            data,
            key=lambda x: (
                x.get("latestAction", {}).get("actionDate") or x.get("updateDate")
            ),
            reverse=query.sort_by == "desc",
        ):
            latest_action = bill.pop("latestAction", {})

            if latest_action:
                bill["latest_action_date"] = latest_action.get("actionDate")
                bill["latest_action"] = latest_action.get("text")

            transformed_data.append(CongressBillsData(**bill))

        return transformed_data
