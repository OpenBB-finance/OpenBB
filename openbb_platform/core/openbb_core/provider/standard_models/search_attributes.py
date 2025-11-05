"""Search Attributes Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class SearchAttributesQueryParams(QueryParams):
    """Search Attributes Query."""

    query: str = Field(description="Query to search for.")
    limit: int | None = Field(default=1000, description=QUERY_DESCRIPTIONS.get("limit"))


class SearchAttributesData(Data):
    """Search Attributes Data."""

    id: str = Field(description="ID of the financial attribute.")
    name: str = Field(description="Name of the financial attribute.")
    tag: str = Field(description="Tag of the financial attribute.")
    statement_code: str = Field(description="Code of the financial statement.")
    statement_type: str | None = Field(
        default=None, description="Type of the financial statement."
    )
    parent_name: str | None = Field(
        default=None, description="Parent's name of the financial attribute."
    )
    sequence: int | None = Field(
        default=None, description="Sequence of the financial statement."
    )
    factor: str | None = Field(
        default=None, description="Unit of the financial attribute."
    )
    transaction: str | None = Field(
        default=None,
        description="Transaction type (credit/debit) of the financial attribute.",
    )
    type: str | None = Field(
        default=None, description="Type of the financial attribute."
    )
    unit: str | None = Field(
        default=None, description="Unit of the financial attribute."
    )
