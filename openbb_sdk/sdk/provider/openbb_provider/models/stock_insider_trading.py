"""Stock insider trading data model."""


from datetime import date, datetime
from typing import List, Literal, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol

from pydantic import Field


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


class StockInsiderTradingQueryParams(QueryParams, BaseSymbol):
    """Stock Insider Trading Query."""

    transactionType: Optional[List[TRANSACTION_TYPES]] = Field(
        default=["P-Purchase"], description="The type of the transaction."
    )
    reportingCik: Optional[int] = Field(description="The CIK of the reporting owner.")
    companyCik: Optional[int] = Field(description="The CIK of the company owner.")
    page: Optional[int] = Field(
        default=0, description="The page number of the data to fetch."
    )


class StockInsiderTradingData(Data, BaseSymbol):
    """Stock Insider Trading Data."""

    filing_date: datetime = Field(
        description="The filing date of the stock insider trading."
    )
    transaction_date: date = Field(
        description="The transaction date of the stock insider trading."
    )
    reporting_cik: int = Field(
        description="The reporting CIK of the stock insider trading."
    )
    transaction_type: str = Field(
        description="The transaction type of the stock insider trading."
    )
    securities_owned: int = Field(
        description="The securities owned of the stock insider trading."
    )
    company_cik: int = Field(
        description="The company CIK of the stock insider trading."
    )
    reporting_name: str = Field(
        description="The reporting name of the stock insider trading."
    )
    type_of_owner: str = Field(
        description="The type of owner of the stock insider trading."
    )
    acquistion_or_disposition: str = Field(
        description="The acquistion or disposition of the stock insider trading."
    )
    form_type: str = Field(description="The form type of the stock insider trading.")
    securities_transacted: float = Field(
        description="The securities transacted of the stock insider trading."
    )
    price: float = Field(description="The price of the stock insider trading.")
    security_name: str = Field(
        description="The security name of the stock insider trading."
    )
    link: str = Field(description="The link of the stock insider trading.")
