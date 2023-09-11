"""TMX ETF Sectors fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_sectors import (
    EtfSectorsData,
    EtfSectorsQueryParams,
)
from pydantic import Field

from openbb_tmx.utils.helpers import get_all_etfs


class TmxEtfSectorsQueryParams(EtfSectorsQueryParams):
    """TMX ETF Info Query Params"""


class TmxEtfSectorsData(EtfSectorsData):
    """TMX ETF Info Data."""

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


class TmxEtfSectorsFetcher(
    Fetcher[
        TmxEtfSectorsQueryParams,
        List[TmxEtfSectorsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEtfSectorsQueryParams:
        """Transform the query."""
        return TmxEtfSectorsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxEtfSectorsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )

        _data = get_all_etfs()
        data = {}
        results = {}
        for symbol in symbols:
            if ".TO" in symbol:
                symbol = symbol.replace(".TO", "")
            _target = _data[_data["symbol"] == symbol]["sectors"]
            target = pd.DataFrame()
            if len(_target) > 0:
                target = pd.DataFrame.from_records(_target.iloc[0]).rename(
                    columns={"name": "sector", "percent": "weight"}
                )
                if not target.empty:
                    target = target.set_index("sector")
                for i in target.index:
                    data.update({i: target.loc[i]["weight"]})
                if data != {}:
                    results.update({symbol: data})

        return (
            pd.DataFrame(results)
            .transpose()
            .reset_index()
            .rename(columns={"index": "symbol"})
            .to_dict("records")
        )

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxEtfSectorsData]:
        """Return the transformed data."""
        return [TmxEtfSectorsData(**d) for d in data]
