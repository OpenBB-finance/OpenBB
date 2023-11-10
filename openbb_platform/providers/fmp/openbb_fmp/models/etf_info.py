"""FMP ETF Info fetcher."""

import concurrent.futures
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_info import EtfInfoData, EtfInfoQueryParams
from pydantic import Field


class FMPEtfInfoQueryParams(EtfInfoQueryParams):
    """FMP ETF Info Query Params."""


class FMPEtfInfoData(EtfInfoData):
    """FMP ETF Info Data."""

    domicile: Optional[str] = Field(
        default=None,
        description="Domicile of the ETF.",
    )
    issuer: Optional[str] = Field(
        default=None,
        alias="etfCompany",
        description="The issuer of the ETF.",
    )
    asset_class: Optional[str] = Field(
        default=None,
        alias="assetClass",
        description="Asset class of the ETF.",
    )
    isin: Optional[str] = Field(
        default=None,
        description="ISIN of the ETF.",
    )
    cusip: Optional[str] = Field(
        default=None,
        description="CUSIP of the ETF.",
    )
    holdings_count: Optional[int] = Field(
        default=None,
        alias="holdingsCount",
        description="Number of holdings in the ETF.",
    )
    aum: Optional[float] = Field(
        default=None,
        description="Assets under management.",
    )
    nav: Optional[float] = Field(
        default=None,
        description="Net asset value of the ETF.",
    )
    nav_currency: Optional[str] = Field(
        default=None,
        alias="navCurrency",
        description="Currency of the ETF's net asset value.",
    )
    expense_ratio: Optional[float] = Field(
        default=None,
        alias="expenseRatio",
        description="Expense ratio of the ETF.",
    )
    avg_volume: Optional[float] = Field(
        default=None,
        alias="avgVolume",
        description="Average trading volume of the ETF.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the ETF.",
    )
    website: Optional[str] = Field(
        default=None,
        description="Website link of the ETF.",
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
    def extract_data(
        query: FMPEtfInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )

        results = []

        def get_one(symbol):
            url = create_url(
                version=4,
                endpoint="etf-info",
                query={"symbol": symbol},
                api_key=api_key,
            )
            result = get_data_many(url=url, **kwargs)
            if result != {}:
                results.extend(result)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_one, symbols)

        return results

    @staticmethod
    def transform_data(
        query: FMPEtfInfoQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEtfInfoData]:
        """Return the transformed data."""
        # remove "sectorList" key from data. it's handled by the sectors
        for d in data:
            d.pop("sectorsList", None)
        return [FMPEtfInfoData.model_validate(d) for d in data]
