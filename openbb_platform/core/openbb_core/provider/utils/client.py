"""Aiohttp client."""

# pylint: disable=protected-access,invalid-overridden-method
import asyncio
import random
import warnings
from typing import Any, Dict, Type, Union

import aiohttp
from multidict import CIMultiDict, CIMultiDictProxy, MultiDict

FILTER_QUERY_REGEX = r".*key.*|.*token.*|.*auth.*|(c$)"


def obfuscate(params: Union[CIMultiDict[str], MultiDict[str]]) -> Dict[str, Any]:
    """Obfuscate sensitive information."""
    # pylint: disable=import-outside-toplevel
    import re

    return {
        param: "********" if re.match(FILTER_QUERY_REGEX, param, re.IGNORECASE) else val
        for param, val in params.items()
    }


def get_user_agent() -> str:
    """Get a not very random user agent."""
    user_agent_strings = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:84.0) Gecko/20100101 Firefox/84.0",
    ]

    return random.choice(user_agent_strings)  # nosec # noqa: S311


class ClientResponse(aiohttp.ClientResponse):
    """Client response class."""

    def __init__(self, *args, **kwargs):
        """Initialize the response."""
        kwargs["request_info"] = self.obfuscate_request_info(kwargs["request_info"])
        super().__init__(*args, **kwargs)

    @classmethod
    def obfuscate_request_info(
        cls, request_info: aiohttp.RequestInfo
    ) -> aiohttp.RequestInfo:
        """Remove sensitive information from request info."""
        query = obfuscate(request_info.url.query.copy())
        headers = CIMultiDictProxy(CIMultiDict(obfuscate(request_info.headers.copy())))
        url = request_info.url.with_query(query)

        return aiohttp.RequestInfo(url, request_info.method, headers, url)

    async def json(self, **kwargs) -> Union[dict, list]:
        """Return the json response."""
        return await super().json(**kwargs)


class ClientSession(aiohttp.ClientSession):
    """Client session."""

    _response_class: Type[ClientResponse]
    _session: "ClientSession"

    def __init__(self, *args, **kwargs):
        """Initialize the session."""
        kwargs["connector"] = kwargs.get(
            "connector", aiohttp.TCPConnector(ttl_dns_cache=300)
        )
        kwargs["response_class"] = kwargs.get("response_class", ClientResponse)
        kwargs["auto_decompress"] = kwargs.get("auto_decompress", False)

        super().__init__(*args, **kwargs)

    # pylint: disable=unused-argument
    def __del__(self, _warnings: Any = warnings) -> None:
        """Close the session."""
        if not self.closed:
            asyncio.create_task(self.close())

    async def get(self, url: str, **kwargs) -> ClientResponse:  # type: ignore
        """Send GET request."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> ClientResponse:  # type: ignore
        """Send POST request."""
        return await self.request("POST", url, **kwargs)

    async def get_json(self, url: str, **kwargs) -> Union[dict, list]:
        """Send GET request and return json."""
        response = await self.request("GET", url, **kwargs)
        return await response.json()

    async def get_one(self, url: str, **kwargs) -> Dict[str, Any]:
        """Send GET request and return first item in json if list."""
        response = await self.request("GET", url, **kwargs)
        data = await response.json()

        if isinstance(data, list):
            return data[0]

        return data

    async def request(  # type: ignore
        self, *args, raise_for_status: bool = False, **kwargs
    ) -> ClientResponse:
        """Send request."""
        # pylint: disable=import-outside-toplevel
        import zlib

        kwargs["headers"] = kwargs.get(
            "headers",
            # Default headers, makes sure we accept gzip
            {
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            },
        )

        if kwargs["headers"].get("User-Agent", None) is None:
            kwargs["headers"]["User-Agent"] = get_user_agent()

        response = await super().request(*args, **kwargs)

        if raise_for_status:
            response.raise_for_status()

        encoding = response.headers.get("Content-Encoding", "")
        if encoding in ("gzip", "deflate") and not self.auto_decompress:
            response_body = await response.read()
            wbits = 16 + zlib.MAX_WBITS if encoding == "gzip" else -zlib.MAX_WBITS
            response._body = zlib.decompress(response_body, wbits)

        return response  # type: ignore
