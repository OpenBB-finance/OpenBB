"""SEC HTM/HTML File Model."""

from typing import Any, cast

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class SecHtmFileQueryParams(QueryParams):
    """SEC HTM File Query Parameters."""

    url: str | None = Field(
        default=None,
        description="URL for the SEC filing.",
    )
    use_cache: bool = Field(
        default=True,
        description="Cache the file for use later. Default is True.",
    )


class SecHtmFileData(Data):
    """SEC HTM File Data."""

    url: str = Field(
        description="URL of the downloaded file.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    content: str = Field(description="Raw content of the HTM/HTML file.")


class SecHtmFileFetcher(Fetcher[SecHtmFileQueryParams, SecHtmFileData]):
    """SEC HTM File Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecHtmFileQueryParams:
        """Transform the query."""
        from urllib.parse import urlparse

        url = params.get("url") or ""

        if not isinstance(url, str) or not url.strip():
            raise OpenBBError(ValueError("Please enter a URL."))

        parsed = urlparse(url.strip())

        if parsed.scheme not in ("http", "https"):
            raise OpenBBError(
                ValueError("Invalid URL supplied, must use http or https scheme.")
            )

        host = (parsed.hostname or "").lower()
        if host != "sec.gov" and not host.endswith(".sec.gov"):
            raise OpenBBError(
                ValueError(
                    "Invalid URL supplied, host must be sec.gov (e.g. https://www.sec.gov/...)."
                )
            )

        path = parsed.path or ""
        if not (path.endswith(".htm") or path.endswith(".html")):
            raise OpenBBError(
                ValueError(
                    "Invalid URL. Please a SEC URL that directs specifically to a HTM or HTML file."
                )
            )

        params["url"] = parsed.scheme + "://" + parsed.netloc + path
        return SecHtmFileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecHtmFileQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the SEC endpoint."""
        from openbb_sec.models.sec_filing import SecBaseFiling

        return {
            "url": query.url,
            "content": SecBaseFiling.download_file(query.url, False, query.use_cache),
        }

    @staticmethod
    def transform_data(
        query: SecHtmFileQueryParams, data: dict, **kwargs: Any
    ) -> SecHtmFileData:
        """Transform the data to the standard format."""
        from bs4 import BeautifulSoup, Tag  # noqa

        if not data or not data.get("content"):
            raise OpenBBError("Failed to extract HTM file data.")

        content = data.pop("content", "")
        soup = cast("Tag", BeautifulSoup(content, "html.parser").find("html"))

        # Remove style elements that add background color to table rows
        for row in soup.find_all("tr"):
            if "background-color" in cast("str", row.get("style", "")):
                del row["style"]
            for attr in ["class", "bgcolor"]:
                if attr in row.attrs:
                    del row[attr]

        return SecHtmFileData(content=str(soup), url=data["url"])
