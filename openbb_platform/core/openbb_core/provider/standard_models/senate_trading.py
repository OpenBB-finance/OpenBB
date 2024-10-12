"""Senate Trading Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class SenateTradingQueryParams(QueryParams):
    """Senate Trading Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()



class SenateTradingData(Data):
    """Senate Trading data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    first_name: Optional[str] = Field(
        default=None, description="Senator's first name."
    )
    last_name: Optional[str] = Field(
        default=None, description="Senator's last name."
    )
    office: Optional[str] = Field(
        default=None, description="Senator's office."
    )
    link: Optional[str] = Field(
        default=None, description="Link to the transaction record."
    )
    date_recieved: Optional[dateType] = Field(
        default=None, description="Date the transaction was received."
    )
    transaction_date: Optional[dateType] = Field(
        default=None, description="Date of the transaction."
    )
    owner: Optional[str] = Field(
        default=None, description="Owner of the transaction."
    )
    assetDescription: Optional[str] = Field(
        default=None, description="Description of the asset traded."
    )
    assetType: Optional[str] = Field(
        default=None, description="Type of the asset traded."
    )
    type: Optional[str] = Field(
        default=None, description="Type of the transaction."
    )
    amount: Optional[str] = Field(
        default=None, description="Amount range to be traded."
    )
    comment: Optional[str] = Field(
        default=None, description="Comment on the transaction."
    )
