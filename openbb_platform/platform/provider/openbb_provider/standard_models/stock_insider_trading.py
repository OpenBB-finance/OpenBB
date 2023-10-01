"""Stock insider trading data model."""


from datetime import date, datetime
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, field_validator, model_validator

from openbb_provider.abstract.data import Data, StrictInt
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS

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


class StockInsiderTradingQueryParams(QueryParams):
    """Stock Insider Trading Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    transactionType: Optional[Union[List[TRANSACTION_TYPES], str]] = Field(
        default=["P-Purchase"], description="Type of the transaction."
    )
    page: Optional[int] = Field(
        default=0, description="Page number of the data to fetch."
    )

    @model_validator(mode="after")
    @classmethod
    def validate_transaction_type(cls, values: "StockInsiderTradingQueryParams"):
        """Validate the transaction type."""
        if isinstance(values.transactionType, list):
            values.transactionType = ",".join(values.transactionType)
        return values

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class StockInsiderTradingData(Data):
    """Stock Insider Trading Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    filing_date: datetime = Field(
        description="Filing date of the stock insider trading."
    )
    transaction_date: date = Field(
        description="Transaction date of the stock insider trading."
    )
    reporting_cik: int = Field(
        description="Reporting CIK of the stock insider trading."
    )
    transaction_type: str = Field(
        description="Transaction type of the stock insider trading."
    )
    securities_owned: StrictInt = Field(
        description="Securities owned of the stock insider trading."
    )
    company_cik: int = Field(description="Company CIK of the stock insider trading.")
    reporting_name: str = Field(
        description="Reporting name of the stock insider trading."
    )
    type_of_owner: str = Field(
        description="Type of owner of the stock insider trading."
    )
    acquisition_or_disposition: str = Field(
        description="Acquisition or disposition of the stock insider trading.",
    )
    form_type: str = Field(description="Form type of the stock insider trading.")
    securities_transacted: float = Field(
        description="Securities transacted of the stock insider trading."
    )
    price: float = Field(description="Price of the stock insider trading.")
    security_name: str = Field(
        description="Security name of the stock insider trading."
    )
    link: str = Field(description="Link of the stock insider trading.")

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
