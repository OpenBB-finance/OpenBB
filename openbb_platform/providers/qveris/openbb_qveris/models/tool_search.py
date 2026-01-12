"""QVERISAI Tool Search Model.

Note: According to QVERISAI documentation, tool search is typically done through
the MCP server's search_tools tool. This Fetcher provides a placeholder structure
for potential future REST API support or integration with MCP search functionality.
"""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class QverisToolSearchQueryParams(QueryParams):
    """QVERISAI Tool Search Query Parameters.

    Source: https://qveris.ai/
    """

    query: str = Field(
        description="Search query describing the tool's functionality.",
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results to return.",
    )


class QverisToolSearchData(Data):
    """QVERISAI Tool Search Data."""

    tool_id: str | None = Field(
        default=None,
        description="The ID of the found tool.",
    )
    tool_name: str | None = Field(
        default=None,
        description="The name of the tool.",
    )
    description: str | None = Field(
        default=None,
        description="Description of the tool.",
    )
    parameters: dict[str, Any] | None = Field(
        default=None,
        description="Parameters schema for the tool.",
    )


class QverisToolSearchFetcher(
    Fetcher[
        QverisToolSearchQueryParams,
        list[QverisToolSearchData],
    ]
):
    """QVERISAI Tool Search Fetcher.

    Note: Tool search is typically done through MCP server's search_tools.
    This Fetcher is a placeholder for future REST API support.
    """

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> QverisToolSearchQueryParams:
        """Transform the query parameters."""
        return QverisToolSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: QverisToolSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Extract data from QVERISAI API.

        Uses the /search endpoint to search for tools.
        """
        from openbb_qveris.utils.client import QverisClient
        from openbb_qveris.utils.helpers import get_api_key_from_credentials

        # Get API key
        api_key = get_api_key_from_credentials(credentials)
        if not api_key:
            import os
            api_key = os.getenv("QVERIS_API_KEY")

        if not api_key:
            from openbb_core.app.model.abstract.error import OpenBBError

            raise OpenBBError(
                "QVERISAI API key is required. Set QVERIS_API_KEY environment variable."
            )

        # Create client and search tools
        client = QverisClient(api_key=api_key)
        try:
            limit = kwargs.get("limit") or query.limit if hasattr(query, "limit") else 10
            result = await client.search_tools(query=query.query, limit=limit)
            
            # Extract tools from result
            # The API returns: {"search_id": "...", "total": N, "results": [...], "tools": [...]}
            tools = result.get("tools", [])
            if not tools:
                # Try "results" field
                tools = result.get("results", [])
            if not tools and "data" in result:
                tools = result.get("data", [])
            
            if isinstance(tools, list):
                return tools
            
            return []
        except Exception as e:
            from openbb_core.app.model.abstract.error import OpenBBError
            raise OpenBBError(f"Failed to search QVERISAI tools: {str(e)}") from e

    @staticmethod
    def transform_data(
        query: QverisToolSearchQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[QverisToolSearchData]:
        """Transform the data to the standard format."""
        if not data:
            return []

        results = []
        for item in data:
            # Handle different possible field names from API response
            tool_id = item.get("tool_id") or item.get("id")
            tool_name = item.get("tool_name") or item.get("name") or item.get("title")
            description = item.get("description") or item.get("desc")
            
            # Handle parameters - it might be a list or dict
            parameters_raw = item.get("parameters") or item.get("params") or item.get("params_schema")
            parameters: dict[str, Any] | None = None
            
            if parameters_raw:
                if isinstance(parameters_raw, dict):
                    parameters = parameters_raw
                elif isinstance(parameters_raw, list):
                    # Convert list of parameter definitions to a dict
                    # Format: [{"name": "param1", "type": "...", ...}, ...]
                    parameters = {}
                    for param_def in parameters_raw:
                        if isinstance(param_def, dict) and "name" in param_def:
                            param_name = param_def.get("name")
                            # Store the full parameter definition
                            parameters[param_name] = param_def
                else:
                    # If it's neither dict nor list, try to convert or set to None
                    parameters = None
            
            results.append(
                QverisToolSearchData(
                    tool_id=tool_id,
                    tool_name=tool_name,
                    description=description,
                    parameters=parameters,
                )
            )

        return results


