"""FMP ETF Info fetcher."""

import concurrent.futures
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pydantic import Field


class FMPEtfInfoQueryParams(EtfInfoQueryParams):
    """FMP ETF Countries Query Params"""


class FMPEtfInfoData(EtfInfoData):
    """FMP ETF Countries Data."""

    __alias_dict__ = {
        "inception_date": "inceptionDate",
    }

    issuer: Optional[str] = Field(
        description="The issuer of the ETF.", alias="etfCompany", default=None
    )
    asset_class: Optional[str] = Field(
        description="The asset class of the ETF.", alias="assetClass", default=None
    )
    currency: Optional[str] = Field(
        description="The currency of the ETF.", alias="navCurrency", default=None
    )
    country: Optional[str] = Field(
        description="The country where the ETF is domiciled.",
        alias="domicile",
        default=None,
    )
    cusip: Optional[str] = Field(
        description="The CUSIP number of the ETF.", default=None
    )
    isin: Optional[str] = Field(description="The ISIN number of the ETF.", default=None)
    holdings_count: Optional[int] = Field(
        description="The number of holdings of the ETF.", default=None
    )
    nav: Optional[float] = Field(description="The NAV of the ETF.", default=None)
    aum: Optional[int] = Field(description="The AUM of the ETF.", default=None)
    expense_ratio: Optional[float] = Field(
        description="The expense ratio of the ETF.", default=None
    )
    avg_volume: Optional[float] = Field(
        description="The average daily volume of the ETF.", default=None
    )
    sectors: Optional[List[Dict]] = Field(
        description="The sector weightings of the ETF holdings.",
        alias="sectorsList",
        default=None,
    )
    website: Optional[str] = Field(description="The website of the ETF.", default=None)
    description: Optional[str] = Field(
        description="The description of the ETF.", default=None
    )


class FMPEtfInfoFetcher(
    Fetcher[
        FMPEtfInfoQueryParams,
        List[FMPEtfInfoData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfInfoQueryParams:
        """Transform the query."""
        return FMPEtfInfoQueryParams(**params)

    @staticmethod
    def get_info(symbol: str, api_key: str) -> Dict:
        """Return the raw data from the FMP endpoint."""
        data = {}
        url = f"https://financialmodelingprep.com/api/v4/etf-info?symbol={symbol}&apikey={api_key}"
        r = make_request(url)
        if len(r.json()) > 0:
            data = r.json()

        return data

    @staticmethod
    def extract_data(
        query: FMPEtfInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data for one or many symbols."""

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        results = []

        def get_one(symbol):
            result = FMPEtfInfoFetcher.get_info(symbol, api_key)  # type: ignore
            if result != {}:
                results.extend(result)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_one, symbols)

        return results

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPEtfInfoData]:
        """Return the transformed data."""
        return [FMPEtfInfoData(**d) for d in data]
