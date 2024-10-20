"""DeFiLlama Helpers Module."""

from typing import Any, Dict

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request


async def response_callback(response, _):
    """Use callback for make_request."""
    data = await response.json()
    if isinstance(data, dict) and "message" in data:
        raise OpenBBError(f"DeFiLlama Error Message -> {data['message']}")
    if isinstance(data, dict) and data.get("coins") == {}:
        raise EmptyDataError("No data found")
    return data


async def get_data(url: str, **kwargs: Any) -> Dict[str, Any]:
    """Get data from DeFiLlama coins endpoint."""
    # pylint: disable=import-outside-toplevel
    return await amake_request(url, response_callback=response_callback, **kwargs)
