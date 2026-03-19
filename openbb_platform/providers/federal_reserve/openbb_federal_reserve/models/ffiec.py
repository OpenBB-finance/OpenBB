"""FFIEC Bank Financial Data Models."""

from datetime import date as dateType
from typing import Optional
from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams

class FfiecRiskQueryParams(QueryParams):
    """Query parameters for FFIEC FR Y-15 Report."""
    
    rssd_id: str = Field(
        description="The Federal Reserve RSSD ID of the institution (e.g., '1039502' for JPMorgan)."
    )
    date: Optional[dateType] = Field(
        default=None, 
        description="The specific report date. If left blank, gets the latest."
    )

class FfiecRiskData(Data):
    """Data schema for FFIEC FR Y-15 Report."""
    
    rssd_id: str = Field(description="The Federal Reserve RSSD ID.")
    report_date: dateType = Field(description="The date of the report.")
    
    total_assets: Optional[float] = Field(
        default=None, 
        description="Total Consolidated Assets."
    )
    tier_1_capital: Optional[float] = Field(
        default=None, 
        description="Tier 1 Capital."
    )
