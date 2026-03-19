"""FFIEC Bank Financial Data Models."""

import pandas as pd
from datetime import date as dateType
from io import StringIO
from typing import Optional

from pydantic import Field
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import make_request

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


class FfiecRiskFetcher(
    Fetcher[
        FfiecRiskQueryParams,
        list[FfiecRiskData],
    ]
):
    """Fetcher for the FFIEC FR Y-15 Systemic Risk Report."""

    @staticmethod
    def extract_data(query: FfiecRiskQueryParams, credentials: dict, **kwargs) -> pd.DataFrame:
        """Pings the FFIEC server and downloads the CSV."""
        
        target_date = "20241231"
        rssd_id = query.rssd_id
        
        url = f"https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportCSV?rssd={rssd_id}&dt={target_date}&b=Y15"
        
        # Heavy disguise headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": f"https://www.ffiec.gov/npw/Institution/Profile/{rssd_id}?dt={target_date}",
            "Connection": "keep-alive"
        }
        
        try:
            response = make_request(url, headers=headers)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            return df
        except Exception as e:
            raise EmptyDataError(f"Could not retrieve FFIEC data for RSSD {rssd_id}. Error: {e}")

    @staticmethod
    def transform_data(query: FfiecRiskQueryParams, data: pd.DataFrame, **kwargs) -> list[FfiecRiskData]:
        """Translates the messy government dataframe into the strict OpenBB model."""
        
        if data.empty:
            raise EmptyDataError("The FFIEC returned an empty report.")

        column_mapping = {
            "ID_RSSD": "rssd_id",
            "As of Date": "report_date",
            "RISKC490": "total_assets", 
            "RISK2170": "tier_1_capital" 
        }
        
        data.rename(columns=column_mapping, inplace=True)
        mapped_columns = list(column_mapping.values())
        valid_columns = [col for col in mapped_columns if col in data.columns]
        
        clean_df = data[valid_columns].copy()
        
        if "report_date" in clean_df.columns:
            clean_df["report_date"] = pd.to_datetime(clean_df["report_date"]).dt.date
            
        if "rssd_id" in clean_df.columns:
            clean_df["rssd_id"] = clean_df["rssd_id"].astype(float).astype(int).astype(str)

        results = []
        for _, row in clean_df.iterrows():
            row_dict = row.dropna().to_dict()
            results.append(FfiecRiskData(**row_dict))
            
        return results