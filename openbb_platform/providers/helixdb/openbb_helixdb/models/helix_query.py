from typing import List, Optional, Dict, Any
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS, DATA_DESCRIPTIONS
from pydantic import Field

class HelixDBQueryQueryParams(QueryParams):
    """HelixDB Generic Query Parameters."""
    query: str = Field(description="The database query string.")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Optional parameters for the query.")

class HelixDBQueryData(Data):
    """HelixDB Generic Query Data."""
    # This model will likely need to be a list of dictionaries,
    # or a more structured model if the output is known.
    # For now, allowing any data.
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Results from the HelixDB query")
    # Example of a more specific field if we knew the structure:
    # some_specific_field: Optional[str] = Field(default=None, description="A specific field from HelixDB")
