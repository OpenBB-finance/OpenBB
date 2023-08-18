"""Stock insider trading data model."""


from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol

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
        default=["P-Purchase"], description="Type of the transaction."
    )
    reportingCik: Optional[int] = Field(description="CIK of the reporting owner.")
    companyCik: Optional[int] = Field(description="CIK of the company owner.")
    page: Optional[int] = Field(
        default=0, description="Page number of the data to fetch."
    )


class StockInsiderTradingData(Data, BaseSymbol):
    """Stock Insider Trading Data."""

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
    securities_owned: int = Field(
        description="Securities owned of the stock insider trading."
    )
    company_cik: int = Field(description="Company CIK of the stock insider trading.")
    reporting_name: str = Field(
        description="Reporting name of the stock insider trading."
    )
    type_of_owner: str = Field(
        description="Type of owner of the stock insider trading."
    )
    acquistion_or_disposition: str = Field(
        description="Acquistion or disposition of the stock insider trading."
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
