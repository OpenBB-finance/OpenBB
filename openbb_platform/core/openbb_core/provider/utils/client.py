"""Aiohttp client."""
# pylint: disable=protected-access
import random
import zlib
from typing import Any, Dict, Union

import aiohttp

FILTER_QUERY_PARAMS = [
    "apikey",
    "apiKey",
    "api_key",
    "token",
    "key",
    "auth_token",
    "access_token",
    "c",
]


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
        self, *args, raise_for_status: bool = False, **kwargs
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
        if raise_for_status and not response.ok:
            query = response.request_info.url.query.copy()

            for param in FILTER_QUERY_PARAMS:
                if param in query:
                    query[param] = "*****"

            url = response.request_info.url.with_query(query)
            raise aiohttp.ClientResponseError(
                aiohttp.RequestInfo(
                    url,
                    response.request_info.method,
                    response.request_info.headers,
                    url,
                ),
                response.history,
                status=response.status,
                message=response.reason,
                headers=response.headers,
            )

        encoding = response.headers.get("Content-Encoding", "")
        if encoding in ("gzip", "deflate") and not self.auto_decompress:
            response_body = await response.read()
            wbits = 16 + zlib.MAX_WBITS if encoding == "gzip" else -zlib.MAX_WBITS
            response._body = zlib.decompress(
                response_body, wbits
            )  # pylint: disable=protected-access

        return response

    async def get(self, url: str, **kwargs) -> ClientResponse:
        """Send GET request."""
        return await self.request("GET", url, **kwargs)

    async def get_json(self, url: str, **kwargs) -> Union[dict, list]:
        """Send GET request and return json."""
        response = await self.request("GET", url, **kwargs)
        return await response.json()
