"""From 13F-HR Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class Form13FHRQueryParams(QueryParams):
    """Form 13F-HR Query."""

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
        + " The date parameter takes priority over this parameter.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """Convert field to uppercase."""
        return str(v).upper()


class Form13FHRData(Data):
    """
    Form 13F-HR Data.

    Detailed documentation of the filing can be found here:
    https://www.sec.gov/pdf/form13f.pdf
    """

    period_ending: dateType = Field(
        description="The end-of-quarter date of the filing."
    )
    issuer: str = Field(description="The name of the issuer.")
    cusip: str = Field(description="The CUSIP of the security.")
    asset_class: str = Field(
        description="The title of the asset class for the security."
    )
    security_type: Optional[Literal["SH", "PRN"]] = Field(
        default=None,
        description="Whether the principal amount represents the number of shares"
        + " or the principal amount of such class."
        + " 'SH' for shares. 'PRN' for principal amount."
        + " Convertible debt securities are reported as 'PRN'.",
    )
    option_type: Optional[Literal["call", "put"]] = Field(
        default=None,
        description="Defined when the holdings being reported are put or call options."
        + " Only long positions are reported.",
    )
    investment_discretion: Optional[str] = Field(
        default=None,
        description="The investment discretion held by the Manager."
        + " Sole, shared-defined (DFN), or shared-other (OTR).",
    )
    voting_authority_sole: Optional[int] = Field(
        default=None,
        description="The number of shares for which the Manager"
        + " exercises sole voting authority.",
    )
    voting_authority_shared: Optional[int] = Field(
        default=None,
        description="The number of shares for which the Manager"
        + " exercises a defined shared voting authority.",
    )
    voting_authority_none: Optional[int] = Field(
        default=None,
        description="The number of shares for which the Manager"
        + " exercises no voting authority.",
    )
    principal_amount: int = Field(
        description="The total number of shares of the class of security"
        + " or the principal amount of such class. Defined by the 'security_type'."
        + " Only long positions are reported"
    )
    value: int = Field(
        description="The fair market value of the holding of the particular class of security."
        + " The value reported for options is the fair market value of the underlying security"
        + " with respect to the number of shares controlled."
        + " Values are rounded to the nearest US dollar"
        + " and use the closing price of the last trading day of the calendar year or quarter.",
    )

    @field_validator("option_type", mode="before", check_fields=False)
    @classmethod
    def validate_option_type(cls, v: str):
        """Validate and convert to lower case."""
        return v.lower() if v else None
