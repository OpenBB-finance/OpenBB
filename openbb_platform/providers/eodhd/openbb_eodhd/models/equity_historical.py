from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import Field
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.utils.helpers import make_request

class EODHDEquityHistoricalQueryParams(QueryParams):
    """EODHD Equity Historical Query Parameters."""
    symbol: str = Field(description="The ticker symbol to fetch data for.")
    start_date: Optional[date] = Field(default=None, description="Start date of the data.")
    end_date: Optional[date] = Field(default=None, description="End date of the data.")
    interval: str = Field(default="d", description="Interval: d (daily), w (weekly), m (monthly).")

class EODHDEquityHistoricalData(Data):
    """EODHD Equity Historical Data Model."""
    date: date
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float = Field(alias="adjusted_close")
    volume: int

class EODHDEquityHistoricalFetcher(Fetcher[EODHDEquityHistoricalQueryParams, List[EODHDEquityHistoricalData]]):
    """EODHD Equity Historical Fetcher."""
    
    @staticmethod
    def transform_query(query: EODHDEquityHistoricalQueryParams, extra_params: dict) -> Dict[str, Any]:
        return {**query.model_dump(), **extra_params}

    async def fetch(
        self,
        query: EODHDEquityHistoricalQueryParams,
        credentials: Dict[str, Any],
    ) -> List[EODHDEquityHistoricalData]:
        """Fetch historical equity candles from EODHD API."""
        api_key = credentials.get("api_key")
        if not api_key:
            raise ValueError("EODHD API key is required. Please set 'api_key' in your credentials.")

        symbol = query.symbol.upper()
        url = f"https://eodhd.com/api/eod/{symbol}"
        
        params = {
            "api_token": api_key,
            "fmt": "json",
            "period": query.interval,
        }
        
        if query.start_date:
            params["from"] = query.start_date.strftime("%Y-%m-%d")
        if query.end_date:
            params["to"] = query.end_date.strftime("%Y-%m-%d")

        # FIX: Yahan se await hata diya aur .json() se data extract kiya
        response = make_request(url, params=params)
        response_data = response.json()
        
        if not isinstance(response_data, list):
            raise ValueError(f"Failed to fetch data from EODHD: {response_data}")
            
        return self.extract_data(response_data, query)

    @staticmethod
    def extract_data(response_data: List[Dict[str, Any]], query: EODHDEquityHistoricalQueryParams) -> List[EODHDEquityHistoricalData]:
        return [EODHDEquityHistoricalData(**item) for item in response_data]