"""TMX Index Documents Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

INDEX_FILE = "https://tmxinfoservices.com/files/indices/sptsx-indices.json"
DOCUMENTS = {"factsheet": "Factsheet", "methodology": "Methodology"}


class TmxIndexDocumentsQueryParams(QueryParams):
    """TMX Index Documents Query Params."""

    symbol: str | None = Field(
        default=None,
        description="The index symbol. Every published document when not supplied.",
    )
    document_type: Literal["all", "factsheet", "methodology"] = Field(
        default="all",
        description="The kind of document to list.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request."
        + " Index data is from a single JSON file, updated each day after close."
        + " It is cached for one day. To bypass, set to False.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """Convert the symbol to uppercase."""
        return v.upper() if v else None


class TmxIndexDocumentsData(Data):
    """TMX Index Documents Data."""

    symbol: str = Field(description="The index the document describes.")
    index_name: str | None = Field(
        default=None, description="The name of the index the document describes."
    )
    name: str = Field(description="The title of the document.")
    document_type: str = Field(
        description="The kind of document, factsheet or methodology."
    )
    url: str = Field(description="The URL of the PDF.")


class TmxIndexDocumentsFetcher(
    Fetcher[TmxIndexDocumentsQueryParams, list[TmxIndexDocumentsData]]
):
    """TMX Index Documents Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxIndexDocumentsQueryParams:
        """Transform the query."""
        return TmxIndexDocumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxIndexDocumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Read the published index file.

        Raises
        ------
        OpenBBError
            If the symbol is not one of the published indices.
        """
        from openbb_tmx.utils.helpers import get_data_from_url

        published = await get_data_from_url(INDEX_FILE, use_cache=query.use_cache)
        indices = (published or {}).get("indices") or {}

        if not indices:
            raise EmptyDataError

        if query.symbol and query.symbol not in indices:
            raise OpenBBError(f"Index {query.symbol} was not found. Check the symbol.")

        return {query.symbol: indices[query.symbol]} if query.symbol else indices

    @staticmethod
    def transform_data(
        query: TmxIndexDocumentsQueryParams, data: dict, **kwargs: Any
    ) -> list[TmxIndexDocumentsData]:
        """Pair every index with the documents it publishes.

        Raises
        ------
        EmptyDataError
            If no index in the selection publishes a document.
        """
        wanted = (
            list(DOCUMENTS) if query.document_type == "all" else [query.document_type]
        )
        results: list[TmxIndexDocumentsData] = []

        for symbol, index in data.items():
            name = index.get("name_en")

            for key in wanted:
                url = index.get(key)

                if not url:
                    continue

                results.append(
                    TmxIndexDocumentsData(
                        symbol=symbol,
                        index_name=name,
                        name=f"{name} - {DOCUMENTS[key]}" if name else DOCUMENTS[key],
                        document_type=key,
                        url=url,
                    )
                )

        if not results:
            raise EmptyDataError("No documents are published for this selection.")

        return results
