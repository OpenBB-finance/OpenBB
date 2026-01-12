"""QVERISAI API Client."""

import os
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.helpers import amake_request


class QverisClient:
    """QVERISAI API Client for making requests to QVERISAI services."""

    BASE_URL = "https://qveris.ai/api/v1"
    TIMEOUT = 30  # seconds - increased from 5 to allow for longer tool executions

    def __init__(self, api_key: str | None = None):
        """Initialize QVERISAI client.

        Parameters
        ----------
        api_key : str | None
            QVERISAI API key. If not provided, will try to get from environment variable QVERIS_API_KEY.
        """
        self.api_key = api_key or os.getenv("QVERIS_API_KEY", "")
        if not self.api_key:
            raise OpenBBError(
                "QVERISAI API key is required. Set QVERIS_API_KEY environment variable or pass api_key parameter."
            )

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def execute_tool(
        self,
        tool_id: str,
        parameters: dict[str, Any] | None = None,
        search_id: str | None = None,
        session_id: str | None = None,
        max_response_size: int = 20480,
    ) -> dict[str, Any]:
        """Execute a QVERISAI tool.

        Parameters
        ----------
        tool_id : str
            The ID of the tool to execute.
        parameters : dict[str, Any] | None
            Parameters to pass to the tool.
        search_id : str | None
            Optional search ID from tool search.
        session_id : str | None
            Optional session ID for tracking.
        max_response_size : int
            Maximum response size in bytes. Default is 20480.

        Returns
        -------
        dict[str, Any]
            The execution result from QVERISAI.

        Raises
        ------
        OpenBBError
            If the API request fails or returns an error.
        """
        url = f"{self.BASE_URL}/tools/execute?tool_id={tool_id}"

        payload: dict[str, Any] = {
            "parameters": parameters or {},
            "max_response_size": max_response_size,
        }

        if search_id:
            payload["search_id"] = search_id
        if session_id:
            payload["session_id"] = session_id

        try:
            response = await amake_request(
                url=url,
                method="POST",
                headers=self._get_headers(),
                json=payload,
                timeout=self.TIMEOUT,
            )

            if isinstance(response, dict):
                if not response.get("success", False):
                    error_message = response.get("error_message", "Unknown error")
                    raise OpenBBError(f"QVERISAI API error: {error_message}")
                return response

            raise OpenBBError("Unexpected response format from QVERISAI API")

        except Exception as e:
            if isinstance(e, OpenBBError):
                raise
            raise OpenBBError(f"Failed to execute QVERISAI tool: {str(e)}") from e

    async def search_tools(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search for QVERISAI tools.

        Parameters
        ----------
        query : str
            Search query describing the tool's functionality.
        limit : int
            Maximum number of results to return. Default is 10.

        Returns
        -------
        dict[str, Any]
            Search result containing search_id and list of tools.
            Format: {"search_id": "...", "tools": [...]}

        Raises
        ------
        OpenBBError
            If the API request fails or returns an error.
        """
        url = f"{self.BASE_URL}/search"

        payload: dict[str, Any] = {
            "query": query,
            "limit": limit,
        }

        try:
            response = await amake_request(
                url=url,
                method="POST",
                headers=self._get_headers(),
                json=payload,
                timeout=self.TIMEOUT,
            )

            if isinstance(response, dict):
                # The API returns: {"search_id": "...", "total": N, "results": [...], "tools": [...]}
                # Normalize to always have "tools" key
                if "tools" not in response:
                    # Try to get tools from "results" field
                    if "results" in response:
                        response["tools"] = response.get("results", [])
                    elif "data" in response:
                        response["tools"] = response.get("data", [])
                    else:
                        response["tools"] = []
                return response

            # If response is a list, wrap it
            if isinstance(response, list):
                return {
                    "search_id": "",
                    "tools": response,
                }

            raise OpenBBError("Unexpected response format from QVERISAI API")

        except Exception as e:
            if isinstance(e, OpenBBError):
                raise
            raise OpenBBError(f"Failed to search QVERISAI tools: {str(e)}") from e


