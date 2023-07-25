"""Major Indices Constituents data model."""


from datetime import date
from typing import Literal, Optional, Union

from pydantic import Field

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.metadata import QUERY_DESCRIPTIONS


class MajorIndicesConstituentsQueryParams(QueryParams):
    """Major Indices Constituents query.

    Parameter
    ---------
    index : Literal['nasdaq', 'sp500', 'dowjones']
        The index for which we want to fetch the constituents. Default is 'dowjones'.
    """

    index: Literal["nasdaq", "sp500", "dowjones"] = Field(
        description=QUERY_DESCRIPTIONS.get("index", ""),
        default="dowjones",
    )


class MajorIndicesConstituentsData(Data):
    """Major Indices Constituents price data.

    Returns
    -------
    symbol : str
        The symbol of the constituent company in the index.
    name : str
        The name of the constituent company in the index.
    sector : str
        The sector the constituent company in the index belongs to.
    subSector : str
        The sub-sector the constituent company in the index belongs to.
    headQuarter : str
        The location of the headquarter of the constituent company in the index.
    dateFirstAdded : date
        The date the constituent company was added to the index.
    cik : int
        The Central Index Key of the constituent company in the index.
    founded : date
        The founding year of the constituent company in the index.
    """

    name: str
    sector: str
    subSector: Optional[str] = Field(alias="sub_sector")
    headQuarter: Optional[str] = Field(alias="headquarter")
    dateFirstAdded: Optional[Union[date, str]] = Field(alias="date_first_added")
    cik: int
    founded: Union[date, str]
