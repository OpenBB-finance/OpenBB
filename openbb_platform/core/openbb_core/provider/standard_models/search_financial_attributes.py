"""Search Financial Attributes Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class SearchFinancialAttributesQueryParams(QueryParams):
    """Search Financial Attributes Query."""

    query: str = Field(description="Query to search for.")
    limit: Optional[int] = Field(
        default=1000, description=QUERY_DESCRIPTIONS.get("limit")
    )


class SearchFinancialAttributesData(Data):
    """Search Financial Attributes Data."""

    id: str = Field(description="ID of the financial attribute.")
    name: str = Field(description="Name of the financial attribute.")
    tag: str = Field(description="Tag of the financial attribute.")
    statement_code: str = Field(description="Code of the financial statement.")
    statement_type: Optional[str] = Field(
        default=None, description="Type of the financial statement."
    )
    parent_name: Optional[str] = Field(
        default=None, description="Parent's name of the financial attribute."
    )
    sequence: Optional[int] = Field(
        default=None, description="Sequence of the financial statement."
    )
    factor: Optional[str] = Field(
        default=None, description="Unit of the financial attribute."
    )
    transaction: Optional[str] = Field(
        default=None,
        description="Transaction type (credit/debit) of the financial attribute.",
    )
    type: Optional[str] = Field(
        default=None, description="Type of the financial attribute."
    )
    unit: Optional[str] = Field(
        default=None, description="Unit of the financial attribute."
    )
