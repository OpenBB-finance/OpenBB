"""Insider Trading Standard Model."""

from datetime import date, datetime, time
from typing import List, Literal, Optional, Set, Union

from dateutil import parser
from pydantic import Field, StrictInt, field_validator, model_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS

TRANSACTION_TYPES = Literal[
    "A-Award",
    "C-Conversion",
    "D-Return",
    "E-ExpireShort",
    "F-InKind",
    "G-Gift",
    "H-ExpireLong",
    "I-Discretionary",
    "J-Other",
    "L-Small",
    "M-Exempt",
    "O-OutOfTheMoney",
    "P-Purchase",
    "S-Sale",
    "U-Tender",
    "W-Will",
    "X-InTheMoney",
    "Z-Trust",
]


class InsiderTradingQueryParams(QueryParams):
    """Insider Trading Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    transaction_type: Optional[Union[List[TRANSACTION_TYPES], str]] = Field(
        default=["P-Purchase"], description="Type of the transaction."
    )
    limit: StrictInt = Field(
        default=100,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )

    @model_validator(mode="after")
    @classmethod
    def validate_transaction_type(cls, values: "InsiderTradingQueryParams"):
        """Validate the transaction type."""
        if isinstance(values.transaction_type, list):
            values.transaction_type = ",".join(values.transaction_type)
        return values

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class InsiderTradingData(Data):
    """Insider Trading Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    filing_date: datetime = Field(description="Filing date of the insider trading.")
    transaction_date: date = Field(
        description="Transaction date of the insider trading."
    )
    reporting_cik: int = Field(description="Reporting CIK of the insider trading.")
    transaction_type: str = Field(
        description="Transaction type of the insider trading."
    )
    securities_owned: StrictInt = Field(
        description="Securities owned of the insider trading."
    )
    company_cik: int = Field(description="Company CIK of the insider trading.")
    reporting_name: str = Field(description="Reporting name of the insider trading.")
    type_of_owner: str = Field(description="Type of owner of the insider trading.")
    acquisition_or_disposition: Optional[str] = Field(
        default=None,
        description="Acquisition or disposition of the insider trading.",
    )
    form_type: str = Field(description="Form type of the insider trading.")
    securities_transacted: float = Field(
        description="Securities transacted of the insider trading."
    )
    price: Optional[float] = Field(
        default=None,
        description="Price of the insider trading.",
    )
    security_name: str = Field(description="Security name of the insider trading.")
    link: str = Field(description="Link of the insider trading.")

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
        filing_date = parser.isoparse(str(v))

        if filing_date.time() == time(0, 0):
            return datetime.combine(filing_date.date(), time(0, 0, 0))
        return filing_date
