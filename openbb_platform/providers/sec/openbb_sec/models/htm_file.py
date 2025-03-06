"""SEC HTM/HTML File Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class SecHtmFileQueryParams(QueryParams):
    """SEC HTM File Query Parameters."""

    url: str = Field(
        default="",
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
        if not params.get("url"):
            raise OpenBBError(ValueError("Please enter a URL."))

        url = params.get("url", "")

        if (
            not url.startswith("http")
            or "sec.gov" not in url
            or (not url.endswith(".htm") and not url.endswith(".html"))
        ):
            raise OpenBBError(
                ValueError(
                    "Invalid URL. Please a SEC URL that directs specifically to a HTM or HTML file."
                )
            )
        return SecHtmFileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecHtmFileQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the SEC endpoint."""
        # pylint: disable=import-outside-toplevel
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
        # pylint: disable=import-outside-toplevel
        from bs4 import BeautifulSoup  # noqa

        if not data or not data.get("content"):
            raise OpenBBError("Failed to extract HTM file data.")

        content = data.pop("content", "")
        soup = BeautifulSoup(content, "html.parser").find("html")

        # Remove style elements that add background color to table rows
        for row in soup.find_all("tr"):
            if "background-color" in row.get("style", ""):
                del row["style"]
            for attr in ["class", "bgcolor"]:
                if attr in row.attrs:
                    del row[attr]

        return SecHtmFileData(content=str(soup), url=data["url"])
