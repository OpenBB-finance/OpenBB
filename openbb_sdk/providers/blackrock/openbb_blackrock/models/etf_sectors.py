"""Blackrock ETF Sectors fetcher."""

import concurrent.futures
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_sectors import (
    EtfSectorsData,
    EtfSectorsQueryParams,
)
from pydantic import Field

from openbb_blackrock.utils.helpers import COUNTRIES, extract_from_holdings


class BlackrockEtfSectorsQueryParams(EtfSectorsQueryParams):
    """Blackrock ETF Sectors Query Params"""

    country: Optional[COUNTRIES] = Field(
        description="The country the ETF is registered in.  Symbol suffix with `.TO` can be used as a proxy for Canada.",
        default="america",
    )
    date: Optional[str] = Field(description="The as-of date for the data.")


class BlackrockEtfSectorsData(EtfSectorsData):
    """Blackrock ETF Sectors Data."""

    class Config:
        fields = {
            "energy": "Energy",
            "materials": "Basic Materials",
            "industrials": "Industrials",
            "consumer_cyclical": "Consumer Discretionary",
            "consumer_defensive": "Consumer Staples",
            "financial_services": "Financials",
            "technology": "Information Technology",
            "health_care": "Healthcare",
            "communication_services": "Communication",
            "utilities": "Utilities",
            "real_estate": "Real Estate",
        }

    cash_or_derivatives: Optional[float] = Field(
        description="Cash and/or derivatives.", alias="Cash and/or Derivatives"
    )


class BlackrockEtfSectorsFetcher(
    Fetcher[
        BlackrockEtfSectorsQueryParams,
        List[BlackrockEtfSectorsData],
    ]
):
    """Transform the query, extract and transform the data from the Blackrock endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BlackrockEtfSectorsQueryParams:
        """Transform the query."""
        return BlackrockEtfSectorsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlackrockEtfSectorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Blackrock endpoint."""

        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        results = {}

        def get_one(symbol):
            data = {}
            data = extract_from_holdings(
                symbol,
                to_extract="sector",
                country=query.country,  # type: ignore
                date=query.date,  # type: ignore
            )
            if data != {}:
                results.update({symbol: data})

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_one, symbols)

        return (
            pd.DataFrame(results)
            .transpose()
            .reset_index()
            .rename(columns={"index": "symbol"})
            .to_dict("records")
        )

    @staticmethod
    def transform_data(data: List[Dict]) -> List[BlackrockEtfSectorsData]:
        """Return the transformed data."""
        return [BlackrockEtfSectorsData(**d) for d in data]
