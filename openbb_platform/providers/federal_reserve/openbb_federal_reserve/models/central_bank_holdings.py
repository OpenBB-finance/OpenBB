"""Federal Reserve Central Bank Holdings Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.central_bank_holdings import (
    CentralBankHoldingsData,
    CentralBankHoldingsQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator, model_validator

HoldingTypes = Literal[
    "all_agency",
    "agency_debts",
    "mbs",
    "cmbs",
    "all_treasury",
    "bills",
    "notesbonds",
    "frn",
    "tips",
]
HOLDING_TYPE_CHOICES: list[Any] = [
    "all_agency",
    "agency_debts",
    "mbs",
    "cmbs",
    "all_treasury",
    "bills",
    "notesbonds",
    "frn",
    "tips",
]
AGENCY_HOLDING_TYPES = {
    "all": "all",
    "agency_debts": "agency%20debts",
    "mbs": "mbs",
    "cmbs": "cmbs",
}
TREASURY_HOLDING_TYPES = ["all", "bills", "notesbonds", "frn", "tips"]


class FederalReserveCentralBankHoldingsQueryParams(CentralBankHoldingsQueryParams):
    """Federal Reserve Central Bank Holdings Query."""

    __json_schema_extra__ = {
        "cusip": {"multiple_items_allowed": True},
        "holding_type": {
            "x-widget_config": {
                "options": [
                    {"label": "All Agency securities", "value": "all_agency"},
                    {"label": "Agency debts", "value": "agency_debts"},
                    {
                        "label": "Agency mortgage-backed securities (MBS)",
                        "value": "mbs",
                    },
                    {
                        "label": "Agency commercial mortgage-backed securities (CMBS)",
                        "value": "cmbs",
                    },
                    {"label": "All Treasury securities", "value": "all_treasury"},
                    {"label": "Treasury bills", "value": "bills"},
                    {"label": "Treasury notes and bonds", "value": "notesbonds"},
                    {"label": "Treasury floating rate notes (FRN)", "value": "frn"},
                    {
                        "label": "Treasury inflation-protected securities (TIPS)",
                        "value": "tips",
                    },
                ]
            }
        },
    }

    holding_type: HoldingTypes = Field(
        default="all_treasury",
        description="Type of holdings to return.",
        json_schema_extra={"choices": HOLDING_TYPE_CHOICES},
    )
    summary: bool = Field(
        default=False,
        description="If True, returns historical weekly summary by holding type."
        + " This parameter takes priority over other parameters.",
    )
    cusip: str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("cusip", ""),
    )
    wam: bool = Field(
        default=False,
        description="If True, returns weighted average maturity aggregated by agency or treasury securities."
        + " This parameter takes priority over `holding_type`, `cusip`, and `monthly`.",
    )
    monthly: bool = Field(
        default=False,
        description="If True, returns historical data for all Treasury securities at a monthly interval."
        + " This parameter takes priority over other parameters, except `wam`."
        + " Only valid when `holding_type` is set to: 'all_treasury', 'bills', 'notesbonds', 'frn', 'tips'.",
    )


class FederalReserveCentralBankHoldingsData(CentralBankHoldingsData):
    """Federal Reserve Central Bank Holdings Data."""

    __alias_dict__ = {
        "date": "asOfDate",
        "notes_and_bonds": "notesbonds",
        "description": "securityDescription",
        "face_value": "currentFaceValue",
        "is_aggregated": "isAggregated",
        "security_type": "securityTypes",
        "tips_inflation_compensation": "tipsInflationCompensation",
        "change_prior_week": "changeFromPriorWeek",
        "change_prior_year": "changeFromPriorYear",
    }

    security_type: str | None = Field(
        default=None,
        description="Type of security - i.e. TIPs, FRNs, etc.",
    )
    description: str | None = Field(
        default=None,
        description="Description of the security. Only returned for Agency securities.",
    )
    is_aggregated: Literal["Y"] | None = Field(
        default=None,
        description="Whether the security is aggregated. Only returned for Agency securities.",
    )
    cusip: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cusip", ""),
    )
    issuer: str | None = Field(
        default=None,
        description="Issuer of the security.",
    )
    maturity_date: dateType | None = Field(
        default=None,
        description="Maturity date of the security.",
    )
    term: str | None = Field(
        default=None,
        description="Term of the security. Only returned for Agency securities.",
    )
    face_value: float | None = Field(
        default=None,
        description="Current face value of the security ($USD)."
        + " Current face value of the securities, which is the remaining principal balance of the securities.",
    )
    par_value: float | None = Field(
        default=None,
        description="Par value of the security ($USD)."
        + " Changes in par may reflect primary and secondary market transactions and/or custodial account activity.",
    )
    coupon: float | None = Field(
        default=None,
        description="Coupon rate of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    spread: float | None = Field(
        default=None,
        description="Spread to the current reference rate, as determined at each security's initial auction.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percent_outstanding: float | None = Field(
        default=None,
        description="Total percent of the outstanding CUSIP issuance.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    bills: float | None = Field(
        default=None,
        description="Treasury bills amount ($USD)."
        + " Only returned when 'summary' is True.",
    )
    frn: float | None = Field(
        default=None,
        description="Floating rate Treasury notes amount ($USD)."
        + " Only returned when 'summary' is True.",
    )
    notes_and_bonds: float | None = Field(
        default=None,
        description="Treasuy Notes and bonds amount ($USD)."
        + " Only returned when 'summary' is True.",
    )
    tips: float | None = Field(
        default=None,
        description="Treasury inflation-protected securities amount ($USD)."
        + " Only returned when 'summary' is True.",
    )
    mbs: float | None = Field(
        default=None,
        description="Mortgage-backed securities amount ($USD)."
        + " Only returned when 'summary' is True.",
    )
    cmbs: float | None = Field(
        default=None,
        description="Commercial mortgage-backed securities amount ($USD)."
        + " Only returned when 'summary' is True.",
    )
    agencies: float | None = Field(
        default=None,
        description="Agency securities amount ($USD)."
        + " Only returned when 'summary' is True.",
    )
    total: float | None = Field(
        default=None,
        description="Total SOMA holdings amount ($USD)."
        + " Only returned when 'summary' is True.",
    )
    tips_inflation_compensation: float | None = Field(
        default=None,
        description="Treasury inflation-protected securities inflation compensation amount ($USD)."
        + " Only returned when 'summary' is True.",
        alias="inflationCompensation",
    )
    change_prior_week: float | None = Field(
        default=None,
        description="Change in SOMA holdings from the prior week ($USD).",
    )
    change_prior_year: float | None = Field(
        default=None,
        description="Change in SOMA holdings from the prior year ($USD).",
    )

    @field_validator("security_type", mode="before", check_fields=False)
    @classmethod
    def validate_security_type(cls, v):
        """Validate the security type."""
        if not v:
            return None
        if isinstance(v, list):
            return ",".join(v)
        return v

    @field_validator("coupon", "spread", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize the percent value."""
        return float(v) / 100 if v and v != "''" else None

    @model_validator(mode="before")
    @classmethod
    def empty_strings(cls, values):
        """Clear empty strings and replace with None."""
        return (
            {k: None if v in ("''", "", "0") else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class FederalReserveCentralBankHoldingsFetcher(
    Fetcher[
        FederalReserveCentralBankHoldingsQueryParams,
        list[FederalReserveCentralBankHoldingsData],
    ]
):
    """Federal Reserve Central Bank Holdings Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveCentralBankHoldingsQueryParams:
        """Transform the query params."""
        return FederalReserveCentralBankHoldingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FederalReserveCentralBankHoldingsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FederalReserve endpoint."""
        from openbb_federal_reserve.utils.ny_fed_api import SomaHoldings

        hold_type = "all" if "all" in query.holding_type else query.holding_type
        security_type = query.holding_type
        date = query.date.strftime("%Y-%m-%d") if query.date else None
        if (
            query.holding_type == "all_agency"
            or query.holding_type in AGENCY_HOLDING_TYPES
        ):
            security_type = "agency"
        if (
            query.holding_type == "all_treasury"
            or query.holding_type in TREASURY_HOLDING_TYPES
        ):
            security_type = "treasury"
        if query.cusip is not None:
            cusips = (
                query.cusip if isinstance(query.cusip, str) else ",".join(query.cusip)
            )
            return (
                await SomaHoldings().get_agency_holdings(cusip=cusips, as_of=date)
                if security_type == "agency"
                else await SomaHoldings().get_treasury_holdings(
                    cusip=cusips, as_of=date
                )
            )
        if query.summary is True:
            return await SomaHoldings().get_summary()
        if query.monthly is True:
            return await SomaHoldings().get_treasury_holdings(
                monthly=True, holding_type=hold_type
            )
        if security_type == "treasury" and query.wam is True:
            return await SomaHoldings().get_treasury_holdings(wam=True, as_of=date)
        if security_type == "agency" and query.wam is True:
            return await SomaHoldings().get_agency_holdings(wam=True, as_of=date)
        return (
            await SomaHoldings().get_agency_holdings(as_of=date, holding_type=hold_type)
            if security_type == "agency"
            else await SomaHoldings().get_treasury_holdings(
                as_of=date, holding_type=hold_type
            )
        )

    @staticmethod
    def transform_data(
        query: FederalReserveCentralBankHoldingsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveCentralBankHoldingsData]:
        """Transform data."""
        return [FederalReserveCentralBankHoldingsData.model_validate(d) for d in data]
