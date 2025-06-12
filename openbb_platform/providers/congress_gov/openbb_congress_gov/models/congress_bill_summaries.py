"""Congress Bill Summaries Model."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from pydantic import Field


class CongressBillSummariesQueryParams(QueryParams):
    """Congress Bill Summaries Query Parameters."""
    
    congress: int = Field(
        description="The congress session number (e.g. 117, 118)."
    )
    bill_type: str = Field(
        description="The bill type (e.g. 'hr', 's', 'hjres', 'sjres')."
    )
    bill_number: str = Field(
        description="The bill number."
    )
    limit: Optional[int] = Field(
        default=200,
        description=QUERY_DESCRIPTIONS.get("limit", "") + " Max is 250."
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of results to skip."
    )


class CongressBillSummariesData(Data):
    """Congress Bill Summaries Data."""
    
    action_date: Optional[dateType] = Field(
        default=None,
        description="Date of the summary action."
    )
    action_desc: Optional[str] = Field(
        default=None,
        description="Description of the summary action."
    )
    text: Optional[str] = Field(
        default=None,
        description="The summary text content."
    )
    update_date: Optional[dateType] = Field(
        default=None,
        description="Date the summary was last updated."
    )
    version_code: Optional[str] = Field(
        default=None,
        description="Version code of the summary."
    )


class CongressBillSummariesFetcher(
    Fetcher[
        CongressBillSummariesQueryParams,
        List[CongressBillSummariesData],
    ]
):
    """Extract and transform data from the Congress API."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> CongressBillSummariesQueryParams:
        """Transform the query params."""
        return CongressBillSummariesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressBillSummariesQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data from the Congress API."""
        api_key = credentials.get("api_key") if credentials else ""
        
        url = (
            f"https://api.congress.gov/v3/bill/{query.congress}/"
            f"{query.bill_type}/{query.bill_number}/summaries"
        )
        
        params = {
            "api_key": api_key,
            "format": "json",
            "offset": query.offset,
            "limit": query.limit
        }
        
        response = await amake_request(url, params=params, **kwargs)
        
        if not response or not response.get("summaries"):
            raise EmptyDataError()
        
        return response["summaries"]

    @staticmethod
    def transform_data(
        query: CongressBillSummariesQueryParams,
        data: List[Dict],
        **kwargs: Any
    ) -> List[CongressBillSummariesData]:
        """Transform raw data into CongressBillSummariesData models."""
        transformed_data = []
        
        for summary in data:
            transformed_summary = CongressBillSummariesData(
                action_date=summary.get("actionDate"),
                action_desc=summary.get("actionDesc"),
                text=summary.get("text"),
                update_date=summary.get("updateDate"),
                version_code=summary.get("versionCode")
            )
            transformed_data.append(transformed_summary)
        
        return transformed_data 