"""BLS Search Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class SearchQueryParams(QueryParams):
    """BLS Search Query Params."""

    query: str = Field(
        default="",
        description="The search word(s). Use semi-colon to separate multiple queries as an & operator.",
    )


class SearchData(Data):
    """BLS Search Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    title: str | None = Field(default=None, description="The title of the series.")
    survey_name: str | None = Field(default=None, description="The name of the survey.")
