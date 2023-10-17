"""Invesco ETF Holdings fetcher."""

from datetime import date as dateType
from io import StringIO
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from dateutil import parser
from openbb_invesco.utils.helpers import (
    COUNTRIES,
    America,
    invesco_america_etf_holdings,
)
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from pydantic import Field, field_validator


class InvescoEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """Invesco ETF Holdings query.

    Source: https://www.invesco.com/
    """

    country: Optional[COUNTRIES] = Field(
        description="The country the ETF is registered in.", default="america"
    )


class InvescoEtfHoldingsData(EtfHoldingsData):
    """Invesco ETF Holdings Data."""

    symbol: Optional[str] = Field(
        description="The ticker symbol of the asset.",
        default=None,
        alias="Holding Ticker",
    )
    security_identifier: Optional[Union[str, int]] = Field(
        description="The unique security identifier of the asset.",
        default=None,
        alias="Security Identifier",
    )
    identifier: Optional[str] = Field(
        description="The asset class identifier.", default=None, alias="Identifier"
    )
    name: Optional[str] = Field(
        description="The name of the asset.", default=None, alias="Name"
    )
    weight: Optional[float] = Field(
        description="The weight of the asset in the portfolio.",
        default=None,
        alias="Weight",
    )
    shares_or_contracts: Optional[float] = Field(
        description="The number of shares or contracts of the asset held.",
        alias="Shares",
        default=None,
    )
    market_value: Optional[float] = Field(
        description="The market value of the holding.",
        default=None,
        alias="MarketValue",
    )
    rating: Optional[str] = Field(description="The rating of the bond.", default=None)
    coupon_rate: Optional[float] = Field(
        description="The coupon rate of the bond.", default=None, alias="Coupon Rate"
    )
    contract_expiry_date: Optional[Union[dateType, str]] = Field(
        description="The expiration date of the derivatives contract.",
        default=None,
        alias="Contract Expiry Date",
    )
    maturity_date: Optional[Union[dateType, str]] = Field(
        description="The maturity date of the bond.",
        default=None,
        alias="Maturity Date",
    )
    effective_date: Optional[Union[dateType, str]] = Field(
        description="The effective date of the bond holding.",
        default=None,
        alias="Effective Date",
    )
    next_call_date: Optional[Union[dateType, str]] = Field(
        description="The next call date of the bond.",
        default=None,
        alias="Next Call Date",
    )
    sector: Optional[str] = Field(
        description="The sector of the asset.", default=None, alias="Sector"
    )
    share_class: Optional[str] = Field(
        description="The share class of the asset.",
        default=None,
        alias="Class of Shares",
    )
    fund_ticker: Optional[str] = Field(
        description="The ticker symbol of the Fund.", default=None, alias="Fund Ticker"
    )
    holdings_date: Optional[dateType] = Field(
        description="The date the asset was added to the portfolio.",
        default=None,
        alias="Date",
    )

    @field_validator("holdings_date")
    def holdings_date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        return parser.parse(v.strftime("%Y-%m-%d")).date()


class InvescoEtfHoldingsFetcher(
    Fetcher[
        InvescoEtfHoldingsQueryParams,
        List[InvescoEtfHoldingsData],
    ]
):
    """Transform the query, extract and transform the data from the Invesco endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> InvescoEtfHoldingsQueryParams:
        """Transform the query."""
        return InvescoEtfHoldingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: InvescoEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Invesco endpoint."""

        holdings = pd.DataFrame()
        query.symbol = query.symbol.upper()

        if query.country == "america":
            etfs = America.get_all_etfs()
            if query.symbol not in etfs["Ticker"].to_list():
                raise ValueError(
                    f"Symbol is not supported, or not a valid Invesco ETF -> {query.symbol}"
                )

            url = (
                f"https://www.invesco.com/us/financial-products/etfs/holdings/main/holdings/"
                f"0?audienceType=Investor&action=download&ticker={query.symbol}"
            )
            r = invesco_america_etf_holdings.get(url, timeout=5)

        if r.status_code != 200:  # type: ignore
            raise RuntimeError("HTTP Error -> " + str(r.status_code))  # type: ignore

        holdings = pd.read_csv(StringIO(r.text))  # type: ignore
        holdings.columns = [c.strip() for c in holdings.columns]
        holdings = holdings.rename(
            columns={
                "$ Value": "MarketValue",
                "Shares/Par Value": "Shares",
                "Shares/Contracts": "Shares",
                "PositionDate": "Date",
                "PercentageOfFund": "Weight",
                "Next_Call_Date": "Next Call Date",
                "MaturityDate": "Maturity Date",
                "CouponRate": "Coupon Rate",
            }
        )

        holdings["Date"] = pd.to_datetime(holdings["Date"], yearfirst=True).dt.strftime(
            "%Y-%m-%d"
        )

        if "Contract Expiry Date" in holdings.columns:
            holdings["Contract Expiry Date"] = (
                pd.to_datetime(holdings["Contract Expiry Date"], yearfirst=True)
                .dt.strftime("%Y-%m-%d")
                .astype(str)
                .str.replace("nan", "")
            )
        if "Next Call Date" in holdings.columns:
            holdings["Next Call Date"] = (
                pd.to_datetime(holdings["Next Call Date"], yearfirst=True)
                .dt.strftime("%Y-%m-%d")
                .astype(str)
                .str.replace("nan", "")
            )
        if "Effective Date" in holdings.columns:
            holdings["Effective Date"] = (
                pd.to_datetime(holdings["Effective Date"], yearfirst=True)
                .dt.strftime("%Y-%m-%d")
                .astype(str)
                .str.replace("nan", "")
            )
        if "Maturity Date" in holdings.columns:
            holdings["Maturity Date"] = (
                pd.to_datetime(holdings["Maturity Date"], yearfirst=True)
                .dt.strftime("%Y-%m-%d")
                .astype(str)
                .str.replace("nan", "")
            )
        if "Identifier" in holdings.columns:
            holdings["Identifier"] = (
                holdings["Identifier"].astype(str).replace("nan", "")
            )
        holdings["Shares"] = holdings["Shares"].str.replace(",", "").astype(float)
        holdings["MarketValue"] = (
            holdings["MarketValue"].astype(str).str.replace(",", "").astype(float)
        )
        holdings["Security Identifier"] = holdings["Security Identifier"].astype(str)
        if "Holding Ticker" in holdings.columns:
            holdings["Holding Ticker"] = (
                holdings["Holding Ticker"].astype(str).replace("nan", "")
            )

        return holdings.to_dict("records")

    @staticmethod
    def transform_data(
        data: List[Dict],
        **kwargs: Any,
    ) -> List[InvescoEtfHoldingsData]:
        """Transform the data."""
        return [InvescoEtfHoldingsData.model_validate(d) for d in data]
