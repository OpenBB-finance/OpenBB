"""Document chunking utilities."""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import settings


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Get configured text splitter for financial documents."""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=[
            "\n\n",
            "\n",
            ". ",
            ", ",
            " ",
            "",
        ],
    )


def split_document(
    text: str,
    metadata: dict,
) -> tuple[list[str], list[dict]]:
    """Split a document into chunks with metadata.

    Returns:
        Tuple of (chunks, metadatas) where each metadata dict
        includes the original metadata plus a chunk_index field.
    """
    splitter = get_text_splitter()
    chunks = splitter.split_text(text)

    metadatas = [{**metadata, "chunk_index": i} for i in range(len(chunks))]

    return chunks, metadatas
