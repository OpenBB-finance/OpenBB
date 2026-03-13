"""Insider Trading Standard Model."""

from datetime import (
    date as dateType,
    datetime,
    time,
)

from dateutil import parser
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class InsiderTradingQueryParams(QueryParams):
    """Insider Trading Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: int | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class InsiderTradingData(Data):
    """Insider Trading Data."""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    company_cik: str | None = Field(
        default=None,
        description="CIK number of the company.",
        coerce_numbers_to_str=True,
    )
    filing_date: dateType | datetime | None = Field(
        default=None, description="Filing date of the trade."
    )
    transaction_date: dateType | None = Field(
        default=None, description="Date of the transaction."
    )
    owner_cik: int | str | None = Field(
        default=None, description="Reporting individual's CIK."
    )
    owner_name: str | None = Field(
        default=None, description="Name of the reporting individual."
    )
    owner_title: str | None = Field(
        default=None, description="The title held by the reporting individual."
    )
    ownership_type: str | None = Field(
        default=None, description="Type of ownership, e.g., direct or indirect."
    )
    transaction_type: str | None = Field(
        default=None, description="Type of transaction being reported."
    )
    acquisition_or_disposition: str | None = Field(
        default=None, description="Acquisition or disposition of the shares."
    )
    security_type: str | None = Field(
        default=None, description="The type of security transacted."
    )
    securities_owned: float | None = Field(
        default=None,
        description="Number of securities owned by the reporting individual.",
    )
    securities_transacted: float | None = Field(
        default=None,
        description="Number of securities transacted by the reporting individual.",
    )
    transaction_price: float | None = Field(
        default=None, description="The price of the transaction."
    )
    filing_url: str | None = Field(default=None, description="Link to the filing.")

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
