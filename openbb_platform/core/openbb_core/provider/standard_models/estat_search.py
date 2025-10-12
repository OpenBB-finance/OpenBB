"""e-Stat Search Model."""

from datetime import date as dateType
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class SearchQueryParams(QueryParams):
    """e-Stat Search Query Params."""

    query: Optional[str] = Field(
        default=None,
        description="Search keyword(s) for datasets. If not provided, returns all available datasets.",
    )


class SearchData(Data):
    """e-Stat Search Data."""

    dataset_id: str = Field(
        description="Statistical dataset ID (e.g., '0003433219'). Use this with estat_series() to fetch data."
    )
    title: Optional[str] = Field(
        default=None,
        description="Dataset title in English (when available) or Japanese.",
    )
    stats_code: Optional[str] = Field(
        default=None,
        description="Statistical survey code (e.g., '00200521').",
    )
    gov_org: Optional[str] = Field(
        default=None,
        description="Government organization responsible for the dataset.",
    )
    statistics_name: Optional[str] = Field(
        default=None,
        description="Name of the statistical survey or collection.",
    )
    survey_date: Optional[dateType] = Field(
        default=None,
        description="Survey or data collection date.",
    )
    open_date: Optional[dateType] = Field(
        default=None,
        description="Date the dataset was made publicly available.",
    )
    small_area: Optional[str] = Field(
        default=None,
        description="Whether dataset includes small area statistics (0=No, 1=Yes).",
    )
