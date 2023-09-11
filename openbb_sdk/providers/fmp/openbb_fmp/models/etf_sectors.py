"""FMP ETF Sectors fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_sectors import (
    EtfSectorsData,
    EtfSectorsQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pydantic import Field


class FMPEtfSectorsQueryParams(EtfSectorsQueryParams):
    """FMP ETF Info Query Params"""


class FMPEtfSectorsData(EtfSectorsData):
    """FMP ETF Info Data."""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")
    energy: Optional[float] = Field(description="Energy Sector Weight.", alias="Energy")
    materials: Optional[float] = Field(
        description="Materials Sector Weight.", alias="Basic Materials"
    )
    industrials: Optional[float] = Field(
        description="Industrials Sector Weight.", alias="Industrials"
    )
    consumer_cyclical: Optional[float] = Field(
        description="Consumer Cyclical Sector Weight.", alias="Consumer Cyclical"
    )
    consumer_defensive: Optional[float] = Field(
        description="Consumer Defensive Sector Weight.", alias="Consumer Defensive"
    )
    financial_services: Optional[float] = Field(
        description="Financial Services Sector Weight.", alias="Financial Services"
    )
    technology: Optional[float] = Field(
        description="Technology Sector Weight.", alias="Technology"
    )
    health_care: Optional[float] = Field(
        description="Health Care Sector Weight.", alias="Healthcare"
    )
    communication_services: Optional[float] = Field(
        description="Communication Services Sector Weight.",
        alias="Communication Services",
    )
    utilities: Optional[float] = Field(
        description="Utilities Sector Weight.", alias="Utilities"
    )
    real_estate: Optional[float] = Field(
        description="Real Estate Sector Weight.", alias="Real Estate"
    )
    other: Optional[float] = Field(description="Other Sector Weight.", alias="Other")


class FMPEtfSectorsFetcher(
    Fetcher[
        FMPEtfSectorsQueryParams,
        List[FMPEtfSectorsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfSectorsQueryParams:
        """Transform the query."""
        return FMPEtfSectorsQueryParams(**params)

    @staticmethod
    def get_sectors(symbol: str, api_key: str) -> Dict:
        """Get sectors."""
        url = f"https://financialmodelingprep.com/api/v3/etf-sector-weightings/{symbol}?apikey={api_key}"
        r = make_request(url)
        data = {}
        if len(r.json()) > 0:
            df = pd.DataFrame(r.json()).set_index("sector")
            for i in df.index:
                data.update({i: df.loc[i]["weightPercentage"].replace("%", "")})
        return data

    @staticmethod
    def extract_data(
        query: FMPEtfSectorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        results = {}
        for symbol in symbols:
            result = FMPEtfSectorsFetcher.get_sectors(symbol, api_key)
            if result != {}:
                results.update({symbol: result})

        return (
            pd.DataFrame(results)
            .transpose()
            .reset_index()
            .rename(columns={"index": "symbol"})
            .to_dict("records")
        )

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPEtfSectorsData]:
        """Return the transformed data."""
        return [FMPEtfSectorsData(**d) for d in data]
