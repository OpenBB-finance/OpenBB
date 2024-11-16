"""SEC Insider Trading Model."""

# pylint: disable =unused-argument

from datetime import date as dateType
from typing import Any, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.insider_trading import (
    InsiderTradingData,
    InsiderTradingQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator

TRANSACTION_CODE_MAP = {
    "A": "Grant, award or other acquisition pursuant to Rule 16b-3(d)",
    "C": "Conversion of derivative security",
    "D": "Disposition to the issuer of issuer equity securities pursuant to Rule 16b-3(e)",
    "E": "Expiration of short derivative position",
    "F": (
        "Payment of exercise price or tax liability by delivering or withholding securities incident to the receipt, "
        "exercise or vesting of a security issued in accordance with Rule 16b-3"
    ),
    "G": "Bona fide gift",
    "H": "Expiration (or cancellation) of long derivative position with value received",
    "I": (
        "Discretionary transaction in accordance with Rule 16b-3(f) "
        "resulting in acquisition or disposition of issuer securities"
    ),
    "J": "Other acquisition or disposition (describe transaction)",
    "L": "Small acquisition under Rule 16a-6",
    "M": "Exercise or conversion of derivative security exempted pursuant to Rule 16b-3",
    "O": "Exercise of out-of-the-money derivative security",
    "P": "Open market or private purchase of non-derivative or derivative security",
    "S": "Open market or private sale of non-derivative or derivative security",
    "U": "Disposition pursuant to a tender of shares in a change of control transaction",
    "W": "Acquisition or disposition by will or the laws of descent and distribution",
    "X": "Exercise of in-the-money or at-the-money derivative security",
    "Z": "Deposit into or withdrawal from voting trust",
}

TIMELINESS_MAP = {
    "E": "Early",
    "L": "Late",
    "Empty": "On-time",
}


class SecInsiderTradingQueryParams(InsiderTradingQueryParams):
    """SEC Insider Trading Query Params.

    Source: https://www.sec.gov/Archives/edgar/data/
    """

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Wide date ranges can result in long download times."
        + " Recommended to use a smaller date range, default is 120 days ago.",
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "") + " Default is today.",
    )
    use_cache: bool = Field(
        default=True,
        description="Persist the data locally for future use. Default is True."
        + " Each form submission is an individual download and the SEC limits the number of concurrent downloads."
        + " This prevents the same file from being downloaded multiple times.",
    )


class SecInsiderTradingData(InsiderTradingData):
    """SEC Insider Trading Data."""

    company_name: Optional[str] = Field(
        default=None, description="Name of the company."
    )
    form: Optional[Union[str, int]] = Field(default=None, description="Form type.")
    director: Optional[bool] = Field(
        default=None, description="Whether the owner is a director."
    )
    officer: Optional[bool] = Field(
        default=None, description="Whether the owner is an officer."
    )
    ten_percent_owner: Optional[bool] = Field(
        default=None, description="Whether the owner is a 10% owner."
    )
    other: Optional[bool] = Field(
        default=None, description="Whether the owner is classified as other."
    )
    other_text: Optional[str] = Field(
        default=None, description="Text for other classification."
    )
    transaction_timeliness: Optional[str] = Field(
        default=None, description="Timeliness of the transaction."
    )
    ownership_type: Optional[str] = Field(
        default=None, description="Type of ownership, direct or indirect."
    )
    nature_of_ownership: Optional[str] = Field(
        default=None, description="Nature of the ownership."
    )
    exercise_date: Optional[dateType] = Field(
        default=None, description="Date of exercise."
    )
    expiration_date: Optional[dateType] = Field(
        default=None, description="Date of expiration for the derivative."
    )
    deemed_execution_date: Optional[dateType] = Field(
        default=None, description="Deemed execution date."
    )
    underlying_security_title: Optional[str] = Field(
        default=None, description="Title of the underlying security."
    )
    underlying_security_shares: Optional[float] = Field(
        default=None,
        description="Number of underlying shares associated with the derivative.",
    )
    underlying_security_value: Optional[float] = Field(
        default=None, description="Value of the underlying security."
    )
    conversion_exercise_price: Optional[float] = Field(
        default=None, description="Price of conversion or exercise of the securities."
    )
    transaction_value: Optional[float] = Field(
        default=None, description="Total value of the transaction."
    )
    value_owned: Optional[float] = Field(
        default=None, description="Value of the securities owned after the transaction."
    )
    footnote: Optional[str] = Field(
        default=None, description="Footnote for the transaction."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _to_upper(cls, v):
        """Convert symbol to uppercase."""
        return v.upper() if v else None

    @field_validator("ownership_type", mode="before", check_fields=False)
    @classmethod
    def _map_ownership_type(cls, v):
        """Map ownership type to description."""
        if not v:
            return None
        return "Direct" if v.strip() == "D" else "Indirect" if v.strip() == "I" else v

    @field_validator("acquisition_or_disposition", mode="before", check_fields=False)
    @classmethod
    def _map_acquisition_disposition(cls, v):
        """Map acquisition or disposition to description."""
        if not v:
            return None
        return (
            "Acquisition"
            if v.strip() == "A"
            else "Disposition" if v.strip() == "D" else v
        )

    @field_validator("transaction_type", mode="before", check_fields=False)
    @classmethod
    def _map_transaction_code(cls, v):
        """Map transaction code to description."""
        return TRANSACTION_CODE_MAP.get(v, v) if v else None

    @field_validator("transaction_timeliness", mode="before", check_fields=False)
    @classmethod
    def _map_timeliness(cls, v):
        """Map timeliness code to description."""
        return TIMELINESS_MAP.get(v, v) if v else None


class SecInsiderTradingFetcher(
    Fetcher[SecInsiderTradingQueryParams, list[SecInsiderTradingData]]
):
    """SEC Insider Trading Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecInsiderTradingQueryParams:
        """Transform query parameters."""
        # pylint: disable=import-outside-toplevel
        from datetime import datetime, timedelta

        start_date = params.get("start_date")
        end_date = params.get("end_date")

        if not start_date and not end_date:
            params["start_date"] = (datetime.now() - timedelta(days=120)).date()
            params["end_date"] = datetime.now().date()

        return SecInsiderTradingQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecInsiderTradingQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the SEC archives."""
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.form4 import get_form_4

        return await get_form_4(
            query.symbol,
            query.start_date,
            query.end_date,
            query.limit,
            query.use_cache,
        )

    @staticmethod
    def transform_data(
        query: SecInsiderTradingQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecInsiderTradingData]:
        """Transform the data."""
        return [SecInsiderTradingData.model_validate(d) for d in data]
