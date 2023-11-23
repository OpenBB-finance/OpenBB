"""Aiohttp client."""
# pylint: disable=protected-access
import random
import zlib
from typing import Any, Dict, Union

import aiohttp


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
        super().__init__(*args, **kwargs)

        self.auto_decompress = getattr(self._session, "auto_decompress", False)

    async def json(self, **kwargs) -> Union[dict, list]:
        """Read and decodes JSON response."""
        encoding = self.headers.get("Content-Encoding", "")
        if encoding in ("gzip", "deflate") and not self.auto_decompress:
            response_body = await self.read()
            wbits = 16 + zlib.MAX_WBITS if encoding == "gzip" else -zlib.MAX_WBITS
            self._body = zlib.decompress(response_body, wbits)

        return await super().json(**kwargs)

    async def get_one(self) -> Dict[str, Any]:
        """Return the first item in the response."""
        data = await self.json()
        if isinstance(data, list):
            return data[0]

        return data


class ClientSession(aiohttp.ClientSession):
    _response_class: ClientResponse
    _session: "ClientSession"

    def __init__(self, *args, **kwargs):
        kwargs["connector"] = kwargs.get(
            "connector", aiohttp.TCPConnector(ttl_dns_cache=300)
        )
        kwargs["response_class"] = kwargs.get("response_class", ClientResponse)
        kwargs["auto_decompress"] = kwargs.get("auto_decompress", False)

        super().__init__(*args, **kwargs)

    async def request(
        self, *args, raise_for_status: bool = True, **kwargs
    ) -> ClientResponse:
        """Send request."""
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

        return response

    async def get(self, url: str, **kwargs) -> ClientResponse:
        """Send GET request."""
        return await self.request("GET", url, **kwargs)

    async def get_json(self, url: str, **kwargs) -> Union[dict, list]:
        """Send GET request and return json."""
        response = await self.get(url, **kwargs)
        return await response.json()


aiohttp_client = ClientSession()
