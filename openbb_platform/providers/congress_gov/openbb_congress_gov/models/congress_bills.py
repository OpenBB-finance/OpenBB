"""Congress Bills Model."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from pydantic import Field, field_validator


class CongressBillsQueryParams(QueryParams):
    """Congress Bills Query Parameters."""
    
    congress: Optional[int] = Field(
        default=None,
        description="Filter by congress number (e.g. 117, 118)."
    )
    bill_type: Optional[str] = Field(
        default=None,
        description="Filter by bill type (e.g. 'hr', 's', 'hjres', 'sjres')."
    )
    limit: Optional[int] = Field(
        default=100,
        description=QUERY_DESCRIPTIONS.get("limit", "") + " Max is 250."
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of results to skip."
    )
    from_date: Optional[dateType] = Field(
        default=None,
        description="Filter bills updated on or after this date."
    )
    to_date: Optional[dateType] = Field(
        default=None,
        description="Filter bills updated on or before this date."
    )
    sort: Optional[str] = Field(
        default="updateDate+desc",
        description="Sort order (updateDate+asc or updateDate+desc)."
    )

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Validate limit parameter."""
        if v and v > 250:
            raise ValueError("Limit cannot exceed 250")
        return v


class CongressBillsData(Data):
    """Congress Bills Data."""
    
    congress: Optional[int] = Field(
        default=None,
        description="The congress session number."
    )
    number: Optional[str] = Field(
        default=None,
        description="The bill number."
    )
    bill_type: Optional[str] = Field(
        default=None,
        description="The type of bill (e.g., HR, S)."
    )
    title: Optional[str] = Field(
        default=None,
        description="The title of the bill."
    )
    latest_action_date: Optional[dateType] = Field(
        default=None,
        description="Date of the latest action on the bill."
    )
    latest_action_text: Optional[str] = Field(
        default=None,
        description="Description of the latest action on the bill."
    )
    origin_chamber: Optional[str] = Field(
        default=None,
        description="The chamber where the bill originated."
    )
    origin_chamber_code: Optional[str] = Field(
        default=None,
        description="The chamber code where the bill originated."
    )
    update_date: Optional[dateType] = Field(
        default=None,
        description="The date the bill was last updated."
    )
    update_date_including_text: Optional[dateType] = Field(
        default=None,
        description="The date the bill text was last updated."
    )
    url: Optional[str] = Field(
        default=None,
        description="URL to the bill on congress.gov."
    )


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
        api_key = credentials.get("api_key") if credentials else ""
        
        if query.congress and query.bill_type:
            url = (
                f"https://api.congress.gov/v3/bill/"
                f"{query.congress}/{query.bill_type}"
            )
        else:
            url = "https://api.congress.gov/v3/bill"
        
        params = {
            "api_key": api_key,
            "format": "json",
            "offset": query.offset,
            "limit": query.limit,
            "sort": query.sort
        }
        
        if query.from_date:
            params["fromDateTime"] = f"{query.from_date}T00:00:00Z"
        if query.to_date:
            params["toDateTime"] = f"{query.to_date}T00:00:00Z"
        
        response = await amake_request(url, params=params, **kwargs)
        
        if not response or not response.get("bills"):
            raise EmptyDataError()
        
        return response["bills"]

    @staticmethod
    def transform_data(
        query: CongressBillsQueryParams,
        data: List[Dict],
        **kwargs: Any
    ) -> List[CongressBillsData]:
        """Transform raw data into CongressBillsData models."""
        transformed_data = []
        
        for bill in data:
            latest_action = bill.get("latestAction", {})
            
            transformed_bill = CongressBillsData(
                congress=bill.get("congress"),
                number=bill.get("number"),
                bill_type=bill.get("type"),
                title=bill.get("title"),
                latest_action_date=latest_action.get("actionDate"),
                latest_action_text=latest_action.get("text"),
                origin_chamber=bill.get("originChamber"),
                origin_chamber_code=bill.get("originChamberCode"),
                update_date=bill.get("updateDate"),
                update_date_including_text=bill.get("updateDateIncludingText"),
                url=bill.get("url")
            )
            transformed_data.append(transformed_bill)
        
        return transformed_data 