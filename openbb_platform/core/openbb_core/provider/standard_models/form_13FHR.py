"""From 13F-HR Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)


class Form13FHRQueryParams(QueryParams):
    """Form 13F-HR Query."""

    __validator_dict__ = {"check_single": ("symbol")}

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " A CIK or Symbol can be used."
    )
    date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " The date represents the end of the reporting period."
        + " All form 13F-HR filings are based on the calendar year"
        + " and are reported quarterly."
        + " If a date is not supplied, the most recent filing is returned."
        + " Submissions beginning 2013-06-30 are supported.",
    )
    limit: Optional[int] = Field(
        default=1,
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + " The number of previous filings to return."
        + " This parameter is overriden by the date parameter.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str):
        """Convert symbol to uppercase."""
        return str(v).upper()


class Form13FHRData(Data):
    """Form 13F-HR Data."""

    period_ending: dateType = Field(
        description="The date of the reporting period ended."
    )
    issuer: str = Field(description="The name of the issuer.")
    cusip: str = Field(description="The CUSIP of the security.")
    asset_class: str = Field(
        description="The title of the asset class for the security."
    )
    security_type: str = Field(
        description="The type of security"
        + " 'SH' for shares. 'PRN' for principal amount. 'Call' or 'Put' for options.",
    )
    investment_discretion: str = Field(
        description="The nature of the investment discretion held by the Manager."
        + " One of: 'SOLE', 'DFND' (defined), 'OTR' (other).",
    )
    voting_authority_sole: Optional[int] = Field(
        default=None,
        description="The number of shares for which the Manager"
        + " exercises sole voting authority (none).",
    )
    voting_authority_shared: Optional[int] = Field(
        default=None,
        description="The number of shares for which the Manager"
        + " exercises a defined shared voting authority (none).",
    )
    voting_authority_other: Optional[int] = Field(
        default=None,
        description="The number of shares for which the Manager"
        + " exercises other shared voting authority (none).",
    )
    principal_amount: int = Field(
        description="The total number of shares of the class of security"
        + " or the principla amount of such class.",
    )
    value: int = Field(
        description="The fair market value of the holding of the particular class of security."
        + " Values are rounded to the nearest US dollar",
    )
