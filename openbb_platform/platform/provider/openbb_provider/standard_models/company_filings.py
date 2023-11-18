"""Company Filings Standard Model."""


from datetime import date as dateType
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS

SEC_FORM_TYPES = Literal[
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


class CompanyFilingsQueryParams(QueryParams):
    """Company Filings Query."""

    symbol: Optional[str] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    limit: Optional[int] = Field(
        default=300, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None


class CompanyFilingsData(Data):
    """Company Filings Data."""

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + " In this case, it is the date of the filing."
    )
    type: str = Field(description="Type of document.")
    link: str = Field(description="URL to the document.")
