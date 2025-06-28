"""FOMC document and release utilities."""

from functools import lru_cache
from typing import Literal, Optional

FomcDocumentType = Literal[
    "all",
    "monetary_policy",
    "minutes",
    "projections",
    "materials",
    "press_release",
    "press_conference",
    "agenda",
    "transcript",
    "speaker_key",
    "beige_book",
    "teal_book",
    "green_book",
    "blue_book",
    "red_book",
]


@lru_cache(maxsize=1)
def load_historical_fomc_documents() -> list:
    """Load historical FOMC documents map from the static assets."""
    # pylint: disable=import-outside-toplevel
    import json

    historical_docs: list = []
    historical_docs_path = __file__.replace(
        "utils/fomc_documents.py", "assets/historical_releases.json"
    )
    with open(historical_docs_path, encoding="utf-8") as file:
        historical_docs = json.load(file)

    return historical_docs


@lru_cache(maxsize=64)
def get_current_fomc_documents(url: Optional[str] = None) -> list:
    """
    Get the current FOMC documents from https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm.

    Returns
    -------
    list
        A list of dictionaries containing the FOMC documents.
        Each dictionary contains the following:
        - date: str
            The date of the document, formatted as YYYY-MM-DD.
        - doc_type: str
            The type of the document.
        - doc_format: str
            The format of the document.
        - url: str
            The URL of the document
    """
    # pylint: disable=import-outside-toplevel
    import re  # noqa
    from bs4 import BeautifulSoup
    from openbb_core.provider.utils.helpers import make_request

    data_releases: list = []
    if url is None:
        beige_books = get_beige_books()

        if beige_books:
            data_releases.extend(beige_books)

    url = (
        url
        if url is not None
        else "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    )
    response = make_request(url, method="GET")
    soup = BeautifulSoup(response.content, "html.parser")

    for link in soup.find_all("a"):
        url = link.get("href", "")

        if "/newsevents/pressreleases" in url:
            continue

        file_url = (
            f"https://www.federalreserve.gov{url}"
            if not url.startswith("https://www.federalreserve.gov")
            else url
        )
        date = file_url.split("/")[
            -2 if file_url.endswith("/default.htm") else -1
        ].split(".")[0]
        date_match = re.search(r"(\d{4})(\d{2})(\d{2})", date)
        if date_match:
            new_date = (
                f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            )
            file_type = ""
            if "beige" in url.lower():
                file_type = "beige_book"
            if "files" in url and "monetary" in date:
                file_type = "monetary_policy"
            if "fomcproj" in date:
                file_type = "projections"
            if "fomcminutes" in date:
                file_type = "minutes"
            if "fomcpresconf" in date:
                file_type = "press_conference"

            file_format = file_url.rsplit(".", maxsplit=1)[-1]
            data_releases.append(
                {
                    "date": new_date,
                    "doc_type": file_type,
                    "doc_format": file_format,
                    "url": file_url,
                }
            )

    data_releases = sorted(data_releases, key=lambda x: x["date"], reverse=True)

    return data_releases


@lru_cache(maxsize=32)
def get_fomc_documents_by_year(
    year: Optional[int] = None,
    document_type: Optional[FomcDocumentType] = None,
    pdf_only: bool = False,
) -> list[dict]:
    """
    Get a list of FOMC documents by year and document type.

    Parameters
    ----------
    year : Optional[int]
        The year of the FOMC documents to retrieve. If None, all years since 1959 are returned.
    document_type : Optional[FomcDocumentType]
        The type of FOMC document to retrieve. If None, all document types are returned.
        Valid document types are:
        - all
        - monetary_policy
        - minutes
        - projections
        - materials
        - press_release
        - press_conference
        - conference_call
        - agenda
        - transcript
        - speaker_key
        - beige_book
        - teal_book
        - green_book
        - blue_book
        - red_book
    pdf_only : bool
        Whether to return with only the PDF documents. Default is False.

    Returns
    -------
    list[dict]
        A list of dictionaries mapping FOMC documents to URLs.
        Each dictionary contains the following:
        - date: str
            The date of the document, formatted as YYYY-MM-DD.
        - doc_type: str
            The type of the document.
        - doc_format: str
            The format of the document.
        - url: str
            The URL of the document
    """
    filtered_docs: list[dict] = []
    choice_types = list(getattr(FomcDocumentType, "__args__", ()))

    if year and year < 1959:
        raise ValueError("Year must be from 1959.")

    if year and isinstance(year, str):
        year = int(year) if year.isdigit() else 0
        if year == 0:
            raise ValueError("Year must be an integer.")

    if not document_type:
        document_type = "all"

    if document_type not in choice_types:
        raise ValueError(
            f"Invalid document type. Must be one of: {', '.join(choice_types)}"
        )

    if year:
        docs = (
            get_current_fomc_documents()
            if year > 2024
            else load_historical_fomc_documents()
        )
    else:
        current_docs = get_current_fomc_documents()
        historical_docs = load_historical_fomc_documents()
        docs = current_docs + historical_docs

    for doc in docs:
        doc_year = int(doc["date"].split("-")[0])
        if year and doc_year != year:
            continue
        if pdf_only is True and doc["doc_format"] != "pdf":
            continue
        if document_type in ("all", doc["doc_type"]):
            filtered_docs.append(doc)

    return sorted(filtered_docs, key=lambda x: x["date"], reverse=True)


def get_beige_books(year: Optional[int] = None) -> list[dict]:
    """
    Get a list of Beige Books by year.

    Parameters
    ----------
    year : Optional[int]
        The year of the Beige Books to retrieve. If None, all years since 1959 are returned.

    Returns
    -------
    list[dict]
        A list of dictionaries mapping Beige Books to URLs.
        Each dictionary contains the following:
        - date: str
            The date of the document, formatted as YYYY-MM-DD.
        - doc_type: str
            The type of the document (always "beige_book").
        - doc_format: str
            The format of the document.
        - url: str
            The URL of the document.
    """
    url = (
        "https://www.federalreserve.gov/monetarypolicy/publications/beige-book-default.htm"
        if year is None
        else f"https://www.federalreserve.gov/monetarypolicy/beigebook{year}.htm"
    )
    return get_current_fomc_documents(url=url)
