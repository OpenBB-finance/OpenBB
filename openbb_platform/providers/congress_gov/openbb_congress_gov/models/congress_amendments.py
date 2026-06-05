"""Congress Amendments Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, model_validator

from openbb_congress_gov.utils.constants import (
    AmendmentTypes,
    amendment_type_docstring,
    amendment_type_options,
)
from openbb_congress_gov.utils.helpers import year_to_congress


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
        + " When None, defaults to the current Congress.",
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
    def validate_query(self):
        """Validate the query parameters."""
        if (
            self.amendment_type is not None
            and self.amendment_type not in AmendmentTypes
        ):
            raise OpenBBError(
                ValueError(
                    f"Invalid amendment_type: {self.amendment_type}."
                    f" Must be one of: {', '.join(AmendmentTypes)}."
                )
            )
        if self.limit == 0 and self.amendment_type is None:
            raise OpenBBError(
                ValueError("'limit' cannot be set to 0 without 'amendment_type'.")
            )
        return self


class CongressAmendmentsData(Data):
    """Congress Amendments Data."""

    __alias_dict__ = {
        "amendment_type": "type",
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
                        "paramName": "amendment_id",
                        "label": "Amendment ID",
                        "description": "Ghost parameter to group by the amendment id"
                        + " (e.g. '119-hamdt-2'). Create a group and use the"
                        + " 'Congressional Amendment Info' / 'Congressional Amendment"
                        + " Viewer' widgets to view the amendment.",
                        "type": "text",
                        "value": None,
                        "show": True,
                    },
                ],
                "$.refetchInterval": False,
            },
        }
    )

    amendment_id: str = Field(
        description="The amendment identifier, e.g. '119-hamdt-2'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "▸ Group: Amendment ID",
                "headerTooltip": "Click a cell here to group by this amendment and view"
                + " it in the 'Congressional Amendment Info' / 'Congressional Amendment"
                + " Viewer' widgets.",
                "pinned": "left",
                "renderFn": "cellOnClick",
                "renderFnParams": {
                    "actionType": "groupBy",
                    "groupByParamName": "amendment_id",
                },
            },
        },
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
        """Extract amendments from the GovInfo BILLSTATUS bulk archives."""
        from openbb_congress_gov.utils.bulk import (
            filter_amendments,
            load_amendments,
            to_amendment_list_item,
        )

        congress = (
            query.congress
            if query.congress is not None
            else year_to_congress(datetime.now().year)
        )
        records = await load_amendments(congress, query.amendment_type)
        items = [to_amendment_list_item(record) for record in records]

        return filter_amendments(
            items,
            start_date=query.start_date,
            end_date=query.end_date,
            limit=query.limit,
            offset=query.offset,
            sort_by=query.sort_by,
        )

    @staticmethod
    def transform_data(
        query: CongressAmendmentsQueryParams, data: list, **kwargs: Any
    ) -> list[CongressAmendmentsData]:
        """Transform raw data into CongressAmendmentsData models."""
        transformed_data: list[CongressAmendmentsData] = []

        for amendment in sorted(
            data,
            key=lambda x: (
                x.get("latestAction", {}).get("actionDate") or x.get("updateDate") or ""
            ),
            reverse=query.sort_by == "desc",
        ):
            latest_action = amendment.pop("latestAction", {})

            if latest_action:
                amendment["latest_action_date"] = (
                    latest_action.get("actionDate") or None
                )
                amendment["latest_action_time"] = (
                    latest_action.get("actionTime") or None
                )
                amendment["latest_action"] = latest_action.get("text") or None

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

            update_date = amendment.get("updateDate")
            amendment["updateDate"] = update_date[:10] if update_date else None

            transformed_data.append(CongressAmendmentsData(**amendment))

        return transformed_data
