"""FMP ETF Holdings Model."""

# pylint: disable=unused-argument

import warnings
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, field_validator

_warn = warnings.warn


class FMPEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """FMP ETF Holdings Query.

    Source: https://site.financialmodelingprep.com/developer/docs#Historical-ETF-Holdings
    """

    date: Optional[Union[str, dateType]] = Field(
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " Entering a date will attempt to return the NPORT-P filing for the entered date."
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

    __alias_dict__ = {
        "weight": "weightPercentage",
        "value": "marketValue",
        "symbol": "asset",
        "balance": "sharesNumber",
    }

    lei: Optional[str] = Field(description="The LEI of the holding.", default=None)
    title: Optional[str] = Field(description="The title of the holding.", default=None)
    cusip: Optional[str] = Field(description="The CUSIP of the holding.", default=None)
    isin: Optional[str] = Field(description="The ISIN of the holding.", default=None)
    balance: Optional[ForceInt] = Field(
        description="The balance of the holding, in shares or units.", default=None
    )
    units: Optional[Union[float, str]] = Field(
        description="The type of units.", default=None
    )
    currency: Optional[str] = Field(
        description="The currency of the holding.", alias="cur_cd", default=None
    )
    value: Optional[float] = Field(
        description="The value of the holding, in dollars.",
        alias="valUsd",
        default=None,
    )
    weight: Optional[float] = Field(
        description="The weight of the holding, as a normalized percent.",
        alias="pctVal",
        default=None,
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
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
    updated: Optional[Union[dateType, datetime]] = Field(
        description="The date the data was updated.", default=None
    )

    @field_validator("weight", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent values."""
        return float(v) / 100 if v else None

    @field_validator("cusip", "isin", "balance", "name", "symbol", "value")
    @classmethod
    def replace_empty(cls, v):
        """Replace empty strings and 0s with None."""
        if isinstance(v, str):
            return v if v not in ("", "0") else None
        if isinstance(v, (float, int)):
            return v if v and v not in (0.0, 0) else None
        return v if v else None


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
    async def aextract_data(
        query: FMPEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        data = []
        if query.date is not None:
            url = create_url(
                version=4, endpoint="etf-holdings", api_key=api_key, query=query
            )
            try:
                data = await get_data_many(url, **kwargs)
            except Exception:
                _warn(
                    "No data found for this symbol and date, attempting to retrieve the most recent data available."
                )

        if query.date is None or not data:
            url = f"https://financialmodelingprep.com/api/v3/etf-holder/{query.symbol}?apikey={api_key}"
            data = await get_data_many(url, **kwargs)
        return data

    @staticmethod
    def transform_data(
        query: FMPEtfHoldingsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPEtfHoldingsData]:
        """Return the transformed data."""
        return [FMPEtfHoldingsData.model_validate(d) for d in data]
