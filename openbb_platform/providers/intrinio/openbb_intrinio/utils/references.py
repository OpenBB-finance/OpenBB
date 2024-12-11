"""Intrinio References Helpers."""

from typing import Literal, Optional

from openbb_core.provider.abstract.data import Data
from pydantic import Field

SOURCES = Literal[
    "iex",
    "bats",
    "bats_delayed",
    "utp_delayed",
    "cta_a_delayed",
    "cta_b_delayed",
    "intrinio_mx",
    "intrinio_mx_plus",
    "delayed_sip",
]

VENUES = {
    "A": "NYSE MKT",
    "B": "NASDAQ OMX BX",
    "C": "National Stock Exchange",
    "D": "FINRA ADF",
    "I": "International Securities Exchange",
    "J": "Bats EDGA Exchange",
    "K": "Bats EDGX Exchange",
    "L": "Long-term Stock Exchange",
    "M": "Chicago Stock Exchange",
    "N": "New York Stock Exchange",
    "P": "NYSE Arca",
    "S": "Consolidated Tape System",
    "T": "NASDAQ (Tape A, B securities)",
    "Q": "NASDAQ (Tape C securities)",
    "V": "The Investors Exchange",
    "W": "Cboe",
    "X": "NASDAQ OMX PSX",
    "Y": "Bats BYX Exchange",
    "Z": "Bats BZX Exchange",
    "U": "Other OTC Markets",
}


TRADE_CONDITIONS = {
    "@": "Regular Sale",
    "A": "Acquisition",
    "B": "Bunched Trade",
    "C": "Cash Sale",
    "D": "Distribution",
    "E": "Placeholder",
    "F": "Intermarket Sweep",
    "G": "Bunched Sold Trade",
    "H": "Priced Variation Trade",
    "I": "Odd Lot Trade",
    "K": "Rule 155 Trade (AMEX)",
    "L": "Sold Last",
    "M": "Market Center Official Close",
    "N": "Next Day",
    "O": "Opening Prints",
    "P": "Prior Reference Price",
    "Q": "Market Center Official Open",
    "R": "Seller",
    "S": "Split Trade",
    "T": "Form T",
    "U": "Extended Trading Hours (Sold Out of Sequence)",
    "V": "Contingent Trade",
    "W": "Average Price Trade",
    "X": "Cross/Periodic Auction Trade",
    "Y": "Yellow Flag Regular Trade",
    "Z": "Sold (Out of Sequence)",
    "1": "Stopped Stock (Regular Trade)",
    "4": "Derivatively Priced",
    "5": "Re-Opening Prints",
    "6": "Closing Prints",
    "7": "Qualified Contingent Trade (QCT)",
    "8": "Placeholder for 611 Exempt",
    "9": "Corrected Consolidated Close",
}

ETF_EXCHANGES = Literal[
    "xnas",
    "arcx",
    "bats",
    "xnys",
    "bvmf",
    "xshg",
    "xshe",
    "xhkg",
    "xbom",
    "xnse",
    "xidx",
    "tase",
    "xkrx",
    "xkls",
    "xmex",
    "xses",
    "roco",
    "xtai",
    "xbkk",
    "xist",
]


ETF_PERFORMANCE_MAP = {
    "trailing_one_month_return_split_and_dividend": "one_month",
    "trailing_one_month_return_split_only": "one_month",
    "trailing_one_year_return_split_and_dividend": "one_year",
    "trailing_one_year_return_split_only": "one_year",
    "trailing_one_year_volatility_annualized": "volatility_one_year",
    "trailing_three_year_annualized_return_split_and_dividend": "three_year",
    "trailing_three_year_annualized_return_split_only": "three_year",
    "trailing_three_year_volatility_annualized": "volatility_three_year",
    "trailing_five_year_annualized_return_split_and_dividend": "five_year",
    "trailing_five_year_annualized_return_split_only": "five_year",
    "trailing_five_year_volatility_annualized": "volatility_five_year",
    "trailing_ten_year_annualized_return_split_and_dividend": "ten_year",
    "trailing_ten_year_annualized_return_split_only": "ten_year",
    "inception_annualized_return_split_and_dividend": "max_annualized",
    "inception_annualized_return_split_only": "max_annualized",
    "calendar_year_5_return_split_and_dividend": "five_year",
    "calendar_year_5_return_split_only": "five_year",
    "calendar_year_4_return_split_and_dividend": "four_year",
    "calendar_year_4_return_split_only": "four_year",
    "calendar_year_3_return_split_and_dividend": "three_year",
    "calendar_year_3_return_split_only": "three_year",
    "calendar_year_2_return_split_and_dividend": "two_year",
    "calendar_year_2_return_split_only": "two_year",
    "calendar_year_1_return_split_and_dividend": "one_year",
    "calendar_year_1_return_split_only": "one_year",
    "calendar_year_to_date_return_split_and_dividend": "ytd",
    "calendar_year_to_date_return_split_only": "ytd",
    "net_asset_value": "nav",
    "beta_vs_spy": "beta",
}


class IntrinioCompany(Data):
    """Intrinio Company Data."""

    id: str = Field(description="The Intrinio ID of the Company.")
    ticker: Optional[str] = Field(
        description="The stock market ticker symbol associated with the company's common stock securities",
        default=None,
    )
    name: Optional[str] = Field(description="The company's common name.", default=None)
    lei: Optional[str] = Field(
        description="The Legal Entity Identifier (LEI) of the company.", default=None
    )
    cik: Optional[str] = Field(
        description="The Central Index Key (CIK) of the company.",
    )


class IntrinioSecurity(Data):
    """Intrinio Security Data."""

    id: str = Field(description="The Intrinio ID for Security.")
    company_id: Optional[str] = Field(
        description="The Intrinio ID for the company for which the Security is issued.",
        default=None,
    )
    name: Optional[str] = Field(description="Name of the Security.", default=None)
    code: Optional[str] = Field(
        description="""
            A 2-3 digit code classifying the Security.
            Reference: https://docs.intrinio.com/documentation/security_codes
        """,
        default=None,
    )
    currency: Optional[str] = Field(
        description="The currency in which the Security is traded.", default=None
    )
    ticker: Optional[str] = Field(
        description="The common/local ticker of the Security.", default=None
    )
    composite_ticker: Optional[str] = Field(
        description="The country-composite ticker of the Security.", default=None
    )
    figi: Optional[str] = Field(description="The OpenFIGI identifier.", default=None)
    composite_figi: Optional[str] = Field(
        description="The country-composite OpenFIGI identifier.", default=None
    )
    share_class_figi: Optional[str] = Field(
        description="The global-composite OpenFIGI identifier.", default=None
    )
    primary_listing: Optional[bool] = Field(
        description="""
            If true, the Security is the primary issue for the company,
            otherwise it is a secondary issue on a secondary stock exchange,
        """,
        default=None,
    )
