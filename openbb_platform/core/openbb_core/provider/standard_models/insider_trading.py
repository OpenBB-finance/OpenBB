"""Insider Trading Standard Model."""

from datetime import date, datetime, time
from typing import List, Optional, Set, Union

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
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class InsiderTradingData(Data):
    """Insider Trading Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    company_cik: Optional[Union[str, int]] = Field(
        default=None, description="CIK for the company of the shares transacted."
    )
    filing_date: Optional[datetime] = Field(
        default=None, description="The date of the filing discolsure."
    )
    transaction_date: Optional[date] = Field(
        default=None, description="The date of the transaction."
    )
    owner_cik: Optional[Union[str, int]] = Field(
        default=None, description="The owner's CIK for SEC reporting."
    )
    owner_name: Optional[str] = Field(
        default=None, description="The name of the owner making the transaction."
    )
    owner_title: Optional[str] = Field(
        default=None, description="The job title held by the owner of the shares."
    )
    transaction_type: Optional[str] = Field(
        default=None, description="The type of transaction."
    )
    acquisition_or_disposition: Optional[str] = Field(
        default=None,
        description="Acquisition or disposition of the shares.",
    )
    security_type: Optional[str] = Field(
        default=None, description="The type of security being transacted."
    )
    securities_owned: Optional[float] = Field(
        default=None, description="Number of securities owned by the insider."
    )
    securities_transacted: Optional[float] = Field(
        default=None, description="Number of securities transacted."
    )
    transaction_price: Optional[float] = Field(
        default=None,
        description="The execution price of the trade.",
    )
    filing_url: Optional[str] = Field(
        default=None, description="URL for the public filing document."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])

    @field_validator("filing_date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        if v:
            filing_date = parser.isoparse(str(v))

            if filing_date.time() == time(0, 0):
                return datetime.combine(filing_date.date(), time(0, 0, 0))
            return filing_date
        return None
