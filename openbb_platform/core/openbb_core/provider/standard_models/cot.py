"""Commitment of Traders Reports Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class COTQueryParams(QueryParams):
    """Commitment of Traders Reports Query."""

    id: str = Field(
        description="A string with the CFTC market code or other identifying string,"
        + " such as the contract market name, commodity name, or commodity group - i.e, 'gold' or 'japanese yen'."
        + "Default report is Fed Funds Futures. Use the 'cftc_market_code' for an exact match.",
        default="045601",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Default is the most recent report.",
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class COTData(Data):
    """Commitment of Traders Reports Data.
    Data returned will vary based on the query, this model will not define all possible fields.
    """

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    report_week: str | None = Field(
        default=None, description="Report week for the year."
    )
    market_and_exchange_names: str | None = Field(
        default=None, description="Market and exchange names."
    )
    cftc_contract_market_code: str | None = Field(
        default=None, description="CFTC contract market code."
    )
    cftc_market_code: str | None = Field(default=None, description="CFTC market code.")
    cftc_region_code: str | None = Field(default=None, description="CFTC region code.")
    cftc_commodity_code: str | None = Field(
        default=None, description="CFTC commodity code."
    )
    cftc_contract_market_code_quotes: str | None = Field(
        default=None, description="CFTC contract market code quotes."
    )
    cftc_market_code_quotes: str | None = Field(
        default=None, description="CFTC market code quotes."
    )
    cftc_commodity_code_quotes: str | None = Field(
        default=None, description="CFTC commodity code quotes."
    )
    cftc_subgroup_code: str | None = Field(
        default=None, description="CFTC subgroup code."
    )
    commodity: str | None = Field(default=None, description="Commodity.")
    commodity_group: str | None = Field(
        default=None, description="Commodity group name."
    )
    commodity_subgroup: str | None = Field(
        default=None, description="Commodity subgroup name."
    )
    futonly_or_combined: str | None = Field(
        default=None, description="If the report is futures-only or combined."
    )
    contract_units: str | None = Field(default=None, description="Contract units.")
