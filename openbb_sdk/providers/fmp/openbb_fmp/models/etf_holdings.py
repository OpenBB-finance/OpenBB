"""FMP ETF Holdings fetcher."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pydantic import Field


class FMPEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """FMP ETF Holdings query.

    Source: https://site.financialmodelingprep.com/developer/docs#Historical-ETF-Holdings
    """

    date: Optional[str | dateType] = Field(
        description="The as-of date for historical daily holdings.", default=""
    )


class FMPEtfHoldingsData(EtfHoldingsData):
    """FMP ETF Holdings Data."""

    symbol: Optional[str] = Field(description="The ticker symbol of the holding.")
    name: Optional[str] = Field(description="The name of the holding.")
    lei: Optional[str] = Field(description="The LEI of the company.")
    title: Optional[str] = Field(description="The title of the holding.")
    cusip: Optional[str] = Field(description="The CUSIP of the holding.")
    isin: Optional[str] = Field(description="The ISIN of the holding.")
    balance: Optional[float] = Field(description="The balance of the holding.")
    units: Optional[float | str] = Field(description="The units of the holding.")
    currency: Optional[str] = Field(
        description="The currency of the holding.", alias="cur_cd"
    )
    value: Optional[float] = Field(
        description="The value of the holding in USD.", alias="valUsd"
    )
    weight: Optional[float] = Field(
        description="The weight of the holding in ETF.", alias="pctVal"
    )
    payoffProfile: Optional[str] = Field(
        description="The payoff profile of the holding.", alias="payoffProfile"
    )
    asset_category: Optional[str] = Field(
        description="The asset category of the holding.", alias="assetCat"
    )
    issuer_category: Optional[str] = Field(
        description="The issuer category of the holding.", alias="issuerCat"
    )
    country: Optional[str] = Field(
        description="The country of the holding.", alias="invCountry"
    )
    is_restricted: Optional[str] = Field(
        description="Whether the holding is restricted.", alias="isRestrictedSec"
    )
    fair_value_level: Optional[int] = Field(
        description="The fair value level of the holding.", alias="fairValLevel"
    )
    is_cash_collateral: Optional[str] = Field(
        description="Whether the holding is cash collateral.", alias="isCashCollateral"
    )
    is_non_cash_collateral: Optional[str] = Field(
        description="Whether the holding is non-cash collateral.",
        alias="isNonCashCollateral",
    )
    is_loan_by_fund: Optional[str] = Field(
        description="Whether the holding is loan by fund.", alias="isLoanByFund"
    )


class FMPEtfHoldingsFetcher(
    Fetcher[
        FMPEtfHoldingsQueryParams,
        List[FMPEtfHoldingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def get_holdings(symbol, date, api_key) -> pd.DataFrame:
        BASE_URL = "https://financialmodelingprep.com/api/v4/etf-holdings/"

        if isinstance(date, dateType) and date is not None:
            date = datetime.strftime(date, "%Y-%m-%d")

        dates_url = BASE_URL + f"portfolio-date?symbol={symbol}&apikey={api_key}"

        r_dates = make_request(dates_url)

        if "Error Message" in r_dates.json():
            raise RuntimeError(r_dates.json()["Error Message"])

        if len(r_dates.json()) == 0:
            raise ValueError(
                f"Error with FMP request -> {symbol}, no results found or the ticker is not supported."
            )

        _dates = r_dates.json()
        dates = [_dates["date"] for _dates in _dates]
        if not date:
            date = dates[0]
        new_date: str = ""
        if date:
            # Check that the date is valid, or gets the nearest valid date.
            __dates = pd.Series(pd.to_datetime(dates))
            __date = pd.to_datetime(date)
            __nearest = pd.DataFrame(__dates - __date)
            __nearest_date = abs(__nearest[0].astype("int64")).idxmin()
            new_date = __dates[__nearest_date].strftime("%Y-%m-%d")

        new_date = new_date if new_date else date
        holdings_url = BASE_URL + f"?symbol={symbol}&date={new_date}&apikey={api_key}"
        r_holdings = make_request(holdings_url)

        if "Error Message" in r_holdings.json():
            raise RuntimeError(r_holdings.json()["Error Message"])
        holdings = pd.DataFrame(r_holdings.json())

        return holdings

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfHoldingsQueryParams:
        """Transform the query."""
        return FMPEtfHoldingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Return the raw data from the FMP endpoint."""
        query.symbol = query.symbol.upper()
        api_key = credentials.get("fmp_api_key") if credentials else ""

        return FMPEtfHoldingsFetcher.get_holdings(
            symbol=query.symbol, date=query.date, api_key=api_key
        )

    @staticmethod
    def transform_data(
        data: pd.DataFrame,
    ) -> Tuple[List[FMPEtfHoldingsData], Dict[str, str]]:
        """Return the transformed data."""
        metadata = {}
        results = pd.DataFrame()
        if not data.empty:
            metadata.update(
                {
                    "cik": data.iloc[0].get("cik"),
                    "acceptance_time": data.iloc[0].get("acceptanceTime"),
                    "date": data.iloc[0].get("date"),
                }
            )
            results = (
                data.sort_values(by="pctVal", ascending=False)
                .drop(columns=["cik", "acceptanceTime", "date"])
                .to_dict("records")
            )

        results = [FMPEtfHoldingsData.parse_obj(d) for d in results]
        return results, metadata
