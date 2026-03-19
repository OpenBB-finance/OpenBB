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

import pandas as pd
from datetime import datetime
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.utils.errors import EmptyDataError

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
        
        # In a production environment, we will dynamically find the latest date.
        # For this proof-of-concept, we will hardcode the date format the FFIEC expects.
        target_date = "20241231" # December 31, 2024
        rssd_id = query.rssd_id
        
        # This is the hidden backend URL the FFIEC website uses to generate CSVs
        url = f"https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportCSV?rssd={rssd_id}&dt={target_date}&b=Y15"
        
        try:
            # We use pandas to grab the CSV directly from the URL
            df = pd.read_csv(url)
            return df
        except Exception as e:
            raise EmptyDataError(f"Could not retrieve FFIEC data for RSSD {rssd_id}. Error: {e}")

    @staticmethod
    def transform_data(query: FfiecRiskQueryParams, data: pd.DataFrame, **kwargs) -> list[FfiecRiskData]:
        """Translates the messy government dataframe into the strict OpenBB model."""
        
        if data.empty:
            raise EmptyDataError("The FFIEC returned an empty report.")

        # 1. Map the MDRM dictionary codes to English
        # We start with just two columns to prove the pipeline works
        column_mapping = {
            "ID_RSSD": "rssd_id",
            "As of Date": "report_date",
            "RISKC490": "total_assets", # Example mapping
            "RISK2170": "tier_1_capital" # Example mapping
        }
        
        # Rename the columns in the dataframe
        data.rename(columns=column_mapping, inplace=True)
        
        # 2. Filter out all the ugly RISK columns we haven't mapped yet
        mapped_columns = list(column_mapping.values())
        
        # Only keep the columns that actually exist in the dataframe (prevents KeyError)
        valid_columns = [col for col in mapped_columns if col in data.columns]
        clean_df = data[valid_columns]
        
        # 3. Convert dates to standard format
        if "report_date" in clean_df.columns:
            clean_df["report_date"] = pd.to_datetime(clean_df["report_date"]).dt.date

        # 4. Convert the pandas dataframe rows into a list of our Pydantic Data models
        results = []
        for _, row in clean_df.iterrows():
            # Convert row to dictionary and drop NaN values
            row_dict = row.dropna().to_dict()
            
            # Pydantic will automatically validate this dictionary against our FfiecRiskData model
            results.append(FfiecRiskData(**row_dict))
            
        return results
