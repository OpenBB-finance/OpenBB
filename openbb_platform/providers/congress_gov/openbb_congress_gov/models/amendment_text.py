"""Congress Amendment Text Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class CongressAmendmentTextQueryParams(QueryParams):
    """Congress Amendment Text Query."""

    __json_schema_extra__ = {
        "urls": {
            "multiple_items_allowed": True,
        }
    }
    urls: str | list[str] | dict[str, list[str]] = Field(
        description="List of direct amendment document URLs to download.",
        kw_only=True,
    )


class CongressAmendmentTextData(Data):
    """Congress Amendment Text Data."""

    error_type: str | None = Field(
        default=None,
        description="Error type if any error occurs during the download.",
    )
    content: str = Field(
        description="Base64-encoded PDF document or plain text content.",
    )
    filename: str | None = Field(
        default=None,
        description="The filename of the downloaded document.",
    )
    data_format: dict[str, str] | None = Field(
        default=None,
        description="Data format information, including data type and filename.",
    )


class CongressAmendmentTextFetcher(
    Fetcher[CongressAmendmentTextQueryParams, list[CongressAmendmentTextData]]
):
    """Congress Amendment Text Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CongressAmendmentTextQueryParams:
        """Transform the query parameters."""
        return CongressAmendmentTextQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CongressAmendmentTextQueryParams,
        credentials: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list:
        """Extract data from the query."""
        # pylint: disable=import-outside-toplevel
        import base64  # noqa
        from io import BytesIO
        from openbb_core.provider.utils.helpers import make_request

        urls = (
            query.urls.get("urls", [])
            if isinstance(query.urls, dict)
            else (query.urls if isinstance(query.urls, list) else query.urls.split(","))
        )
        results: list = []

        for url in urls:
            filename = url.split("/")[-1]

            if "congress.gov" not in url.strip():
                results.append(
                    {
                        "error_type": "invalid_url",
                        "content": f"Invalid URL: {url}. Must be a valid Congress.gov API URL.",
                        "filename": filename,
                    }
                )
                continue
            try:
                response = make_request(url)
                response.raise_for_status()
                datatype = filename.split(".")[-1].lower()

                if datatype == "pdf":
                    pdf_content = base64.b64encode(
                        BytesIO(response.content).read()
                    ).decode("utf-8")
                    results.append(
                        {
                            "content": pdf_content,
                            "data_format": {
                                "data_type": "pdf",
                                "filename": filename,
                            },
                        }
                    )
                else:
                    results.append(
                        {
                            "content": response.text,
                            "data_format": {
                                "data_type": "text",
                                "filename": filename,
                            },
                        }
                    )
            except Exception as exc:  # pylint: disable=broad-except
                results.append(
                    {
                        "error_type": "download_error",
                        "content": f"{exc.__class__.__name__}: {exc.args[0]}",
                        "filename": filename,
                    }
                )
                continue

        return results

    @staticmethod
    def transform_data(
        query: CongressAmendmentTextQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[CongressAmendmentTextData]:
        """Transform the extracted data into the desired format."""
        return [CongressAmendmentTextData(**item) for item in data]
