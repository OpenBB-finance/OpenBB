from typing import List, Optional, Dict, Any
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

class SupabaseQueryQueryParams(QueryParams):
    """Supabase Generic Query Parameters."""
    table_name: str = Field(description="The name of the table to query.")
    select_query: str = Field(default="*", description="The SELECT part of the query, e.g., '*', 'column1, column2'.")
    filters: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of filters, e.g., [{'column': 'id', 'operator': 'eq', 'value': 1}]")
    limit: Optional[int] = Field(default=None, description="Number of rows to return.")
    # Add other common SQL-like parameters as needed, e.g., order_by

class SupabaseQueryData(Data):
    """Supabase Generic Query Data."""
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Results from the Supabase query")
