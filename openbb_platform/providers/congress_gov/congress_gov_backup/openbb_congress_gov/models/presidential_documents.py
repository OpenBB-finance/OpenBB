"""Presidential Documents Model."""

from datetime import date as dateType
from enum import Enum
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from pydantic import Field


class President(str, Enum):
    """President enumeration."""
    
    CLINTON = "william-j-clinton"
    BUSH = "george-w-bush"
    OBAMA = "barack-obama"
    TRUMP = "donald-trump"
    BIDEN = "joe-biden"


class DocumentType(str, Enum):
    """Document type enumeration."""
    
    DETERMINATION = "determination"
    EXECUTIVE_ORDER = "executive_order"
    MEMORANDUM = "memorandum"
    NOTICE = "notice"
    PROCLAMATION = "proclamation"
    PRESIDENTIAL_ORDER = "presidential_order"
    OTHER = "other"


class PresidentialDocumentsQueryParams(QueryParams):
    """Presidential Documents Query Parameters."""
    
    president: President = Field(
        default=President.BIDEN,
        description="The president to filter documents by."
    )
    document_types: Optional[str] = Field(
        default="executive_order",
        description="Comma-separated list of document types to filter by."
    )
    per_page: Optional[int] = Field(
        default=20,
        description=QUERY_DESCRIPTIONS.get("limit", "") + " Max is 100."
    )
    page: Optional[int] = Field(
        default=1,
        description="Page number of results to retrieve."
    )


class PresidentialDocumentsData(Data):
    """Presidential Documents Data."""
    
    title: Optional[str] = Field(
        default=None,
        description="Title of the document."
    )
    document_type: Optional[str] = Field(
        default=None,
        description="Type of the document."
    )
    document_number: Optional[str] = Field(
        default=None,
        description="Document number."
    )
    html_url: Optional[str] = Field(
        default=None,
        description="URL to the HTML version of the document."
    )
    pdf_url: Optional[str] = Field(
        default=None,
        description="URL to the PDF version of the document."
    )
    public_inspection_pdf_url: Optional[str] = Field(
        default=None,
        description="URL to the public inspection PDF."
    )
    publication_date: Optional[dateType] = Field(
        default=None,
        description="Date the document was published."
    )
    abstract: Optional[str] = Field(
        default=None,
        description="Abstract or summary of the document."
    )
    excerpts: Optional[str] = Field(
        default=None,
        description="Excerpts from the document."
    )


class PresidentialDocumentsFetcher(
    Fetcher[
        PresidentialDocumentsQueryParams,
        List[PresidentialDocumentsData],
    ]
):
    """Extract and transform data from the Federal Register API."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> PresidentialDocumentsQueryParams:
        """Transform the query params."""
        return PresidentialDocumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: PresidentialDocumentsQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data from the Federal Register API."""
        base_url = "https://www.federalregister.gov/api/v1/documents.json"
        
        # Split the document_types string into a list
        document_types_list = query.document_types.split(',')
        
        # Build conditions for document types
        document_type_params = [
            f"conditions[presidential_document_type][]={doc_type}"
            for doc_type in document_types_list
        ]
        
        # Construct the full URL with parameters
        params_list = [
            f"per_page={query.per_page}",
            f"page={query.page}",
            f"conditions[president][]={query.president.value}",
            "conditions[type][]=PRESDOCU",
            *document_type_params
        ]
        
        params_string = "&".join(params_list)
        url = f"{base_url}?{params_string}"
        
        response = await amake_request(url, **kwargs)
        
        if not response or not response.get("results"):
            raise EmptyDataError()
        
        return response["results"]

    @staticmethod
    def transform_data(
        query: PresidentialDocumentsQueryParams,
        data: List[Dict],
        **kwargs: Any
    ) -> List[PresidentialDocumentsData]:
        """Transform raw data into PresidentialDocumentsData models."""
        transformed_data = []
        
        for doc in data:
            transformed_doc = PresidentialDocumentsData(
                title=doc.get("title"),
                document_type=doc.get("type"),
                document_number=doc.get("document_number"),
                html_url=doc.get("html_url"),
                pdf_url=doc.get("pdf_url"),
                public_inspection_pdf_url=doc.get("public_inspection_pdf_url"),
                publication_date=doc.get("publication_date"),
                abstract=doc.get("abstract"),
                excerpts=doc.get("excerpts")
            )
            transformed_data.append(transformed_doc)
        
        return transformed_data 