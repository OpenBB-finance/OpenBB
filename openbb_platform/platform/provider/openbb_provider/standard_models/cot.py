"""Commitment of Traders Reports Standard Model."""

from datetime import date as dateType

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS


class COTQueryParams(QueryParams):
    """Commitment of Traders Reports Query."""

    id: str = Field(
        description="The series ID string for the report."
        + " Default report is Two-Year Treasury Note Futures.",
        default="042601",
    )


class COTData(Data):
    """Commitment of Traders Reports Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
