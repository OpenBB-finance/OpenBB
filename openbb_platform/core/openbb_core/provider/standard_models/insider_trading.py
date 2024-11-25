"""Insider Trading Standard Model."""

from datetime import (
    date as dateType,
    datetime,
    time,
)
from typing import Optional, Union

from dateutil import parser
from pydantic import Field, StrictInt, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class InsiderTradingQueryParams(QueryParams):
    """Insider Trading Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: StrictInt = Field(
        default=500,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class InsiderTradingData(Data):
    """Insider Trading Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    company_cik: Optional[Union[int, str]] = Field(
        default=None, description="CIK number of the company."
    )
    filing_date: Optional[Union[dateType, datetime]] = Field(
        default=None, description="Filing date of the trade."
    )
    transaction_date: Optional[dateType] = Field(
        default=None, description="Date of the transaction."
    )
    owner_cik: Optional[Union[int, str]] = Field(
        default=None, description="Reporting individual's CIK."
    )
    owner_name: Optional[str] = Field(
        default=None, description="Name of the reporting individual."
    )
    owner_title: Optional[str] = Field(
        default=None, description="The title held by the reporting individual."
    )
    transaction_type: Optional[str] = Field(
        default=None, description="Type of transaction being reported."
    )
    acquisition_or_disposition: Optional[str] = Field(
        default=None, description="Acquisition or disposition of the shares."
    )
    security_type: Optional[str] = Field(
        default=None, description="The type of security transacted."
    )
    securities_owned: Optional[float] = Field(
        default=None,
        description="Number of securities owned by the reporting individual.",
    )
    securities_transacted: Optional[float] = Field(
        default=None,
        description="Number of securities transacted by the reporting individual.",
    )
    transaction_price: Optional[float] = Field(
        default=None, description="The price of the transaction."
    )
    filing_url: Optional[str] = Field(default=None, description="Link to the filing.")

    @field_validator(
        "filing_date", "transaction_date", mode="before", check_fields=False
    )
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        if v:
            filing_date = parser.isoparse(str(v))
            if filing_date.time() == time(0, 0):
                return filing_date.date()
            return filing_date
        return None
