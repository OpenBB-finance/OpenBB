"""Cboe Index Documents Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

DocumentCategory = Literal[
    "Constituents",
    "Consultations",
    "Factsheet",
    "Governance",
    "Methodology",
    "Reference",
    "Regulatory Resources",
]

DocumentSymbol = Literal[
    "BXMU",
    "SPBFA",
    "SPBFQ",
    "SPBNQ",
    "SPBSA",
    "X2C",
    "X2CF",
    "X2CG",
    "X2CN",
]


class CboeIndexDocumentsQueryParams(QueryParams):
    """Cboe Index Documents Query.

    Source: https://www.cboe.com/
    """

    symbol: DocumentSymbol | None = Field(
        default=None,
        description="Restrict the catalog to documents for this index symbol."
        + " Documents that apply to every index are always included, and the"
        + " per-symbol factsheet when Cboe publishes one.",
    )
    category: DocumentCategory | None = Field(
        default=None,
        description="Restrict the catalog to one document category.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def validate_symbol(cls, v):
        """Upper-case the symbol and strip any index prefix."""
        return v.replace("^", "").upper() if isinstance(v, str) else v


class CboeIndexDocumentsData(Data):
    """Cboe Index Documents Data."""

    category: str = Field(description="The category of the document.")
    title: str = Field(description="The title of the document.")
    url: str = Field(description="The URL of the published PDF.")
    symbols: list[str] | None = Field(
        default=None,
        description="Index symbols the document is specific to."
        + " Empty for documents that apply to every index.",
    )


class CboeIndexDocumentsFetcher(
    Fetcher[
        CboeIndexDocumentsQueryParams,
        list[CboeIndexDocumentsData],
    ]
):
    """Transform the query, extract and transform the data from the Cboe endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CboeIndexDocumentsQueryParams:
        """Transform the query."""
        return CboeIndexDocumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeIndexDocumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the documents catalog, scoped to the symbol when given."""
        from openbb_cboe.utils.helpers import get_index_documents

        return await get_index_documents(query.symbol)

    @staticmethod
    def transform_data(
        query: CboeIndexDocumentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CboeIndexDocumentsData]:
        """Filter the catalog by category and validate.

        Raises
        ------
        EmptyDataError
            If no document matches the query.
        """
        documents = [
            doc
            for doc in data
            if not query.category or doc.get("category") == query.category
        ]

        if not documents:
            raise EmptyDataError("No documents match the query.")

        return [CboeIndexDocumentsData.model_validate(doc) for doc in documents]
