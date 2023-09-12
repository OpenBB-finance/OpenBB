"""SEC Filings data model."""


from datetime import datetime
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS

FORM_TYPES = Literal[
    "1",
    "1-A",
    "1-E",
    "1-K",
    "1-N",
    "1-SA",
    "1-U",
    "1-Z",
    "10",
    "10-D",
    "10-K",
    "10-M",
    "10-Q",
    "11-K",
    "12b-25",
    "13F",
    "13H",
    "144",
    "15",
    "15F",
    "17-H",
    "18",
    "18-K",
    "19b-4",
    "19b-4(e)",
    "19b-7",
    "2-E",
    "20-F",
    "24F-2",
    "25",
    "3",
    "4",
    "40-F",
    "5",
    "6-K",
    "7-M",
    "8-A",
    "8-K",
    "8-M",
    "9-M",
    "ABS-15G",
    "ABS-EE",
    "ABS DD-15E",
    "ADV",
    "ADV-E",
    "ADV-H",
    "ADV-NR",
    "ADV-W",
    "ATS",
    "ATS-N",
    "ATS-R",
    "BD",
    "BD-N",
    "BDW",
    "C",
    "CA-1",
    "CB",
    "CFPORTAL",
    "CRS",
    "CUSTODY",
    "D",
    "F-1",
    "F-10",
    "F-3",
    "F-4",
    "F-6",
    "F-7",
    "F-8",
    "F-80",
    "F-N",
    "F-X",
    "ID",
    "MA",
    "MA-I",
    "MA-NR",
    "MA-W",
    "MSD",
    "MSDW",
    "N-14",
    "N-17D-1",
    "N-17f-1",
    "N-17f-2",
    "N-18f-1",
    "N-1A",
    "N-2",
    "N-23c-3",
    "N-27D-1",
    "N-3",
    "N-4",
    "N-5",
    "N-54A",
    "N-54C",
    "N-6",
    "N-6EI-1",
    "N-6F",
    "N-8A",
    "N-8B-2",
    "N-8B-4",
    "N-8F",
    "N-CEN",
]


class SECFilingsQueryParams(QueryParams):
    """SEC Filings Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    type: Optional[FORM_TYPES] = Field(description="Type of the SEC filing form.")
    page: Optional[int] = Field(default=0, description="Page number of the results.")
    limit: Optional[int] = Field(
        default=100, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class SECFilingsData(Data):
    """SEC Filings Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    filling_date: datetime = Field(description="Filling date of the SEC filing.")
    accepted_date: datetime = Field(description="Accepted date of the SEC filing.")
    cik: str = Field(description="CIK of the SEC filing.")
    type: str = Field(description="Type of the SEC filing.")
    link: str = Field(description="Link of the SEC filing.")
    final_link: str = Field(description="Final link of the SEC filing.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
