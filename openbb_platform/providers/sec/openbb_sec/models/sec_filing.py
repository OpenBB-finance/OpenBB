"""SEC Filing Model."""

# pylint: disable=C0302,R0911,R0912,R0914,R0915,W0613

import contextlib
import re
from collections.abc import Callable, Iterator
from datetime import date as dateType
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, PrivateAttr, computed_field


class SecFilingQueryParams(QueryParams):
    """SEC Filing Query Parameters."""

    __json_schema_extra__ = {
        "url": {
            "x-widget_config": {
                "label": "Filing URL",
            }
        }
    }

    url: str = Field(
        description="URL for the SEC filing."
        + " The specific URL is not directly used or downloaded,"
        + " but is used to generate the base URL for the filing."
        + " e.g. https://www.sec.gov/Archives/edgar/data/317540/000031754024000045/coke-20240731.htm"
        + " and https://www.sec.gov/Archives/edgar/data/317540/000031754024000045/"
        + " are both valid URLs for the same filing.",
    )
    use_cache: bool = Field(
        default=True,
        description="Use cache for the index headers and cover page. Default is True.",
    )


class SecFilingData(Data):
    """SEC Filing Data."""

    # For Workspace, ConfigDict is used to enter the widget configuration at the "$.data" level.
    # Here, we are using a subset of the data - the document URLs with direct links - to avoid nested data.
    # This creates column definitions for the target output while preserving the structure of the model.
    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "dataKey": "results.document_urls",
                "table": {
                    "columnsDefs": [
                        {
                            "field": "sequence",
                            "headerName": "Sequence",
                            "headerTooltip": "The sequence of the document.",
                            "type": "number",
                            "pinned": "left",
                            "maxWidth": 105,
                        },
                        {
                            "field": "type",
                            "headerName": "Document Type",
                            "headerTooltip": "The type of document.",
                            "type": "text",
                            "maxWidth": 150,
                        },
                        {
                            "field": "filename",
                            "headerName": "Filename",
                            "headerTooltip": "The filename of the document.",
                            "type": "text",
                            "maxWidth": 250,
                        },
                        {
                            "field": "content_description",
                            "headerName": "Description",
                            "headerTooltip": "Description of the document.",
                            "type": "text",
                            "minWidth": 600,
                        },
                        {
                            "field": "url",
                            "headerName": "URL",
                            "headerTooltip": "The URL of the document.",
                            "type": "text",
                            "maxWidth": 75,
                        },
                    ],
                },
            }
        }
    )

    base_url: str = Field(
        title="Base URL",
        description="Base URL of the filing.",
        json_schema_extra={
            "x-widget_config": {
                "exclude": True
            }  # Tells the widget factory to exclude this field. Has no effect on endpoint.
        },
    )
    name: str = Field(
        title="Entity Name",
        description="Name of the entity filing.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    cik: str = Field(
        title="CIK",
        description="Central Index Key.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    trading_symbols: list | None = Field(
        default=None,
        title="Trading Symbols",
        description="Trading symbols, if available.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    sic: str = Field(
        title="SIC",
        description="Standard Industrial Classification.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    sic_organization_name: str = Field(
        title="SIC Organization",
        description="SIC Organization Name.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    filing_date: dateType = Field(
        title="Filing Date",
        description="Filing date.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    period_ending: dateType | None = Field(
        default=None,
        title="Period Ending",
        description="Date of the ending period for the filing, if available.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    fiscal_year_end: str | None = Field(
        default=None,
        title="Fiscal Year End",
        description="Fiscal year end of the entity, if available. Format: MM-DD",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    document_type: str = Field(
        title="Document Type",
        description="Specific SEC filing type.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    has_cover_page: bool = Field(
        title="Has Cover Page",
        description="True if the filing has a cover page.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    description: str | None = Field(
        default=None,
        title="Content Description",
        description="Description of attached content, mostly applicable to 8-K filings.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    cover_page: dict | None = Field(
        default=None,
        title="Cover Page",
        description="Cover page information, if available.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    document_urls: list = Field(
        title="Document URLs",
        description="List of files associated with the filing.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )


class LazyDict(dict):
    """A dict-like class that provides keys/labels upfront but lazy-loads values.

    This allows inspection of available items without loading all content.
    Values are loaded on first access and cached.
    """

    def __init__(self, keys_labels: dict, loader: Callable[[str], Any]):
        """Initialize with a dict of {key: label} and a loader function.

        Args:
            keys_labels: Dict mapping keys to their labels/descriptions
            loader: Function that takes a key and returns the full value
        """
        super().__init__()
        self._keys_labels = keys_labels
        self._loader = loader
        self._loaded: dict = {}

    def keys(self):
        """Return all available keys without loading values."""
        return self._keys_labels.keys()

    def labels(self) -> dict:
        """Return mapping of keys to their labels."""
        return self._keys_labels.copy()

    def items(self):
        """Iterate over key-value pairs, loading each value."""
        for key in self._keys_labels:
            yield key, self[key]

    def values(self):
        """Iterate over values, loading each one."""
        for key in self._keys_labels:
            yield self[key]

    def __iter__(self) -> Iterator:
        """Iterate over keys."""
        return iter(self._keys_labels)

    def __len__(self) -> int:
        """Return number of items."""
        return len(self._keys_labels)

    def __contains__(self, key) -> bool:
        """Check if key exists."""
        return key in self._keys_labels

    def __getitem__(self, key):
        """Get item, loading if necessary."""
        if key not in self._keys_labels:
            raise KeyError(key)
        if key not in self._loaded:
            self._loaded[key] = self._loader(key)
        return self._loaded[key]

    def get(self, key, default=None):
        """Get item with default."""
        if key not in self._keys_labels:
            return default
        return self[key]

    def copy(self) -> dict:
        """Return a plain dict with all items materialized."""
        return dict(self.items())

    def __repr__(self) -> str:
        """Show keys without loading values."""
        return f"LazyDict({list(self._keys_labels.keys())})"

    def label(self, key: str) -> str | None:
        """Get the label for a specific key."""
        return self._keys_labels.get(key)


class Filing(Data):  # pylint: disable=too-many-instance-attributes
    """SEC Filing model.

    Handles generic SEC filing files and documents: URL parsing,
    index headers, cover pages, document/exhibit access, item extraction,
    and non-XBRL/8-K support.
    """

    _url: str = PrivateAttr(default="")
    _index_headers_url: str = PrivateAttr(default="")
    _index_headers_download: str = PrivateAttr(default="")
    _complete_submission_text: str = PrivateAttr(default="")
    _embedded_documents: dict = PrivateAttr(default_factory=dict)
    _document_urls: list = PrivateAttr(default_factory=list)
    _filing_date: str = PrivateAttr(default="")
    _period_ending: str = PrivateAttr(default="")
    _document_type: str = PrivateAttr(default="")
    _name: str = PrivateAttr(default="")
    _cik: str = PrivateAttr(default="")
    _sic: str = PrivateAttr(default="")
    _sic_organization_name: str | None = PrivateAttr(default="")
    _description: str | None = PrivateAttr(default=None)
    _cover_page_url: str | None = PrivateAttr(default=None)
    _fiscal_year_end: str = PrivateAttr(default="")
    _fiscal_year: str = PrivateAttr(default="")
    _fiscal_period: str = PrivateAttr(default="")
    _cover_page: dict = PrivateAttr(default_factory=dict)
    _shares_outstanding: dict = PrivateAttr(default_factory=dict)
    _trading_symbols: list = PrivateAttr(default_factory=list)
    _use_cache: bool = PrivateAttr(default=True)
    _items: dict = PrivateAttr(default_factory=dict)
    _non_xbrl_filing_initialized: bool = PrivateAttr(default=False)

    @computed_field(title="Base URL", description="Base URL of the filing.")  # type: ignore
    @property
    def base_url(self) -> str:
        """Base URL of the filing."""
        return self._url

    @computed_field(title="Entity Name", description="Name of the entity filing.")  # type: ignore
    @property
    def name(self) -> str:
        """Entity name."""
        return self._name

    @computed_field(title="CIK", description="Central Index Key.")  # type: ignore
    @property
    def cik(self) -> str:
        """Central Index Key."""
        return self._cik

    @computed_field(title="Trading Symbols", description="Trading symbols, if available.")  # type: ignore
    @property
    def trading_symbols(self) -> list | None:
        """Trading symbols, if available."""
        return self._trading_symbols

    @computed_field(title="SIC", description="Standard Industrial Classification.")  # type: ignore
    @property
    def sic(self) -> str:
        """Standard Industrial Classification."""
        return self._sic

    @computed_field(title="SIC Organization", description="SIC Organization Name.")  # type: ignore
    @property
    def sic_organization_name(self) -> str | None:
        """Standard Industrial Classification Organization Name."""
        return self._sic_organization_name

    @computed_field(title="Filing Date", description="Filing date.")  # type: ignore
    @property
    def filing_date(self) -> dateType:
        """Filing date."""
        return dateType.fromisoformat(self._filing_date)

    @computed_field(  # type: ignore
        title="Period Ending",
        description="Date of the ending period for the filing, if available.",
    )
    @property
    def period_ending(self) -> dateType | None:
        """Date of the ending period for the filing."""
        if self._period_ending:
            return dateType.fromisoformat(self._period_ending)
        return None

    @computed_field(  # type: ignore
        title="Fiscal Year End",
        description="Fiscal year end of the entity, if available. Format: MM-DD",
    )
    @property
    def fiscal_year_end(self) -> str | None:
        """Fiscal year end date of the entity."""
        return self._fiscal_year_end

    @computed_field(title="Document Type", description="Specific SEC filing type.")  # type: ignore
    @property
    def document_type(self) -> str:
        """Document type."""
        return self._document_type

    @computed_field(title="Has Cover Page", description="True if the filing has a cover page.")  # type: ignore
    @property
    def has_cover_page(self) -> bool:
        """True if the filing has a cover page."""
        return bool(self._cover_page_url)

    @computed_field(title="Cover Page", description="Cover page information, if available.")  # type: ignore
    @property
    def cover_page(self) -> dict | None:
        """Cover page information, if available."""
        return self._cover_page

    @computed_field(  # type: ignore
        title="Content Description",
        description="Description of attached content, mostly applicable to 8-K filings.",
    )
    @property
    def description(self) -> str | None:
        """Document description, if available."""
        return self._description

    @computed_field(title="Document URLs", description="List of files associated with the filing.")  # type: ignore
    @property
    def document_urls(self) -> list:
        """List of document URLs."""
        return self._document_urls

    @computed_field(title="Shares Outstanding", description="Shares outstanding by date, if available.")  # type: ignore
    @property
    def shares_outstanding(self) -> dict:
        """Shares outstanding by date, if available."""
        return self._shares_outstanding

    @computed_field(title="Is XBRL", description="Whether this filing contains XBRL data.")  # type: ignore
    @property
    def is_xbrl(self) -> bool:
        """Whether this filing contains XBRL data."""
        for doc in self._document_urls:
            filename = doc.get("filename", "").lower()

            if filename == "metalinks.json":
                return True

            if filename.endswith("_htm.xml") or filename.endswith("-xbrl.zip"):
                return True

        return False

    @computed_field(  # type: ignore
        title="Main Document URL",
        description="URL of the main filing document.",
    )
    @property
    def main_document_url(self) -> str | None:
        """URL of the main filing document."""
        return self.get_main_document_url()

    def _get_document_data(self) -> dict:
        """Get raw document data as dict of {filename: doc_info}."""
        docs_dict: dict = {}
        for doc in self._document_urls:
            filename = doc.get("filename", "")
            if filename:
                docs_dict[filename] = doc

        return docs_dict

    def _get_exhibit_data(self) -> dict:
        """Get raw exhibit data as dict of {type: doc_info}."""
        exhibits_dict: dict = {}
        excluded_extensions = (".xml", ".xsd", ".css", ".js", ".json")
        for doc in self._document_urls:
            filename = doc.get("filename", "").lower()

            if filename.endswith(excluded_extensions):
                continue

            if doc.get("type", "").startswith("EX-"):
                exhibits_dict[doc["type"]] = doc
            elif "EXHIBIT" in doc.get("description", "").upper():
                key = doc.get("type") or doc.get("description", "EXHIBIT")
                exhibits_dict[key] = doc

        return exhibits_dict

    def _get_items_info(self) -> dict:
        """Get filing items info as dict of {key: item_data}."""
        return self._items

    @property
    def documents(self) -> LazyDict:
        """Dictionary of documents keyed by their filename.

        Use .keys() to see available document filenames.
        Use .labels() to get a dict of {filename: description}.
        Access specific document with f.documents['filename.htm'].
        """
        doc_data = self._get_document_data()
        keys_labels = {
            k: v.get("description", v.get("filename", k)) for k, v in doc_data.items()
        }

        def load_document(key: str) -> dict:
            """Load document info (returns the doc dict)."""
            return doc_data[key]

        return LazyDict(keys_labels, load_document)

    @property
    def exhibits(self) -> LazyDict:
        """Lazy-loading dictionary of exhibits keyed by their type (e.g., 'EX-4.4', 'EX-22').

        Use .keys() to see available exhibits without loading content.
        Use .labels() to get a dict of {key: description}.
        Access specific exhibit with f.exhibits['EX-10.1'].
        """
        exhibit_data = self._get_exhibit_data()
        keys_labels = {
            k: v.get("description", v.get("filename", k))
            for k, v in exhibit_data.items()
        }

        def load_exhibit(key: str) -> dict:
            """Load exhibit info (returns the doc dict)."""
            return exhibit_data[key]

        return LazyDict(keys_labels, load_exhibit)

    @property
    def items(self) -> LazyDict:
        """Lazy-loading dictionary of filing items (Item 1, Item 7, etc.).

        Use .keys() to see available items without loading content.
        Use .labels() to get a dict of {key: name}.
        Access specific item with filing.items['item_7'].

        For 10-K filings: Item 1 (Business), Item 1A (Risk Factors), Item 7 (MD&A), etc.
        For 10-Q filings: Item 1 (Financial Statements), Item 2 (MD&A), etc.
        """
        items_info = self._get_items_info()
        keys_labels = {
            k: v.get("name", k) if isinstance(v, dict) else k
            for k, v in items_info.items()
        }

        def load_item(key: str) -> dict:
            """Load item data."""
            return items_info[key]

        return LazyDict(keys_labels, load_item)

    def get_embedded_document(self, identifier: str) -> str | None:
        """Get embedded document content by filename or document type.

        Parameters
        ----------
        identifier : str
            Either a filename or document type (e.g., 'EX-13', '10-K')

        Returns
        -------
        str or None
            The document content, or None if not found
        """
        if identifier in self._embedded_documents:
            return self._embedded_documents[identifier].get("content")

        identifier_upper = identifier.upper()
        for _key, doc in self._embedded_documents.items():
            if doc.get("type", "").upper() == identifier_upper:
                return doc.get("content")

        return None

    @staticmethod
    def _ensure_bytes(content) -> bytes:
        """Ensure content is bytes (encode str if needed for XML parsers)."""
        if isinstance(content, bytes):
            return content
        if isinstance(content, str):
            return content.encode("utf-8")
        raise TypeError(f"Expected str or bytes, got {type(content)}")

    @staticmethod
    def _clean_html_to_text(
        content, base_url: str = "", keep_tables: bool = True
    ) -> str:
        """Clean HTML content to markdown."""
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.html2markdown import html_to_markdown

        return html_to_markdown(content, base_url=base_url, keep_tables=keep_tables)

    def __init__(self, url: str = "", use_cache: bool = True):
        """Initialize the Filing class."""
        super().__init__()

        if not url:
            return  # Allow subclasses to handle initialization

        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import run_async
        from openbb_sec.utils.helpers import cik_map

        # Flexible URL parsing: handle trailing "/", full document URLs, or bare accession paths
        check_val: str = ""
        if url.endswith("/") or "." in url.split("/")[-1]:
            check_val = url.split("/")[-2]
        elif url[-1].isnumeric():
            check_val = url.split("/")[-1]

        if len(check_val) != 18:
            raise ValueError("Invalid SEC URL supplied, must be a filing URL.")

        new_url = url.split(check_val)[0] + check_val + "/"

        cik_check = new_url.split("/")[-3]
        new_url = new_url.replace(f"/{cik_check}/", f"/{cik_check.lstrip('0')}/")
        self._url = new_url
        self._use_cache = use_cache
        index_headers = (
            check_val[:-8]
            + "-"
            + check_val[-8:-6]
            + "-"
            + check_val[-6:]
            + "-index-headers.htm"
        )
        self._index_headers_url = self._url + index_headers
        self._download_index_headers()

        if self._document_urls:
            for doc in self._document_urls:
                if doc.get("url", "").endswith("R1.htm"):
                    self._cover_page_url = doc.get("url")
                    break

        if self.is_xbrl and self.has_cover_page and not self._cover_page:
            self._download_cover_page()

        if not self._trading_symbols:
            symbol = run_async(cik_map, self._cik)
            if symbol:
                self._trading_symbols = [symbol]

        # Post-init: non-XBRL and 8-K specific initialization
        if self.is_xbrl:
            if self._document_type and "8-K" in self._document_type.upper():
                self._initialize_8k_items()
        else:
            if not self._cover_page:
                self._build_non_xbrl_cover_page()
            self._initialize_non_xbrl_filing()

    @staticmethod
    async def _adownload_file(url, use_cache: bool = True):
        """Download a file asynchronously from a SEC URL."""
        # pylint: disable=import-outside-toplevel
        from aiohttp_client_cache import SQLiteBackend
        from aiohttp_client_cache.session import CachedSession
        from openbb_core.app.utils import get_user_cache_directory
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_sec.utils.definitions import SEC_HEADERS
        from openbb_sec.utils.helpers import sec_callback

        response: dict | list | str | None = None
        if use_cache is True:
            cache_dir = f"{get_user_cache_directory()}/http/sec_filings"
            async with CachedSession(cache=SQLiteBackend(cache_dir)) as session:
                try:
                    await session.delete_expired_responses()
                    response = await amake_request(
                        url,
                        headers=SEC_HEADERS,
                        session=session,
                        response_callback=sec_callback,
                        raise_for_status=True,
                    )  # type: ignore
                finally:
                    await session.close()
        else:
            response = await amake_request(
                url,
                headers=SEC_HEADERS,
                response_callback=sec_callback,
                raise_for_status=True,
            )  # type: ignore

        return response

    @staticmethod
    def download_file(url, read_html_table: bool = False, use_cache: bool = True):
        """Download a file from a SEC URL."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import run_async  # noqa
        from warnings import warn

        try:
            response = run_async(Filing._adownload_file, url, use_cache)

            # SEC may serve .json files with non-JSON content type,
            # so sec_callback returns text; parse it here.
            if isinstance(response, str) and url.endswith(".json"):
                import json

                response = json.loads(response)

            if read_html_table is True:
                if not url.endswith(".htm") and not url.endswith(".html"):
                    warn(f"File is not a HTML file: {url}")
                    return response

                return Filing.try_html_table(response)  # type: ignore

            return response

        except Exception as e:
            raise RuntimeError(f"Failed to download file: {e} -> {e.args}") from e

    @staticmethod
    def try_html_table(text: str, **kwargs) -> list:
        """Attempt to parse tables from a HTML string. All keyword arguments passed to `pandas.read_html`"""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from pandas import read_html

        try:
            return read_html(StringIO(text), **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to parse table: {e}") from e

    def _download_index_headers(
        self,
    ):
        """Download the index headers table."""
        # pylint: disable=import-outside-toplevel
        from bs4 import BeautifulSoup

        def document_to_dict(doc, accession_number: str = ""):
            """Convert the document section to a dictionary."""
            doc_dict: dict = {}
            type_match = re.search(r"<TYPE>(.*?)[\r\n]", doc)
            seq_match = re.search(r"<SEQUENCE>(.*?)[\r\n]", doc)
            filename_match = re.search(r"<FILENAME>(.*?)[\r\n]", doc)
            description_match = re.search(r"<DESCRIPTION>(.*?)[\r\n]", doc)

            # Extract the actual document content between <TEXT> tags
            text_match = re.search(r"<TEXT>(.*?)</TEXT>", doc, re.DOTALL)

            if type_match:
                doc_dict["type"] = type_match.group(1).strip()
            if seq_match:
                doc_dict["sequence"] = seq_match.group(1).strip()
            if filename_match:
                doc_dict["filename"] = filename_match.group(1).strip()
                doc_dict["url"] = self.base_url + doc_dict["filename"]
            elif accession_number and doc_dict.get("sequence") == "1":
                # Old filings may not have FILENAME - derive from accession number
                doc_dict["filename"] = f"{accession_number}-d1.html"
                doc_dict["url"] = self.base_url + doc_dict["filename"]
            if description_match:
                doc_dict["description"] = description_match.group(1).strip()
            if text_match:
                doc_dict["content"] = text_match.group(1).strip()

            return doc_dict

        def parse_header_text(text: str, accession_number: str = ""):
            """Parse the header text and extract document info."""
            # Store the complete submission text for later use
            self._complete_submission_text = text
            # Isolate each document by tag
            documents = re.findall(r"<DOCUMENT>.*?</DOCUMENT>", text, re.DOTALL)
            document_dicts = [
                document_to_dict(doc, accession_number) for doc in documents if doc
            ]

            if document_dicts:
                self._document_urls = document_dicts
                # Build embedded documents lookup by filename and type
                for doc in document_dicts:
                    if doc.get("filename"):
                        self._embedded_documents[doc["filename"]] = doc
                    if doc.get("type"):
                        # Also index by type (e.g., "EX-13", "10-K")
                        doc_type = doc["type"]
                        if doc_type not in self._embedded_documents:
                            self._embedded_documents[doc_type] = doc

            lines = text.split("\n")
            n_items = 0

            for line in lines:
                if ":" not in line:
                    continue

                value = ":".join(line.split(":")[1:]).strip()

                if n_items == 9:
                    break

                if "CONFORMED PERIOD OF REPORT" in line:
                    as_of_date = value
                    self._period_ending = (
                        as_of_date[:4] + "-" + as_of_date[4:6] + "-" + as_of_date[6:]
                    )
                elif "FILED AS OF DATE" in line:
                    filing_date = value
                    self._filing_date = (
                        filing_date[:4] + "-" + filing_date[4:6] + "-" + filing_date[6:]
                    )
                    n_items += 1
                elif "COMPANY CONFORMED NAME" in line:
                    self._name = value
                    n_items += 1
                elif "CONFORMED SUBMISSION TYPE" in line:
                    self._document_type = value
                    n_items += 1
                elif "CENTRAL INDEX KEY" in line:
                    self._cik = value
                    n_items += 1
                elif "STANDARD INDUSTRIAL CLASSIFICATION" in line:
                    self._sic = value
                    n_items += 1
                elif "ORGANIZATION NAME" in line:
                    self._sic_organization_name = value
                    n_items += 1
                elif "FISCAL YEAR END" in line:
                    fy = value
                    self._fiscal_year_end = fy[:2] + "-" + fy[2:]
                    n_items += 1
                elif "ITEM INFORMATION" in line:
                    info = value
                    self._description = (
                        self._description + "; " + info if self._description else info
                    )
                    n_items += 1

        try:
            text = ""
            accession_number = ""

            # Extract accession number from URL for old filing fallback
            url_parts = self._index_headers_url.split("/")[-1]
            if "-index-headers" in url_parts:
                accession_number = url_parts.replace("-index-headers.htm", "")

            # Try the modern index-headers.htm file first
            try:
                if not self._index_headers_download:
                    response = self.download_file(
                        self._index_headers_url, False, self._use_cache
                    )
                    self._index_headers_download = response  # type: ignore
                else:
                    response = self._index_headers_download

                if isinstance(response, bytes):
                    response = response.decode("utf-8", errors="ignore")
                soup = BeautifulSoup(response, "html.parser")  # type: ignore
                text = soup.find("pre").text  # type: ignore
            except RuntimeError as e:
                # Fall back to the complete submission .txt file for older filings
                if "404" in str(e):
                    txt_url = self.base_url + accession_number + ".txt"
                    response = self.download_file(txt_url, False, self._use_cache)
                    if isinstance(response, bytes):
                        response = response.decode("utf-8", errors="ignore")
                    text = response  # type: ignore
                else:
                    raise

            if text:
                parse_header_text(text, accession_number)  # type: ignore

        except Exception as e:
            raise RuntimeError(
                f"Failed to download and read the index headers table: {e}"
            ) from e

    @staticmethod
    def _multiplier_map(string) -> int:
        """Map a string to a multiplier."""
        if string.lower() == "millions":
            return 1000000
        if string.lower() == "hundreds of thousands":
            return 100000
        if string.lower() == "tens of thousands":
            return 10000
        if string.lower() == "thousands":
            return 1000
        if string.lower() == "hundreds":
            return 100
        if string.lower() == "tens":
            return 10
        return 1

    def _download_cover_page(
        self,
    ):
        """Download the cover page table."""
        # pylint: disable=import-outside-toplevel
        import unicodedata

        from pandas import MultiIndex, to_datetime

        def normalize_text(text):
            """Normalize unicode characters in text."""
            if not isinstance(text, str):
                return text
            text = unicodedata.normalize("NFKC", text)
            text = " ".join(text.split())
            return text

        try:
            response = self.download_file(self._cover_page_url, True, self._use_cache)
            if not response:
                raise RuntimeError("Failed to download cover page table")
            df = response[0]
            if isinstance(df.columns, MultiIndex):
                df = df.droplevel(0, axis=1)

            if df.empty or len(df) < 1:
                raise RuntimeError("Failed to read cover page table")

            fiscal_year = df[df.iloc[:, 0] == "Document Fiscal Year Focus"]
            fiscal_year_value: str = ""

            if not fiscal_year.empty:
                fiscal_year_value = fiscal_year.iloc[:, 1].values[0]

            if fiscal_year_value is not None:
                self._fiscal_year = fiscal_year_value

            fiscal_period = df[df.iloc[:, 0] == "Document Fiscal Period Focus"]
            fiscal_period_str: str = ""

            if not fiscal_period.empty:
                fiscal_period_str = fiscal_period.iloc[:, 1].values[0]

            if fiscal_period_str:
                self._fiscal_period = fiscal_period_str

            title = str(
                df.columns[0][0]
                if isinstance(df.columns, MultiIndex)
                else df.columns[0]
            )

            if title and "- shares" in title:
                shares_multiplier = title.rsplit(" shares in ", maxsplit=1)[-1]
                multiplier = self._multiplier_map(shares_multiplier)
                shares_outstanding = (
                    df[df.iloc[:, 0].str.contains("Shares Outstanding")]
                    .iloc[:, 2]
                    .values[0]
                )
                as_of_date = (
                    df.columns[2][1]
                    if isinstance(df.columns, MultiIndex)
                    else df.columns[2]
                )

                if as_of_date and shares_outstanding:
                    self._shares_outstanding = {
                        to_datetime(as_of_date).strftime("%Y-%m-%d"): int(  # type: ignore
                            shares_outstanding * multiplier
                        )
                    }

            if not df.empty:
                trading_symbols_df = df[
                    df.iloc[:, 0]
                    .astype(str)
                    .str.lower()
                    .isin(["trading symbol", "no trading symbol flag"])
                ]
                trading_symbols = (
                    trading_symbols_df.iloc[:, 1]
                    .str.strip()
                    .str.replace("true", "No Trading Symbol")
                    .tolist()
                )
                symbol_names = (
                    df[
                        df.iloc[:, 0].astype(str).str.strip()
                        == "Title of 12(b) Security"
                    ]
                    .iloc[:, 1]
                    .tolist()
                )
                exchange_names = (
                    df[
                        df.iloc[:, 0].astype(str).str.strip()
                        == "Security Exchange Name"
                    ]
                    .iloc[:, 1]
                    .fillna("No Exchange")
                    .tolist()
                )

                symbols_list: list = []
                if trading_symbols:
                    self._trading_symbols = sorted(
                        [
                            normalize_text(s)
                            for s in trading_symbols
                            if s and s != "No Trading Symbol"
                        ]
                    )
                    symbols_dict = dict(zip(symbol_names, trading_symbols))
                    exchanges_dict = dict(zip(symbol_names, exchange_names))
                    for k, v in symbols_dict.items():
                        symbols_list.append(
                            {
                                "Title": normalize_text(k),
                                "Symbol": normalize_text(v),
                                "Exchange": normalize_text(
                                    exchanges_dict.get(k, "No Exchange")
                                ),
                            }
                        )

                df.columns = [d[1] if isinstance(d, tuple) else d for d in df.columns]
                df = df.iloc[:, :2].dropna(how="any")
                df.columns = ["key", "value"]
                output = df.set_index("key").to_dict()["value"]

                # Normalize unicode characters in all values
                output = {
                    normalize_text(k): normalize_text(v) for k, v in output.items()
                }

                for drop_key in [
                    "Title of 12(b) Security",
                    "Trading Symbol",
                    "Security Exchange Name",
                    "No Trading Symbol Flag",
                ]:
                    output.pop(drop_key, None)

                if symbols_list:
                    output["12(b) Securities"] = symbols_list

                if not output.get("SIC") and self._sic:
                    output["SIC"] = self._sic
                    output["SIC Organization Name"] = self.sic_organization_name

                self._cover_page = output

        except IndexError:
            pass

        except Exception as e:
            raise RuntimeError(
                f"Failed to download and read the cover page table: {e}"
            ) from e

    def _build_non_xbrl_cover_page(self):  # noqa: PLR0912
        """Build cover page info for non-XBRL filings from submission text.

        Uses the complete submission text file which is already loaded,
        avoiding any additional HTTP requests.
        """
        # pylint: disable=import-outside-toplevel
        from bs4 import BeautifulSoup

        cover_page = {}

        # Start with data already parsed from SEC-HEADER
        if self._name:
            cover_page["Entity Registrant Name"] = self._name
        if self._cik:
            cover_page["Entity Central Index Key"] = self._cik
        if self._document_type:
            cover_page["Document Type"] = self._document_type
        if self._period_ending:
            cover_page["Document Period End Date"] = self._period_ending
        if self._filing_date:
            cover_page["Filed As Of Date"] = self._filing_date
        if self._fiscal_year_end:
            cover_page["Entity Fiscal Year End"] = self._fiscal_year_end
        if self._sic:
            cover_page["SIC"] = self._sic
        if self._sic_organization_name:
            cover_page["SIC Organization Name"] = self._sic_organization_name

        # Try to extract additional info from the main document content
        main_doc_content = self.get_embedded_document(
            "10-K"
        ) or self.get_embedded_document("10-Q")
        if not main_doc_content:
            main_doc_content = self.get_embedded_document(
                "10-K/A"
            ) or self.get_embedded_document("10-Q/A")

        if main_doc_content:
            try:
                soup = BeautifulSoup(main_doc_content, "html.parser")
                text = soup.get_text(separator=" ", strip=True)

                # Try to find state of incorporation
                state_match = re.search(
                    r"<B>([A-Z][A-Z\s]+?)(?:<BR>)?\s*</B>\s*</FONT>\s*<FONT[^>]*>\s*\(State (?:of|or) [Ii]ncorporation",
                    main_doc_content,
                    re.IGNORECASE | re.DOTALL,
                )
                if not state_match:
                    _us_states = (
                        r"NEW YORK|DELAWARE|CALIFORNIA|TEXAS|NEVADA|"
                        r"FLORIDA|ILLINOIS|PENNSYLVANIA|OHIO|GEORGIA|"
                        r"NEW JERSEY|VIRGINIA|MASSACHUSETTS|WASHINGTON|"
                        r"MARYLAND|COLORADO|ARIZONA|MICHIGAN|MINNESOTA|"
                        r"NORTH CAROLINA|MISSOURI|WISCONSIN|CONNECTICUT|"
                        r"OREGON|INDIANA|TENNESSEE|KENTUCKY|LOUISIANA|"
                        r"OKLAHOMA|ALABAMA|SOUTH CAROLINA|IOWA|UTAH|"
                        r"KANSAS|ARKANSAS|MISSISSIPPI|NEBRASKA|"
                        r"NEW MEXICO|HAWAII|IDAHO|NEW HAMPSHIRE|MAINE|"
                        r"MONTANA|RHODE ISLAND|SOUTH DAKOTA|"
                        r"NORTH DAKOTA|ALASKA|VERMONT|WYOMING|"
                        r"WEST VIRGINIA"
                    )
                    state_match = re.search(
                        rf"({_us_states})\s*\(?State (?:of|or) [Ii]ncorporation",
                        text,
                        re.IGNORECASE,
                    )
                if state_match:
                    state_name = state_match.group(1).strip().title()
                    if len(state_name) > 2 and len(state_name) < 30:
                        cover_page["Entity Incorporation State Country Code"] = (
                            state_name
                        )

                # Try to find registrant's telephone number
                phone_match = re.search(
                    r"<B>(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\s*</B>\s*</FONT>.*?\(Registrant'?s?\s*telephone",
                    main_doc_content,
                    re.IGNORECASE | re.DOTALL,
                )
                if not phone_match:
                    phone_match = re.search(
                        r"(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\s*\(?Registrant'?s?\s*telephone",
                        text,
                        re.IGNORECASE,
                    )
                if phone_match:
                    phone = phone_match.group(1).strip()
                    cover_page["Entity Phone"] = phone

                # Try to find shares outstanding from Section 12(b) table
                shares_table_match = re.search(
                    r"Voting shares outstanding.*?(\d{1,3}(?:,\d{3})+)",
                    main_doc_content,
                    re.IGNORECASE | re.DOTALL,
                )
                if shares_table_match:
                    shares_str = shares_table_match.group(1).replace(",", "")
                    with contextlib.suppress(ValueError):
                        cover_page["Entity Common Stock Shares Outstanding"] = int(
                            shares_str
                        )

                # Fallback: try simpler pattern
                if "Entity Common Stock Shares Outstanding" not in cover_page:
                    shares_match = re.search(
                        r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:shares|common shares)\s*(?:outstanding|issued)",
                        text,
                        re.IGNORECASE,
                    )
                    if shares_match:
                        shares_str = shares_match.group(1).replace(",", "")
                        with contextlib.suppress(ValueError):
                            cover_page["Entity Common Stock Shares Outstanding"] = int(
                                float(shares_str)
                            )

                # Try to find stock exchange from Section 12(b) table
                exchange_match = re.search(
                    r"Name of each exchange.*?on which registered.*?<TD[^>]*>.*?<FONT[^>]*>(?:<BR>)?\s*"
                    r"([A-Za-z\s]+(?:Stock\s+)?Exchange)",
                    main_doc_content,
                    re.IGNORECASE | re.DOTALL,
                )
                if not exchange_match:
                    exchange_match = re.search(
                        r"(New York Stock Exchange|NYSE|NASDAQ|Chicago Stock Exchange|Pacific Exchange)",
                        text,
                        re.IGNORECASE,
                    )
                if exchange_match:
                    exchange = exchange_match.group(1).strip()
                    exchange_lower = exchange.lower()
                    if "new york" in exchange_lower or exchange_lower == "nyse":
                        cover_page["Security Exchange Name"] = "NYSE"
                    elif "nasdaq" in exchange_lower:
                        cover_page["Security Exchange Name"] = "NASDAQ"
                    elif "chicago" in exchange_lower:
                        cover_page["Security Exchange Name"] = "NYSE"
                    else:
                        cover_page["Security Exchange Name"] = exchange.title()

                # Parse Section 12(b) securities table for all registered securities
                securities = []
                table_match = re.search(
                    r"Securities registered pursuant to Section[^<]*12\(b\)[^<]*</[^>]+>.*?<TABLE[^>]*>(.*?)</TABLE>",
                    main_doc_content,
                    re.IGNORECASE | re.DOTALL,
                )
                if table_match:
                    table_html = table_match.group(1)
                    rows = re.findall(
                        r"<TR[^>]*>(.*?)</TR>", table_html, re.IGNORECASE | re.DOTALL
                    )
                    for row in rows:
                        if "<TH" in row.upper():
                            continue
                        cells = re.findall(
                            r"<TD[^>]*>(.*?)</TD>", row, re.IGNORECASE | re.DOTALL
                        )
                        if len(cells) >= 3:

                            def clean_cell(cell):
                                cell = re.sub(r"<[^>]+>", " ", cell)
                                cell = re.sub(r"&nbsp;", " ", cell)
                                cell = re.sub(r"\s+", " ", cell)
                                return cell.strip()

                            title = clean_cell(cells[0])
                            shares = clean_cell(cells[2]) if len(cells) > 2 else ""
                            exchange_name = (
                                clean_cell(cells[-1])
                                if len(cells) > 2
                                else clean_cell(cells[1])
                            )

                            if not title and not exchange_name:
                                continue

                            if title:
                                security = {"title": title}
                                if shares and shares.replace(",", "").isdigit():
                                    security["shares_outstanding"] = int(  # type: ignore
                                        shares.replace(",", "")
                                    )
                                if exchange_name:
                                    security["exchange"] = exchange_name
                                securities.append(security)
                            elif exchange_name and securities:
                                if "additional_exchanges" not in securities[-1]:
                                    securities[-1]["additional_exchanges"] = []
                                securities[-1]["additional_exchanges"].append(
                                    exchange_name
                                )

                if securities:
                    cover_page["Securities Registered 12b"] = securities

                # Try to find trading symbol from front page
                symbol_match = re.search(
                    r"(?:Trading Symbol|Ticker Symbol)\s*[:\-]?\s*([A-Z]{1,5})",
                    text,
                    re.IGNORECASE,
                )
                if symbol_match:
                    symbol = symbol_match.group(1).strip()
                    cover_page["Trading Symbol"] = symbol
                    if symbol and symbol not in self._trading_symbols:
                        self._trading_symbols.append(symbol)

            except Exception:  # noqa: S110
                pass  # Don't fail if parsing additional info fails

        if cover_page:
            self._cover_page = cover_page
            if "Entity Common Stock Shares Outstanding" in cover_page:
                date_key = self._period_ending or "unknown"
                self._shares_outstanding = {
                    date_key: cover_page["Entity Common Stock Shares Outstanding"]
                }

    def _initialize_non_xbrl_filing(self):
        """Initialize non-XBRL filing-level data (items) from HTML.

        This parses filing items (Item 1, Item 7, etc.) which are common to all
        10-K/10-Q filings. Financial statement-specific parsing is handled by
        FinancialStatements._initialize_non_xbrl().
        """
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.non_xbrl_parser import extract_items

        if self._non_xbrl_filing_initialized:
            return

        try:
            # Try to get main document from embedded documents first (no HTTP request needed)
            main_doc = self.get_embedded_document("10-K") or self.get_embedded_document(
                "10-Q"
            )
            if not main_doc:
                main_doc = self.get_embedded_document(
                    "10-K/A"
                ) or self.get_embedded_document("10-Q/A")

            if main_doc:
                html_content = main_doc
            else:
                # Fall back to downloading
                main_url = self.main_document_url
                if not main_url:
                    self._non_xbrl_filing_initialized = True
                    return
                html_content = self.download_file(main_url)
                if isinstance(html_content, bytes):
                    html_content = html_content.decode("utf-8", errors="ignore")

            # Parse filing items (Item 1, Item 7, etc.)
            self._items = extract_items(html_content)  # type: ignore

            # If no items found in main doc, try exhibits (EX-13 often has the full content)
            if not self._items:
                self._parse_exhibit_items_filing(extract_items)

            self._non_xbrl_filing_initialized = True

        except Exception as e:
            import warnings

            warnings.warn(f"Failed to parse non-XBRL filing items: {e}")
            self._non_xbrl_filing_initialized = True

    def _initialize_8k_items(self):
        """Initialize 8-K filing items from HTML.

        8-K filings have items in HTML format even when the filing has XBRL data.
        The XBRL data only contains cover page information.
        """
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.html2markdown import html_to_markdown

        if self._non_xbrl_filing_initialized:
            return

        try:
            # Find the main 8-K document
            main_doc = self.get_embedded_document("8-K")
            if not main_doc:
                main_doc = self.get_embedded_document("8-K/A")

            if main_doc:
                html_content = main_doc
            else:
                # Fall back to downloading the main document
                main_url = self.main_document_url
                if not main_url:
                    self._non_xbrl_filing_initialized = True
                    return
                html_content = self.download_file(main_url)
                if isinstance(html_content, bytes):
                    html_content = html_content.decode("utf-8", errors="ignore")

            # Convert HTML to markdown
            markdown_content = html_to_markdown(html_content, base_url=self.base_url)  # type: ignore

            # Store as a single item with the full content
            self._items = {
                "full_document": {
                    "name": "8-K Filing",
                    "text": markdown_content,
                }
            }

            self._non_xbrl_filing_initialized = True

        except Exception as e:
            import warnings

            warnings.warn(f"Failed to parse 8-K filing items: {e}")
            self._non_xbrl_filing_initialized = True

    def _parse_exhibit_items_filing(self, extract_items):
        """Parse items (Item 1, Item 7, etc.) from exhibits.

        This is the Filing-level version that only extracts items.
        FinancialStatements has its own version that also extracts text blocks.
        """
        exhibit_priority = ["EX-13", "EX-13.1", "EX-13.2", "13"]

        # Try embedded documents first (no HTTP request needed)
        for exhibit_key in exhibit_priority:
            exhibit_html = self.get_embedded_document(exhibit_key)
            if exhibit_html:
                try:
                    items = extract_items(exhibit_html)
                    if items:
                        self._items = items
                        return
                except Exception:  # noqa: S112
                    continue

        # Fall back to downloading if not embedded
        exhibits = self.exhibits
        for exhibit_key in exhibit_priority:
            if exhibit_key in exhibits:
                try:
                    exhibit_data = exhibits[exhibit_key]
                    url = exhibit_data.get("url", "")
                    if not url:
                        continue
                    exhibit_html = self.download_file(url)
                    if isinstance(exhibit_html, bytes):
                        exhibit_html = exhibit_html.decode("utf-8", errors="ignore")
                    if exhibit_html:
                        items = extract_items(exhibit_html)
                        if items:
                            self._items = items
                            return
                except Exception:  # noqa: S112
                    continue

    def get_exhibit_text(self, exhibit: str | dict) -> str:
        """Get the text content of an exhibit.

        Args:
            exhibit: Either an exhibit key (e.g., 'EX-4.4', 'EX-22') or the exhibit dict.

        Returns:
            The text content of the exhibit.
        """
        if isinstance(exhibit, str):
            exhibit_data = self.exhibits.get(exhibit)
            if not exhibit_data:
                raise ValueError(
                    f"Exhibit '{exhibit}' not found. Available: {list(self.exhibits.keys())}"
                )
        else:
            exhibit_data = exhibit

        if not (url := exhibit_data.get("url")):
            return ""

        content = self.download_file(url)
        return self._clean_html_to_text(content, url)

    def get_document_text(self, document: str | dict) -> str:
        """Get the text content of a document, converted to markdown.

        Args:
            document: Either a document filename or the document dict.

        Returns:
            The text content of the document as markdown.
        """
        if isinstance(document, str):
            doc_data = self.documents.get(document)
            if not doc_data:
                raise ValueError(
                    f"Document '{document}' not found. Available: {list(self.documents.keys())}"
                )
        else:
            doc_data = document

        if not (url := doc_data.get("url")):
            return ""

        content = self.download_file(url)
        return self._clean_html_to_text(content, url)

    def get_main_document_url(self) -> str:
        """Get the URL of the main filing document (10-K, 10-Q, etc.)."""
        # Common main document types
        main_types = ["10-K", "10-Q", "8-K", "20-F", "40-F", "S-1", "10-K/A", "10-Q/A"]

        # Try to match by type first
        if self._document_urls:
            for doc in self._document_urls:
                if doc.get("type") in main_types:
                    return doc.get("url")

        # Fallback: Find first .htm file that is not an exhibit
        if self._document_urls:
            for doc in self._document_urls:
                if doc.get("filename", "").endswith(".htm") and not doc.get(
                    "type", ""
                ).startswith("EX-"):
                    return doc.get("url")

        return ""

    def get_main_document_content(self) -> str | None:
        """Get the content of the main filing document.

        Finds the main document entry in the filing's document list and
        checks whether it already has inline content (old SGML filings
        embed everything in the index). If so, returns it directly.
        Otherwise downloads from the document URL.

        Returns
        -------
        str or None
            The document content, or None if unavailable.
        """
        main_types = {"10-K", "10-Q", "8-K", "20-F", "40-F", "S-1", "10-K/A", "10-Q/A"}

        # Find the main document entry
        main_doc = None
        for doc in self._document_urls:
            if doc.get("type") in main_types:
                main_doc = doc
                break

        if main_doc is None:
            # Fallback: first non-exhibit .htm file
            for doc in self._document_urls:
                fname = doc.get("filename", "").lower()

                if fname.endswith((".htm", ".html")) and not doc.get(
                    "type", ""
                ).startswith("EX-"):
                    main_doc = doc
                    break

        if main_doc is None:
            return None

        # If the document entry already has inline content, use it directly.
        # Old SGML filings embed all content in the index file, so
        # the individual document URL may no longer exist on SEC servers.
        inline_content = main_doc.get("content")

        if inline_content:
            return inline_content

        # Otherwise download from URL
        url = main_doc.get("url") or self.get_main_document_url()

        if not url:
            return None

        content = self.download_file(url)

        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="ignore")

        return content  # type: ignore

    def get_filing_text(self) -> str:
        """Get the full text of the main filing document."""
        content = self.get_main_document_content()
        if not content:
            return ""

        url = self.get_main_document_url() or ""
        return self._clean_html_to_text(content, url)

    def extract_item(self, item: str) -> str:
        """Extract a specific item from the filing (e.g., 'Item 1A', 'Item 7').

        Dynamically discovers section anchors from the Table of Contents.
        For non-XBRL filings, uses pre-parsed items if available.
        """
        # pylint: disable=import-outside-toplevel
        import warnings  # noqa
        from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

        # Normalize item string (e.g., "Item 1A" -> "1A", "Item 7" -> "7")
        item_normal = item.strip().lower()

        if item_normal.startswith("item"):
            item_normal = item_normal.replace("item", "").strip()

        item_normal = item_normal.replace(".", "").replace(" ", "")

        # For non-XBRL filings, check if we have pre-parsed items
        if self._items:
            for key in [
                f"item_{item_normal}",
                f"item_{item_normal.upper()}",
                item_normal,
                item_normal.upper(),
            ]:
                if key in self._items:
                    return self._items[key].get("text", "")

        # Get the raw HTML to find anchors
        content = self.get_main_document_content()

        if not content:
            return ""

        main_doc_url = self.get_main_document_url() or ""
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        soup = BeautifulSoup(content, "lxml")
        item_normal = item.strip().lower()

        if item_normal.startswith("item"):
            item_normal = item_normal.replace("item", "").strip()

        item_normal = item_normal.replace(".", "").replace(" ", "")

        # Parse TOC to discover anchor IDs dynamically
        toc_items = {}

        for link in soup.find_all("a", href=True):
            href = link.get("href", "")

            if not href.startswith("#"):  # type: ignore
                continue

            anchor_id = href[1:]  # type: ignore
            link_text = link.get_text(strip=True).lower()

            item_match = re.search(r"item\s*(\d+[a-z]?)\.?", link_text)

            if not item_match:
                item_match = re.search(  # type: ignore
                    r"item[_\s]*(\d+)[_\s]*([a-z])?[_\s]", anchor_id, re.IGNORECASE  # type: ignore
                )
                if item_match:
                    found_item = item_match.group(1) + (item_match.group(2) or "")
                else:
                    continue
            else:
                found_item = item_match.group(1)

            found_item = found_item.replace("_", "").replace(" ", "").lower()

            if found_item not in toc_items:
                toc_items[found_item] = anchor_id

        # If we found the item in TOC, use anchor-based extraction
        if item_normal in toc_items:
            start_anchor_id = toc_items[item_normal]

            def sort_key(x):
                match = re.match(r"(\d+)([a-z]?)", x)
                if match:
                    num = int(match.group(1))
                    letter = match.group(2) or ""
                    return (num, letter)
                return (99, x)

            all_items = sorted(toc_items.keys(), key=sort_key)

            end_anchor_id = None
            try:
                idx = all_items.index(item_normal)
                if idx + 1 < len(all_items):
                    end_anchor_id = toc_items[all_items[idx + 1]]
            except (ValueError, IndexError):
                pass

            start_anchor = soup.find(id=start_anchor_id)
            end_anchor = soup.find(id=end_anchor_id) if end_anchor_id else None

            if start_anchor:
                html_str = str(soup)
                start_str = str(start_anchor)
                start_pos = html_str.find(start_str)

                if start_pos != -1:
                    if end_anchor:
                        end_str = str(end_anchor)
                        end_pos = html_str.find(end_str, start_pos)
                        if end_pos == -1:
                            end_pos = len(html_str)
                    else:
                        end_pos = len(html_str)

                    section_html = html_str[start_pos:end_pos]
                    result = self._clean_html_to_text(section_html, main_doc_url)

                    # For Item 7 (10-K) or Item 2 (10-Q) MD&A, if this is
                    # just a cross-reference stub, use the dedicated MD&A
                    # extractor which handles exhibit fallbacks, anchor
                    # following, standalone headings, etc.
                    if (
                        item_normal in ("7", "2")
                        and len(result) < 1000
                        and ("See the information" in result or "See MD&A" in result)
                    ):
                        return self._extract_mda_via_fetcher(content, main_doc_url)  # type: ignore

                    return result

        # Fall back to text-based extraction
        return self._extract_item_by_text(item)

    def _extract_mda_via_fetcher(self, filing_html: str, url: str) -> str:
        """Extract MD&A using SecManagementDiscussionAnalysisFetcher.transform_data.

        This leverages the comprehensive, dedicated MD&A extraction logic
        rather than duplicating it.
        """
        # pylint: disable=import-outside-toplevel
        from openbb_sec.models.management_discussion_analysis import (
            SecManagementDiscussionAnalysisFetcher,
            SecManagementDiscussionAnalysisQueryParams,
        )

        query = SecManagementDiscussionAnalysisQueryParams(
            symbol=self.cik or "",
        )
        data = {
            "symbol": self.name or "",
            "calendar_year": None,
            "calendar_period": None,
            "period_ending": self.period_ending,
            "report_type": self.document_type or "",
            "url": url,
            "content": filing_html,
        }
        try:
            mda_result = SecManagementDiscussionAnalysisFetcher.transform_data(
                query, data
            )
            if mda_result.content:
                return mda_result.content
        except Exception:  # noqa: S110
            pass
        return ""

    def _extract_item_by_text(self, item: str) -> str:
        """Fallback text-based item extraction."""
        text = self.get_filing_text()
        if not text:
            return ""

        item_normal = item.strip().lower()
        if not item_normal.startswith("item"):
            item_normal = f"item {item_normal}"
        item_num = item_normal.replace("item ", "").replace(".", "").upper()

        next_items_map = {
            "1": ["1A", "1B", "2"],
            "1A": ["1B", "1C", "2"],
            "1B": ["1C", "2"],
            "1C": ["2"],
            "7": ["7A", "8"],
            "7A": ["8"],
            "2": ["3", "4"],
            "3": ["4"],
            "4": ["1", "1A"],
        }
        next_items = next_items_map.get(item_num, [])

        patterns = [
            rf"\|\s*ITEM\s+{re.escape(item_num)}\.?\s*\|",
            rf"^Item\s+{re.escape(item_num)}\.?\s*[A-Z]",
            rf"^Item\s+{re.escape(item_num)}\.\s*$",
        ]

        start_pos = None
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
            for m in matches:
                line_end = text.find("\n", m.end())
                if line_end == -1:
                    line_end = len(text)
                rest_of_line = text[m.end() : line_end]

                if re.search(r"\|\s*\d+\s*\|\s*$", rest_of_line):
                    continue

                after = text[m.end() : m.end() + 200]
                if "See the information" in after[:100]:
                    continue
                start_pos = m.start()
                break
            if start_pos is not None:
                break

        if start_pos is None:
            return ""

        end_pos = len(text)

        for next_item in next_items:
            next_patterns = [
                rf"\|\s*ITEM\s+{re.escape(next_item)}\.?\s*\|",
                rf"^Item\s+{re.escape(next_item)}\.?\s*[A-Z]",
                rf"^Item\s+{re.escape(next_item)}\.\s*$",
            ]
            for next_pattern in next_patterns:
                next_matches = list(
                    re.finditer(
                        next_pattern,
                        text[start_pos + 500 :],
                        re.IGNORECASE | re.MULTILINE,
                    )
                )
                for nm in next_matches:
                    candidate = start_pos + 500 + nm.start()
                    end_pos = min(end_pos, candidate)
                    break

        return text[start_pos:end_pos].strip()

    def __repr__(self):
        """Return the string representation of the class."""
        repr_str = "SEC Filing(\n"

        for k, v in self.__class__.model_computed_fields.items():
            rt = v.return_type
            type_name = getattr(rt, "__name__", str(rt))
            repr_str += f"  {k} : {type_name} - {v.description}\n"

        repr_str += ")"

        return repr_str


class SecFilingFetcher(Fetcher[SecFilingQueryParams, SecFilingData]):
    """SEC Filing Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecFilingQueryParams:
        """Transform the query parameters."""
        return SecFilingQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecFilingQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the raw data from the SEC site."""
        if not query.url:
            raise OpenBBError("Please enter a URL.")
        try:
            data = Filing(query.url, query.use_cache)
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

        return data.model_dump(exclude_none=True)

    @staticmethod
    def transform_data(
        query: SecFilingQueryParams, data: dict, **kwargs: Any
    ) -> SecFilingData:
        """Transform the raw data into a structured format."""
        return SecFilingData.model_validate(data)
