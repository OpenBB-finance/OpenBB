"""QVERISAI Tool Execute Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_qveris.utils.client import QverisClient
from openbb_qveris.utils.helpers import get_api_key_from_credentials
from pydantic import Field


class QverisToolExecuteQueryParams(QueryParams):
    """QVERISAI Tool Execute Query Parameters.

    Source: https://qveris.ai/
    """

    tool_id: str = Field(description="The ID of the tool to execute.")
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters to pass to the tool.",
    )
    search_id: str | None = Field(
        default=None,
        description="Optional search ID from tool search.",
    )
    session_id: str | None = Field(
        default=None,
        description="Optional session ID for tracking.",
    )
    max_response_size: int = Field(
        default=20480,
        description="Maximum response size in bytes.",
    )


class QverisToolExecuteData(Data):
    """QVERISAI Tool Execute Data."""

    execution_id: str | None = Field(
        default=None,
        description="The execution ID from QVERISAI.",
    )
    result: dict[str, Any] = Field(
        default_factory=dict,
        description="The result data from the tool execution.",
    )
    success: bool = Field(
        default=False,
        description="Whether the execution was successful.",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if execution failed.",
    )
    elapsed_time_ms: int | None = Field(
        default=None,
        description="Elapsed time in milliseconds.",
    )


class QverisToolExecuteFetcher(
    Fetcher[
        QverisToolExecuteQueryParams,
        QverisToolExecuteData,
    ]
):
    """QVERISAI Tool Execute Fetcher.

    Execute a QVERISAI tool with specified parameters.
    """

    require_credentials = True

    @staticmethod
    def transform_query(params: dict[str, Any]) -> QverisToolExecuteQueryParams:
        """Transform the query parameters."""
        return QverisToolExecuteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: QverisToolExecuteQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Extract data from QVERISAI API."""
        # Get API key from credentials or environment
        api_key = get_api_key_from_credentials(credentials)
        if not api_key:
            import os

            api_key = os.getenv("QVERIS_API_KEY")
        if not api_key:
            from openbb_core.app.model.abstract.error import OpenBBError

            raise OpenBBError(
                "QVERISAI API key is required. Set QVERIS_API_KEY environment variable."
            )

        # Create client and execute tool
        client = QverisClient(api_key=api_key)
        response = await client.execute_tool(
            tool_id=query.tool_id,
            parameters=query.parameters,
            search_id=query.search_id,
            session_id=query.session_id,
            max_response_size=query.max_response_size,
        )

        return response

    @staticmethod
    def transform_data(
        query: QverisToolExecuteQueryParams,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> QverisToolExecuteData:
        """Transform the data to the standard format."""
        if not data:
            raise EmptyDataError("No data returned from QVERISAI API.")

        # Extract result data
        result_data = data.get("result", {})
        if isinstance(result_data, dict):
            # If result has a 'data' key, use that
            if "data" in result_data:
                result_data = result_data["data"]

        return QverisToolExecuteData(
            execution_id=data.get("execution_id"),
            result=result_data if isinstance(result_data, dict) else {"data": result_data},
            success=data.get("success", False),
            error_message=data.get("error_message"),
            elapsed_time_ms=data.get("elapsed_time_ms"),
        )


