"""FMP ETF Holdings Model."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field


class FMPEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """FMP ETF Holdings Query.

    Source: https://site.financialmodelingprep.com/developer/docs#Historical-ETF-Holdings
    """

    date: Optional[Union[str, dateType]] = Field(
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " This needs to be _exactly_ the date of the filing."
        + " Use the holdings_date command/endpoint to find available filing dates for the ETF.",
        default=None,
    )

    cik: Optional[str] = Field(
        description=QUERY_DESCRIPTIONS.get("cik", "")
        + "The CIK of the filing entity. Overrides symbol.",
        default=None,
    )


class FMPEtfHoldingsData(EtfHoldingsData):
    """FMP ETF Holdings Data."""

    lei: Optional[str] = Field(description="The LEI of the holding.", default=None)
    title: Optional[str] = Field(description="The title of the holding.", default=None)
    cusip: Optional[str] = Field(description="The CUSIP of the holding.", default=None)
    isin: Optional[str] = Field(description="The ISIN of the holding.", default=None)
    balance: Optional[float] = Field(
        description="The balance of the holding.", default=None
    )
    units: Optional[Union[float, str]] = Field(
        description="The units of the holding.", default=None
    )
    currency: Optional[str] = Field(
        description="The currency of the holding.", alias="cur_cd", default=None
    )
    value: Optional[float] = Field(
        description="The value of the holding in USD.", alias="valUsd", default=None
    )
    weight: Optional[float] = Field(
        description="The weight of the holding in ETF in %.",
        alias="pctVal",
        default=None,
    )
    payoff_profile: Optional[str] = Field(
        description="The payoff profile of the holding.",
        alias="payoffProfile",
        default=None,
    )
    asset_category: Optional[str] = Field(
        description="The asset category of the holding.", alias="assetCat", default=None
    )
    issuer_category: Optional[str] = Field(
        description="The issuer category of the holding.",
        alias="issuerCat",
        default=None,
    )
    country: Optional[str] = Field(
        description="The country of the holding.", alias="invCountry", default=None
    )
    is_restricted: Optional[str] = Field(
        description="Whether the holding is restricted.",
        alias="isRestrictedSec",
        default=None,
    )
    fair_value_level: Optional[int] = Field(
        description="The fair value level of the holding.",
        alias="fairValLevel",
        default=None,
    )
    is_cash_collateral: Optional[str] = Field(
        description="Whether the holding is cash collateral.",
        alias="isCashCollateral",
        default=None,
    )
    is_non_cash_collateral: Optional[str] = Field(
        description="Whether the holding is non-cash collateral.",
        alias="isNonCashCollateral",
        default=None,
    )
    is_loan_by_fund: Optional[str] = Field(
        description="Whether the holding is loan by fund.",
        alias="isLoanByFund",
        default=None,
    )
    cik: Optional[str] = Field(description="The CIK of the filing.", default=None)
    acceptance_datetime: Optional[str] = Field(
        description="The acceptance datetime of the filing.",
        alias="acceptanceTime",
        default=None,
    )


class FMPEtfHoldingsFetcher(
    Fetcher[
        FMPEtfHoldingsQueryParams,
        List[FMPEtfHoldingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfHoldingsQueryParams:
        """Transform the query."""
        return FMPEtfHoldingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            version=4, endpoint="etf-holdings", api_key=api_key, query=query
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEtfHoldingsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPEtfHoldingsData]:
        """Return the transformed data."""
        return [FMPEtfHoldingsData.model_validate(d) for d in data]
