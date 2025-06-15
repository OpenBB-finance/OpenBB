"""Congress Bills Model."""

from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class CongressBillsQueryParams(QueryParams):
    """Congress Bills Query Parameters."""

    __json_schema_extra__ = {
        "format": {
            "x-widget_config": {
                "exclude": True,
            },
        },
        "offset": {
            "x-widget_config": {
                "exclude": True,
            },
        },
    }

    format: Literal["json", "xml"] = Field(
        default="json", description="The data format. Value can be xml or json."
    )
    limit: int = Field(
        default=100,
        description="The number of records returned. The maximum limit is 250.",
    )
    offset: Optional[int] = Field(
        default=None, description="The starting record returned. 0 is the first record."
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )
    sort: Literal["asc", "desc"] = Field(
        default="asc", description="Sort by update date in Congress.gov."
    )

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Validate limit parameter."""
        if v and v > 250:
            raise ValueError("Limit cannot exceed 250")
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate format parameter."""
        if v and v not in ["json", "xml"]:
            raise ValueError("Format must be either 'json' or 'xml'")
        return v

    @field_validator("sort")
    @classmethod
    def validate_sort(cls, v: str) -> str:
        """Validate sort parameter."""
        if v and v not in ["asc", "desc"]:
            raise ValueError("Sort must be either 'asc' or 'desc'")
        return v


class LatestAction(Data):
    """Latest Action Data for Congress Bills."""

    actionDate: Optional[dateType] = Field(
        default=None, description="Date of the latest action on the bill."
    )
    text: Optional[str] = Field(
        default=None, description="Description of the latest action on the bill."
    )


class CongressBillsData(Data):
    """Congress Bills Data."""

    congress: int = Field(description="The congress session number.")
    latestAction: LatestAction = Field(
        description="Latest action information for the bill."
    )
    number: str = Field(description="The bill number.")
    origin_chamber: str = Field(description="The chamber where the bill originated.")
    origin_chamber_code: str = Field(
        description="The chamber code where the bill originated."
    )
    title: str = Field(description="The title of the bill.")
    type: str = Field(description="The type of bill (e.g., HR, S).")
    update_date: dateType = Field(description="The date the bill was last updated.")
    update_date_including_text: str = Field(
        description="The date and time the bill text was last updated."
    )
    url: str = Field(description="URL to the bill on congress.gov.")


class CongressBillsFetcher(
    Fetcher[
        CongressBillsQueryParams,
        List[CongressBillsData],
    ]
):
    """Transform the query, extract and transform the data from the Congress API."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CongressBillsQueryParams:
        """Transform the query params."""
        return CongressBillsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressBillsQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data from the Congress API."""
        api_key = credentials.get("congres_gov_api_key") if credentials else ""

        url = "https://api.congress.gov/v3/bill"

        params = {
            "api_key": api_key,
            "format": query.format,
            "limit": query.limit,
        }

        if query.offset is not None:
            params["offset"] = query.offset

        if query.start_date:
            params["fromDateTime"] = query.start_date.strftime("%Y-%m-%dT00:00:00Z")
        if query.end_date:
            params["toDateTime"] = query.end_date.strftime("%Y-%m-%dT00:00:00Z")

        params["sort"] = "updateDate+asc" if query.sort == "asc" else "updateDate+desc"

        response = await amake_request(url, params=params, **kwargs)

        if not response or not response.get("bills"):
            raise EmptyDataError()

        return response["bills"]

    @staticmethod
    def transform_data(
        query: CongressBillsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[CongressBillsData]:
        """Transform raw data into CongressBillsData models."""
        transformed_data = []

        for bill in data:
            latest_action = bill.get("latestAction", {})

            transformed_bill = CongressBillsData(
                congress=bill.get("congress"),
                latestAction=(
                    LatestAction(
                        actionDate=latest_action.get("actionDate"),
                        text=latest_action.get("text"),
                    )
                    if latest_action
                    else None
                ),
                number=bill.get("number"),
                origin_chamber=bill.get("originChamber"),
                origin_chamber_code=bill.get("originChamberCode"),
                title=bill.get("title"),
                type=bill.get("type"),
                update_date=bill.get("updateDate"),
                update_date_including_text=bill.get("updateDateIncludingText"),
                url=bill.get("url"),
            )
            transformed_data.append(transformed_bill)

        return transformed_data
