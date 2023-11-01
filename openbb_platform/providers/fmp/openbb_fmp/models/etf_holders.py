"""FMP ETF Holders fetcher."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional, Union

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_holders import (
    EtfHoldersData,
    EtfHoldersQueryParams,
)
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class FMPEtfHoldersQueryParams(EtfHoldersQueryParams):
    """FMP ETF Holders query.

    Source: https://site.financialmodelingprep.com/developer/docs/etf-holders-api
    """


class FMPEtfHoldersData(EtfHoldersData):
    """FMP ETF Holders Data."""

    symbol: Optional[str] = Field(
        description=DATA_DESCRIPTIONS.get("symbol", "") + " Institutional holder.",
        alias="asset",
        default=None,
    )
    name: Optional[str] = Field(description="The name of the holder.", default=None)
    cusip: Optional[str] = Field(description="The CUSIP of the holding.", default=None)
    isin: Optional[str] = Field(description="The ISIN of the holding.", default=None)
    shares_number: Optional[float] = Field(
        description="The number of shares the holder owns.", default=None
    )
    weight: Optional[float] = Field(
        description="The weight of the holder in the ETF in %.",
        alias="weightPercentage",
        default=None,
    )
    value: Optional[float] = Field(
        description="The value of the holding in USD.",
        alias="marketValue",
        default=None,
    )
    payoff_profile: Optional[str] = Field(
        description="The payoff profile of the holding.",
        alias="payoffProfile",
        default=None,
    )
    updated: Optional[Union[str, dateType]] = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + " The date when the data has been updated.",
        default=None,
    )


class FMPEtfHoldersFetcher(
    Fetcher[
        FMPEtfHoldersQueryParams,
        List[FMPEtfHoldersData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfHoldersQueryParams:
        """Transform the query."""
        return FMPEtfHoldersQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPEtfHoldersQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            version=3,
            endpoint=f"etf-holder/{query.symbol}",
            api_key=api_key,
            exclude=["symbol"],
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEtfHoldersQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPEtfHoldersData]:
        """Return the transformed data."""
        return [FMPEtfHoldersData.model_validate(d) for d in data]
