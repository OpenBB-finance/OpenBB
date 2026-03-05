"""SEC Filing and Financial Statements utility.

Provides the Filing and FinancialStatements classes for parsing SEC EDGAR
filings.  XBRL-tagged filings (post-2009) are handled via the
xbrl_taxonomy_helper module; pre-XBRL filings are parsed from raw HTML tables
via non_xbrl_parser.  HTML-to-Markdown conversion uses the html2markdown
utility already present in this package.
"""

# pylint: disable=R0902,R0911,R0912,R0914,R0915
# flake8: noqa: PLR0912, PLR0914
import contextlib
import io
from collections.abc import Callable, Iterator
from functools import lru_cache
from typing import Any

from openbb_sec.utils.xbrl_taxonomy_helper import (
    TaxonomyStyle,
    XBRLNode,
    XBRLParser,
    get_label_url_for_import,
)
from pydantic import BaseModel, PrivateAttr, computed_field


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
        self._keys_labels = keys_labels  # {key: label}
        self._loader = loader
        self._loaded: dict = {}  # Cache of loaded values

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

    def __repr__(self) -> str:
        """Show keys without loading values."""
        return f"LazyDict({list(self._keys_labels.keys())})"

    def label(self, key: str) -> str | None:
        """Get the label for a specific key."""
        return self._keys_labels.get(key)


class Filing(BaseModel):
    """Filing class."""

    _url: str = PrivateAttr(default="")
    _index_headers_url: str = PrivateAttr(default="")
    _index_headers_download: str = PrivateAttr(default="")
    _complete_submission_text: str = PrivateAttr(default="")  # Full .txt file content
    _embedded_documents: dict = PrivateAttr(default_factory=dict)  # Parsed embedded docs
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
    _fiscal_period: str = PrivateAttr(default="")
    _cover_page: dict = PrivateAttr(default_factory=dict)
    _shares_outstanding: dict = PrivateAttr(default_factory=dict)
    _trading_symbols: list = PrivateAttr(default_factory=list)
    # Non-XBRL filing-level attributes
    _items: dict = PrivateAttr(default_factory=dict)  # Filing items (Item 1, 7, etc.)
    _non_xbrl_filing_initialized: bool = PrivateAttr(default=False)

    @computed_field
    @property
    def base_url(self) -> str:
        """Base URL of the filing."""
        return self._url

    @computed_field
    @property
    def name(self) -> str:
        """Entity name."""
        return self._name

    @computed_field
    @property
    def cik(self) -> str:
        """Central Index Key."""
        return self._cik

    @computed_field
    @property
    def trading_symbols(self) -> list:
        """Trading symbols, if available."""
        return self._trading_symbols

    @computed_field
    @property
    def shares_outstanding(self) -> dict:
        """Shares outstanding by date, if available."""
        return self._shares_outstanding

    @computed_field
    @property
    def sic(self) -> str:
        """Standard Industrial Classification."""
        return self._sic

    @computed_field
    @property
    def sic_organization_name(self) -> str | None:
        """Standard Industrial Classification Organization Name."""
        return self._sic_organization_name

    @computed_field
    @property
    def filing_date(self) -> str:
        """Filing date."""
        return self._filing_date

    @computed_field
    @property
    def period_ending(self) -> str:
        """Date of the ending period for the filing."""
        return self._period_ending

    @computed_field
    @property
    def fiscal_year_end(self) -> str:
        """Fiscal year end date of the entity."""
        return self._fiscal_year_end

    @computed_field
    @property
    def document_type(self) -> str:
        """Document type."""
        return self._document_type

    @computed_field
    @property
    def has_cover_page(self) -> bool:
        """True if the filing has a cover page."""
        return bool(self._cover_page_url)

    @computed_field
    @property
    def cover_page(self) -> dict:
        """Cover page information, if available."""
        return self._cover_page

    @computed_field
    @property
    def description(self) -> str | None:
        """Document description, if available."""
        return self._description

    @property
    def document_urls(self) -> LazyDict:
        """Dictionary of documents keyed by their type (e.g., '424B5', '10-K').

        Use .keys() to see available document types.
        Use .labels() to get a dict of {type: description}.
        Access specific document with f.document_urls['424B5']['url'].
        """
        doc_data = self._get_document_data()
        # Build keys_labels dict: {type: description}
        keys_labels = {k: v.get("description", v.get("filename", k)) for k, v in doc_data.items()}

        def load_document(key: str) -> dict:
            """Load document info (returns the doc dict)."""
            return doc_data[key]

        return LazyDict(keys_labels, load_document)

    def _get_document_data(self) -> dict:
        """Get raw document data as dict of {type: doc_info}."""
        docs_dict: dict = {}
        for doc in self._document_urls:
            doc_type = doc.get("type", "")
            if doc_type:
                # Handle duplicate types by appending sequence
                if doc_type in docs_dict:
                    seq = doc.get("sequence", "")
                    doc_type = f"{doc_type}_{seq}" if seq else f"{doc_type}_dup"
                docs_dict[doc_type] = doc
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

    @property
    def exhibits(self) -> LazyDict:
        """Lazy-loading dictionary of exhibits keyed by their type (e.g., 'EX-4.4', 'EX-22').

        Use .keys() to see available exhibits without loading content.
        Use .labels() to get a dict of {key: description}.
        Access specific exhibit with fs.exhibits['EX-10.1'].
        """
        exhibit_data = self._get_exhibit_data()
        # Build keys_labels dict: {type: description}
        keys_labels = {k: v.get("description", v.get("filename", k)) for k, v in exhibit_data.items()}

        def load_exhibit(key: str) -> dict:
            """Load exhibit info (returns the doc dict for now)."""
            return exhibit_data[key]

        return LazyDict(keys_labels, load_exhibit)

    @computed_field
    @property
    def is_xbrl(self) -> bool:
        """Whether this filing contains XBRL data.

        Non-XBRL filings (typically pre-2009) contain financial statements
        embedded in HTML tables without structured XBRL tagging.
        """
        # Check for MetaLinks.json file which indicates XBRL filing
        for doc in self._document_urls:
            filename = doc.get("filename", "").lower()
            if filename == "metalinks.json":
                return True
            # Also check for XBRL instance documents
            if filename.endswith("_htm.xml") or filename.endswith("-xbrl.zip"):
                return True
        return False

    def get_embedded_document(self, identifier: str) -> str | None:
        """Get embedded document content by filename or document type.

        For non-XBRL filings, the complete submission text file contains all
        documents embedded within it. This method retrieves a specific document
        without making additional HTTP requests.

        Parameters
        ----------
        identifier : str
            Either a filename (e.g., 'a2166922zex-13.htm') or document type
            (e.g., 'EX-13', '10-K')

        Returns
        -------
        str or None
            The document content (HTML/text), or None if not found
        """
        if identifier in self._embedded_documents:
            return self._embedded_documents[identifier].get("content")

        # Try case-insensitive match on type
        identifier_upper = identifier.upper()
        for _key, doc in self._embedded_documents.items():
            if doc.get("type", "").upper() == identifier_upper:
                return doc.get("content")

        return None

    def _get_items_info(self) -> dict:
        """Get filing items info as dict of {key: item_data}."""
        return self._items

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
        # Build keys_labels dict: {key: name}
        keys_labels = {k: v.get("name", k) if isinstance(v, dict) else k for k, v in items_info.items()}

        def load_item(key: str) -> dict:
            """Load item data."""
            return items_info[key]

        return LazyDict(keys_labels, load_item)

    @computed_field
    @property
    def main_document_url(self) -> str | None:
        """URL of the main filing document (10-K or 10-Q HTML file)."""
        if not self._document_urls:
            return None

        # Look for the main document (type matches filing type, sequence 1)
        for doc in self._document_urls:
            doc_type = doc.get("type", "").upper()
            if doc_type in ("10-K", "10-Q", "10-K/A", "10-Q/A", "8-K", "8-K/A"):
                return doc.get("url")

        # Fallback: first HTML document
        for doc in self._document_urls:
            url = doc.get("url", "")
            if url.endswith(".htm") or url.endswith(".html"):
                return url

        return None

    def __init__(self, url: str):
        """Initialize the Filing class."""
        super().__init__()
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

        index_headers = check_val[:-8] + "-" + check_val[-8:-6] + "-" + check_val[-6:] + "-index-headers.htm"
        self._index_headers_url = self._url + index_headers
        self._download_index_headers()

        # XBRL filings have R1.htm cover page; non-XBRL use embedded documents
        if self._document_urls:
            for doc in self._document_urls:
                if doc.get("url", "").endswith("R1.htm"):
                    self._cover_page_url = doc.get("url")
                    break

        # Initialize based on filing type
        if self.is_xbrl:
            # XBRL filing: download structured cover page if available
            if self.has_cover_page and not self._cover_page:
                self._download_cover_page()
            # For 8-K filings, items are in HTML even for XBRL filings
            if self._document_type and "8-K" in self._document_type.upper():
                self._initialize_8k_items()
        else:
            # Non-XBRL filing: build cover page from submission text and parse items
            if not self._cover_page:
                self._build_non_xbrl_cover_page()
            self._initialize_non_xbrl_filing()

    @staticmethod
    def download_file(url, read_html_table: bool = False):
        """Download a file from a SEC URL."""
        # pylint: disable=import-outside-toplevel
        from warnings import warn

        from openbb_core.provider.utils.helpers import make_request
        from openbb_sec.utils.definitions import SEC_HEADERS

        @lru_cache(maxsize=128)
        def _download_file(url):
            """Download a file from a URL."""
            return make_request(url, headers=SEC_HEADERS)

        try:
            response = _download_file(url)

            if not response.ok:
                raise RuntimeError(f"Failed to download file: {response.status_code} - {response.reason}")

            if read_html_table is True:
                if not url.endswith(".htm") and not url.endswith(".html"):
                    warn(f"File is not a HTML file: {url}")
                    return response.content

                return Filing.try_html_table(response.text)

            if url.endswith(".json"):
                return response.json()

            return response.content

        except Exception as e:
            raise RuntimeError(f"Failed to download file: {e} -> {e.args}") from e

    @staticmethod
    def try_html_table(text: str, **kwargs) -> list:
        """Attempt to parse tables from a HTML string.
        All keyword arguments are passed to pandas.read_html.
        """
        # pylint: disable=import-outside-toplevel
        from io import StringIO

        from pandas import read_html

        try:
            return read_html(StringIO(text), **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to parse table: {e}") from e

    def _download_index_headers(self):
        """Download the index headers table."""
        # pylint: disable=import-outside-toplevel
        import re

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
            # Convert each document to a dictionary
            document_dicts = [document_to_dict(doc, accession_number) for doc in documents if doc]

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
                    self._period_ending = as_of_date[:4] + "-" + as_of_date[4:6] + "-" + as_of_date[6:]
                elif "FILED AS OF DATE" in line:
                    filing_date = value
                    self._filing_date = filing_date[:4] + "-" + filing_date[4:6] + "-" + filing_date[6:]
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
                    self._description = self._description + "; " + info if self._description else info
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
                    response = self.download_file(self._index_headers_url)
                    self._index_headers_download = response  # type: ignore
                else:
                    response = self._index_headers_download

                soup = BeautifulSoup(response, "html.parser")  # type: ignore
                text = soup.find("pre").text  # type: ignore
            except RuntimeError as e:
                # Fall back to the complete submission .txt file for older filings
                if "404" in str(e):
                    txt_url = self.base_url + accession_number + ".txt"
                    response = self.download_file(txt_url)
                    text = response.decode("utf-8", errors="ignore")  # type: ignore
                else:
                    raise

            if text:
                parse_header_text(text, accession_number)

        except Exception as e:
            raise RuntimeError(f"Failed to download and read the index headers table: {e}") from e

    def _download_cover_page(self):
        """Download the cover page table."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from pandas import read_html, to_datetime, MultiIndex
        import unicodedata

        def normalize_text(text):
            """Normalize unicode characters in text."""
            if not isinstance(text, str):
                return text
            # Normalize unicode (NFKC converts compatibility characters to their canonical form)
            # This converts \xa0 (non-breaking space) to regular space, etc.
            text = unicodedata.normalize("NFKC", text)
            # Also strip any remaining problematic whitespace
            text = " ".join(text.split())
            return text

        try:
            response = self.download_file(self._cover_page_url)
            df = read_html(StringIO(response.decode()))[0]  # type: ignore
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

            title = df.columns[0][0] if isinstance(df.columns, MultiIndex) else df.columns[0]

            if title and "- shares" in title:
                shares_multiplier = title.split(" shares in ")[-1]
                multiplier = FinancialStatements._multiplier_map(  # pylint: disable=W0212
                    shares_multiplier
                )
                shares_outstanding = df[df.iloc[:, 0].str.contains("Shares Outstanding")].iloc[:, 2].values[0]
                as_of_date = df.columns[2][1] if isinstance(df.columns, MultiIndex) else df.columns[2]

                if as_of_date and shares_outstanding:
                    self._shares_outstanding = {
                        to_datetime(as_of_date).strftime("%Y-%m-%d"): int(shares_outstanding * multiplier)
                    }

            if not df.empty:
                trading_symbols = df[df.iloc[:, 0].astype(str).str.lower() == "trading symbol"].iloc[:, 1].values.tolist()
                if trading_symbols:
                    self._trading_symbols = [normalize_text(s) for s in trading_symbols]

                df.columns = [d[1] if isinstance(d, tuple) else d for d in df.columns]
                df = df.iloc[:, :2].dropna(how="any")
                df.columns = ["key", "value"]
                output = df.set_index("key").to_dict()["value"]

                # Normalize unicode characters in all values
                output = {normalize_text(k): normalize_text(v) for k, v in output.items()}

                if not output.get("SIC") and self._sic:
                    output["SIC"] = self._sic
                    output["SIC Organization Name"] = self.sic_organization_name

                self._cover_page = output

        except IndexError:
            pass

        except Exception as e:
            raise RuntimeError(f"Failed to download and read the cover page table: {e}") from e

    def _build_non_xbrl_cover_page(self):
        """Build cover page info for non-XBRL filings from submission text.

        Uses the complete submission text file which is already loaded,
        avoiding any additional HTTP requests.
        """
        # pylint: disable=import-outside-toplevel
        import re

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
        main_doc_content = self.get_embedded_document("10-K") or self.get_embedded_document("10-Q")
        if not main_doc_content:
            main_doc_content = self.get_embedded_document("10-K/A") or self.get_embedded_document("10-Q/A")

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
                    state_match = re.search(
                        r"(NEW YORK|DELAWARE|CALIFORNIA|TEXAS|NEVADA|FLORIDA|ILLINOIS|PENNSYLVANIA|OHIO|GEORGIA|NEW JERSEY|VIRGINIA|MASSACHUSETTS|WASHINGTON|MARYLAND|COLORADO|ARIZONA|MICHIGAN|MINNESOTA|NORTH CAROLINA|MISSOURI|WISCONSIN|CONNECTICUT|OREGON|INDIANA|TENNESSEE|KENTUCKY|LOUISIANA|OKLAHOMA|ALABAMA|SOUTH CAROLINA|IOWA|UTAH|KANSAS|ARKANSAS|MISSISSIPPI|NEBRASKA|NEW MEXICO|HAWAII|IDAHO|NEW HAMPSHIRE|MAINE|MONTANA|RHODE ISLAND|SOUTH DAKOTA|NORTH DAKOTA|ALASKA|VERMONT|WYOMING|WEST VIRGINIA)\s*\(?State (?:of|or) [Ii]ncorporation",
                        text,
                        re.IGNORECASE,
                    )
                if state_match:
                    state_name = state_match.group(1).strip().title()
                    if len(state_name) > 2 and len(state_name) < 30:
                        cover_page["Entity Incorporation State Country Code"] = state_name

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
                        cover_page["Entity Common Stock Shares Outstanding"] = int(shares_str)

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
                            cover_page["Entity Common Stock Shares Outstanding"] = int(float(shares_str))

                # Try to find stock exchange from Section 12(b) table
                exchange_match = re.search(
                    r"Name of each exchange.*?on which registered.*?<TD[^>]*>.*?<FONT[^>]*>(?:<BR>)?\s*([A-Za-z\s]+(?:Stock\s+)?Exchange)",
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
                    rows = re.findall(r"<TR[^>]*>(.*?)</TR>", table_html, re.IGNORECASE | re.DOTALL)
                    for row in rows:
                        if "<TH" in row.upper():
                            continue
                        cells = re.findall(r"<TD[^>]*>(.*?)</TD>", row, re.IGNORECASE | re.DOTALL)
                        if len(cells) >= 3:

                            def clean_cell(cell):
                                cell = re.sub(r"<[^>]+>", " ", cell)
                                cell = re.sub(r"&nbsp;", " ", cell)
                                cell = re.sub(r"\s+", " ", cell)
                                return cell.strip()

                            title = clean_cell(cells[0])
                            shares = clean_cell(cells[2]) if len(cells) > 2 else ""
                            exchange_name = clean_cell(cells[-1]) if len(cells) > 2 else clean_cell(cells[1])

                            if not title and not exchange_name:
                                continue

                            if title:
                                security = {"title": title}
                                if shares and shares.replace(",", "").isdigit():
                                    security["shares_outstanding"] = int(shares.replace(",", ""))
                                if exchange_name:
                                    security["exchange"] = exchange_name
                                securities.append(security)
                            elif exchange_name and securities:
                                if "additional_exchanges" not in securities[-1]:
                                    securities[-1]["additional_exchanges"] = []
                                securities[-1]["additional_exchanges"].append(exchange_name)

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

            except Exception:
                pass  # Don't fail if parsing additional info fails

        if cover_page:
            self._cover_page = cover_page
            if "Entity Common Stock Shares Outstanding" in cover_page:
                date_key = self._period_ending or "unknown"
                self._shares_outstanding = {date_key: cover_page["Entity Common Stock Shares Outstanding"]}

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
            main_doc = self.get_embedded_document("10-K") or self.get_embedded_document("10-Q")
            if not main_doc:
                main_doc = self.get_embedded_document("10-K/A") or self.get_embedded_document("10-Q/A")

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
            self._items = extract_items(html_content)

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
            markdown_content = html_to_markdown(html_content, base_url=self.base_url)

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
                except Exception:
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
                except Exception:
                    continue

    @staticmethod
    def _clean_html_to_text(content, base_url: str = "", keep_tables: bool = True) -> str:
        """Clean HTML content to markdown.

        This is a thin wrapper around the html_to_markdown() function
        in openbb_sec.utils.html2markdown. All HTML-to-markdown conversion
        goes through that single implementation.

        Parameters
        ----------
        content : str or bytes
            HTML content to convert
        base_url : str
            Base URL for resolving relative links and images
        keep_tables : bool
            If True, convert tables to markdown tables. If False, skip tables.

        Returns
        -------
        str
            Markdown-formatted text
        """
        from openbb_sec.utils.html2markdown import html_to_markdown

        return html_to_markdown(content, base_url=base_url, keep_tables=keep_tables)

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
                raise ValueError(f"Exhibit '{exhibit}' not found. Available: {list(self.exhibits.keys())}")
        else:
            exhibit_data = exhibit

        if not (url := exhibit_data.get("url")):
            return ""

        content = self.download_file(url)
        return self._clean_html_to_text(content, url)

    def get_document_text(self, document: str | dict) -> str:
        """Get the text content of a document, converted to markdown.

        Args:
            document: Either a document type key (e.g., '424B5', '10-K') or the document dict.

        Returns:
            The text content of the document as markdown.

        Example:
            >>> f = Filing('https://www.sec.gov/Archives/edgar/data/...')
            >>> text = f.get_document_text('424B5')
            >>> # Or using the dict directly:
            >>> text = f.get_document_text(f.document_urls['424B5'])
        """
        if isinstance(document, str):
            doc_data = self.document_urls.get(document)
            if not doc_data:
                raise ValueError(f"Document '{document}' not found. Available: {list(self.document_urls.keys())}")
        else:
            doc_data = document

        if not (url := doc_data.get("url")):
            return ""

        content = self.download_file(url)
        return self._clean_html_to_text(content, url)

    def get_main_document_url(self) -> str:
        """Get the URL of the main filing document (10-K, 10-Q, etc.)."""
        # Common main document types
        main_types = ["10-K", "10-Q", "8-K", "20-F", "S-1", "10-K/A", "10-Q/A"]

        # Try to match by type first
        if self._document_urls:
            for doc in self._document_urls:
                if doc.get("type") in main_types:
                    return doc.get("url")

        # Fallback: Find first .htm file that is not an exhibit
        if self._document_urls:
            for doc in self._document_urls:
                if doc.get("filename", "").endswith(".htm") and not doc.get("type", "").startswith("EX-"):
                    return doc.get("url")

        return ""

    def get_filing_text(self) -> str:
        """Get the full text of the main filing document."""
        url = self.get_main_document_url()
        if not url:
            return ""
        content = self.download_file(url)
        return self._clean_html_to_text(content, url)

    def extract_item(self, item: str) -> str:
        """Extract a specific item from the filing (e.g., 'Item 1A', 'Item 7').

        Dynamically discovers section anchors from the Table of Contents.
        For non-XBRL filings, uses pre-parsed items if available.
        """
        # pylint: disable=import-outside-toplevel
        import re

        from bs4 import BeautifulSoup

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
        main_doc_url = self.get_main_document_url()
        if not main_doc_url:
            return ""

        content = self.download_file(main_doc_url)
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="ignore")

        import warnings

        from bs4 import XMLParsedAsHTMLWarning

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
            if not href.startswith("#"):
                continue

            anchor_id = href[1:]
            link_text = link.get_text(strip=True).lower()

            item_match = re.search(r"item\s*(\d+[a-z]?)\.?", link_text)
            if not item_match:
                item_match = re.search(r"item[_\s]*(\d+)[_\s]*([a-z])?[_\s]", anchor_id, re.IGNORECASE)
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

                    # For Item 7 (MD&A), check if this is just a cross-reference
                    if item_normal == "7" and len(result) < 1000:
                        if "See the information" in result or "See MD&A" in result:
                            text = self.get_filing_text()
                            mda = self._extract_actual_mda(text)
                            if mda:
                                return mda

                    return result

        # Fall back to text-based extraction
        return self._extract_item_by_text(item)

    def _extract_item_by_text(self, item: str) -> str:
        """Fallback text-based item extraction."""
        import re

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

        if item_num == "7":
            mda_content = self._extract_actual_mda(text)
            if mda_content:
                return mda_content

        if item_num == "2":
            mda_content = self._extract_10q_mda(text)
            if mda_content:
                return mda_content

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

    def _extract_10q_mda(self, text: str) -> str:
        """Extract MD&A section from a 10-Q filing.

        In 10-Q filings, MD&A is Part I, Item 2.
        """
        import re  # pylint: disable=import-outside-toplevel

        mda_pattern = r"^Item\s+2\.?\s*MANAGEMENT['\u2019\u2018\"\u201C\u201D]?S?\s+DISCUSSION\s+AND\s+ANALYSIS"
        match = re.search(mda_pattern, text, re.IGNORECASE | re.MULTILINE)

        if not match:
            mda_pattern = r"\*\*MANAGEMENT['\u2019\u2018\"\u201C\u201D]?S?\s+DISCUSSION\s+AND\s+ANALYSIS"
            match = re.search(mda_pattern, text, re.IGNORECASE)

        if not match:
            return ""

        start_pos = match.start()

        end_patterns = [
            r"^Item\s+3\.?\s*QUANTITATIVE",
            r"^Item\s+3\.?\s*[A-Z]",
            r"^Item\s+4\.?\s*CONTROLS",
            r"^Item\s+4\.?\s*[A-Z]",
            r"\*\*QUANTITATIVE AND QUALITATIVE",
        ]

        end_pos = len(text)
        for pattern in end_patterns:
            m = re.search(pattern, text[start_pos + 500 :], re.IGNORECASE | re.MULTILINE)
            if m:
                candidate = start_pos + 500 + m.start()
                end_pos = min(end_pos, candidate)

        return text[start_pos:end_pos].strip()

    def _extract_actual_mda(self, text: str) -> str:
        """Extract the actual MD&A section by looking for the header."""
        import re  # pylint: disable=import-outside-toplevel

        mda_header_pattern = r"\*\*MANAGEMENT['\u2019\u2018\"\u201C\u201D]?S DISCUSSION AND ANALYSIS\*\*"
        match = re.search(mda_header_pattern, text, re.IGNORECASE)

        if not match:
            mda_header_pattern = r"^MANAGEMENT['\u2019\u2018\"\u201C\u201D]?S DISCUSSION AND ANALYSIS$"
            match = re.search(mda_header_pattern, text, re.IGNORECASE | re.MULTILINE)

        if not match:
            return ""

        start_pos = match.start()

        end_patterns = [
            r"\*\*Item\s+\d+[A-Za-z]?\.",
            r"^\s*Item\s+3\.",
            r"^\s*Item\s+7A\.",
            r"^\s*Item\s+8\.",
            r"\*\*CONSOLIDATED\s+STATEMENTS?\s+OF",
            r"\*\*STATEMENTS?\s+OF\s+CONSOLIDATED",
            r"\*\*CONSOLIDATED\s+BALANCE\s+SHEETS?\*\*",
            r"\*\*CONSOLIDATED\s+FINANCIAL\s+STATEMENTS\*\*",
            r"\*\*REPORT\s+OF\s+INDEPENDENT",
            r"^\*\*SIGNATURES\*\*",
            r"\*\*QUANTITATIVE\s+AND\s+QUALITATIVE",
        ]

        end_pos = len(text)

        for pattern in end_patterns:
            m = re.search(pattern, text[start_pos + 1000 :], re.IGNORECASE | re.MULTILINE)
            if m:
                candidate = start_pos + 1000 + m.start()
                end_pos = min(end_pos, candidate)

        return text[start_pos:end_pos].strip()

    def __repr__(self):
        """Return the string representation of the class."""
        repr_str = "SEC Filing(\n"
        for k, v in self.__class__.model_computed_fields.items():
            repr_str += f"  {k} : {v.return_type.__name__} - {v.description}\n"
        repr_str += ")"
        return repr_str


class FinancialStatements(Filing):
    """FinancialStatements class."""

    _statements: dict = PrivateAttr(default_factory=dict)
    _tags: dict = PrivateAttr(default_factory=dict)
    _resources: dict = PrivateAttr(default_factory=dict)
    _xsd: dict = PrivateAttr(default_factory=dict)
    _calcs: dict = PrivateAttr(default_factory=dict)
    _labels: dict = PrivateAttr(default_factory=dict)
    _presentation: list[XBRLNode] = PrivateAttr(default_factory=list)
    _metalinks: dict = PrivateAttr(default_factory=dict)
    _instance: dict = PrivateAttr(default_factory=dict)
    _text_blocks: dict = PrivateAttr(default_factory=dict)
    _disclosures: dict = PrivateAttr(default_factory=dict)
    _period_context: dict = PrivateAttr(default_factory=dict)
    _period_end1: str = PrivateAttr(default="")
    _period_end2: str = PrivateAttr(default="")
    _html_filing: Any = PrivateAttr(default=None)
    _toc: dict = PrivateAttr(default_factory=dict)
    # Non-XBRL specific attributes (financial statement related only)
    _non_xbrl_statements: dict = PrivateAttr(default_factory=dict)
    _non_xbrl_text_blocks: dict = PrivateAttr(default_factory=dict)
    _non_xbrl_initialized: bool = PrivateAttr(default=False)

    @computed_field
    @property
    def toc(self) -> dict:
        """Table of contents mapping section keys (e.g., '1A', '7') to titles."""
        if self._toc:
            return self._toc

        # pylint: disable=import-outside-toplevel
        import re
        import warnings

        from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

        main_doc_url = self.get_main_document_url()
        if not main_doc_url:
            return {}

        content = self.download_file(main_doc_url)
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="ignore")

        soup = BeautifulSoup(content, "lxml")  # type: ignore
        toc_dict: dict = {}

        href_to_texts: dict = {}
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if not href or not str(href).startswith("#"):
                continue
            link_text = link.get_text(strip=True)
            if not link_text:
                continue
            if href not in href_to_texts:
                href_to_texts[href] = []
            href_to_texts[href].append(link_text)

        valid_item_pattern = re.compile(r"^ITEM\s*(1[0-5]?|[2-9])(A|B|C)?[.:]?$", re.IGNORECASE)

        for href, texts in href_to_texts.items():
            item_num = None
            title = None
            for text in texts:
                item_match = valid_item_pattern.match(text.strip())
                if item_match:
                    num = item_match.group(1)
                    suffix = item_match.group(2) or ""
                    item_num = f"{num}{suffix}".upper()
                elif text and not re.match(r"^\d+$", text):
                    if title is None and len(text) > 5:
                        title = text

            if item_num and title and item_num not in toc_dict:
                toc_dict[item_num] = title

        self._toc = toc_dict
        return self._toc

    @computed_field
    @property
    def calendar_period(self) -> str:
        """Calendar for the period ending."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

        year = self._period_ending[:4]
        period = to_datetime(self._period_ending).quarter
        return f"{year}-Q{period}"

    @computed_field
    @property
    def fiscal_period(self) -> str:
        """Fiscal period focus."""
        year = self._fiscal_year
        period = self._fiscal_period
        return f"{year}-{period}" if year and period else period if period else year if year else ""

    def _get_statements_info(self) -> dict:
        """Get statement info as dict of {key: {name, url/data}}."""
        # XBRL statements
        if self._resources:
            statements: dict = {}
            statement_items = self._resources.copy()
            for v in statement_items.values():
                if v.get("group") == "statement":
                    statements[v["short_name"]] = {
                        "name": v.get("long_name", v["short_name"]),
                        "url": v.get("url"),
                    }
            if statements:
                return statements

        # Non-XBRL statements
        if self._non_xbrl_statements:
            return {
                k: {
                    "name": v.get("name", k),
                    "data": v.get("data"),
                    "meta": v.get("meta"),
                }
                for k, v in self._non_xbrl_statements.items()
            }

        return {}

    @property
    def statements(self) -> LazyDict:
        """Lazy-loading dictionary of financial statements.

        Use .keys() to see available statements without loading data.
        Use .labels() to get a dict of {key: name}.
        Access specific statement with fs.statements['income'].

        For XBRL filings: Returns statement data from XBRL
        For non-XBRL filings: Returns {"name": str, "data": DataFrame, "meta": DataFrame}
        """
        statements_info = self._get_statements_info()
        keys_labels = {k: v.get("name", k) for k, v in statements_info.items()}

        def load_statement(key: str) -> dict:
            """Load statement data."""
            return statements_info[key]

        return LazyDict(keys_labels, load_statement)

    def _get_disclosures_info(self) -> dict:
        """Get disclosure info as dict of {key: disclosure_data}."""
        if self._disclosures:
            return self._disclosures

        if self._items:
            return self._items

        # XBRL disclosures
        disclosures: dict = {}
        disclosure_items = self._resources.copy()
        for v in disclosure_items.values():
            if v.get("group") == "disclosure":
                _tag = v.get("anchor_tag", v.get("name"))
                disclosures[_tag] = {
                    "long_name": v.get("long_name"),
                    "context_ref": v.get("context_ref"),
                    "url": v.get("url"),
                }
        return disclosures

    @property
    def disclosures(self) -> LazyDict:
        """Lazy-loading dictionary of disclosures (Notes to Financial Statements).

        Use .keys() to see available disclosures without loading content.
        Use .labels() to get a dict of {key: long_name}.
        Access specific disclosure with fs.disclosures['InventoryDisclosure'].
        """
        disclosures_info = self._get_disclosures_info()
        keys_labels = {
            k: v.get("long_name", v.get("name", k)) if isinstance(v, dict) else k for k, v in disclosures_info.items()
        }

        def load_disclosure(key: str) -> dict:
            """Load disclosure data."""
            return disclosures_info[key]

        return LazyDict(keys_labels, load_disclosure)

    @computed_field
    @property
    def text_blocks(self) -> dict:
        """Dictionary of extracted text blocks, if available.

        For XBRL filings: Returns text blocks from XBRL instance
        For non-XBRL filings: Returns text blocks extracted from HTML sections
        """
        # XBRL text blocks
        if self._text_blocks:
            text_blocks: dict = {}
            disclosure_keys = list(self.disclosures.keys())

            def find_disclosure_key(local_name: str) -> str | None:
                """Find the actual disclosure key matching a local name."""
                if local_name in disclosure_keys:
                    return local_name
                for dk in disclosure_keys:
                    if "_" in dk and dk.split("_", 1)[1] == local_name:
                        return dk
                return None

            for k, v in self._text_blocks.items():
                if v.get("value") and v["value"] != "\nNone.":
                    pres = v.get("presentation", [])
                    name = pres[0] if pres else v.get("name")
                    local_name = k.split("_", 1)[1] if "_" in k else k
                    disclosure_key = find_disclosure_key(local_name)
                    disclosure_list = [disclosure_key] if disclosure_key else []
                    text_blocks[k] = {
                        "name": name,
                        "disclosure": disclosure_list,
                        "text": v["value"],
                    }
            return text_blocks

        # Non-XBRL text blocks
        if self._non_xbrl_text_blocks:
            return self._non_xbrl_text_blocks

        return {}

    @computed_field
    @property
    def tags(self) -> dict:
        """Dictionary of tags and their properties, if available."""
        return self._tags

    @computed_field
    @property
    def is_xbrl(self) -> bool:
        """Whether this filing contains XBRL data.

        Non-XBRL filings (typically pre-2009) contain financial statements
        embedded in HTML tables without structured XBRL tagging.
        """
        has_metalinks = bool(self._metalinks)
        has_resources = bool(self._resources) and len(self._resources) > 1
        has_tags = bool(self._tags)
        has_instance = bool(self._instance)

        return has_metalinks or has_resources or has_tags or has_instance

    @computed_field
    @property
    def main_document_url(self) -> str | None:
        """URL of the main filing document (10-K or 10-Q HTML file)."""
        return self.get_main_document_url()

    def get_main_document_url(self) -> str | None:
        """Get the URL of the main filing document."""
        if not self._document_urls:
            return None

        for doc in self._document_urls:
            doc_type = doc.get("type", "").upper()
            if doc_type in ("10-K", "10-Q", "10-K/A", "10-Q/A"):
                return doc.get("url")

        for doc in self._document_urls:
            url = doc.get("url", "")
            if url.endswith(".htm") or url.endswith(".html"):
                return url

        return None

    def __init__(self, url: str):
        """Initialize the FinancialStatements class."""
        super().__init__(url)
        self._download_metalinks()
        if self._resources and len(self._resources) > 1:
            self._build_schema_from_xml()
            self._download_xbrl_instance()
        else:
            # Non-XBRL filing - parse from HTML tables
            self._initialize_non_xbrl()

    def _initialize_non_xbrl(self):
        """Initialize non-XBRL filing data from HTML tables.

        For filings where financial statements are in exhibits (e.g., EX-13 Annual Report),
        this method will also parse those exhibits.
        """
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.non_xbrl_parser import (
            extract_items,
            extract_text_blocks,
            extract_toc,
            find_all_statements,
            get_statement_names,
        )

        if self._non_xbrl_initialized:
            return

        try:
            main_doc = self.get_embedded_document("10-K") or self.get_embedded_document("10-Q")
            if not main_doc:
                main_doc = self.get_embedded_document("10-K/A") or self.get_embedded_document("10-Q/A")

            if main_doc:
                html_content = main_doc
            else:
                main_url = self.get_main_document_url()
                if not main_url:
                    return
                html_content = self.download_file(main_url)
                if isinstance(html_content, bytes):
                    html_content = html_content.decode("utf-8", errors="ignore")

            # Parse all financial statements from main document
            statements_data = find_all_statements(html_content)
            statement_names = get_statement_names()

            for stmt_type, (data_df, meta_df) in statements_data.items():
                display_name = statement_names.get(stmt_type, stmt_type.title())
                self._non_xbrl_statements[stmt_type] = {
                    "name": display_name,
                    "data": data_df,
                    "meta": meta_df,
                }

            # If no statements found in main document, check exhibits
            if not self._non_xbrl_statements:
                self._parse_exhibit_statements(find_all_statements, statement_names)

            # Extract table of contents
            self._toc = extract_toc(html_content)

            # Extract text blocks (notes to financial statements)
            self._non_xbrl_text_blocks = extract_text_blocks(html_content)
            self._disclosures = self._non_xbrl_text_blocks

            if not self._disclosures:
                self._parse_exhibit_disclosures(extract_text_blocks)

            if not self._items:
                self._items = extract_items(html_content)
                if not self._items:
                    self._parse_exhibit_items(extract_items, extract_text_blocks)

            self._non_xbrl_initialized = True

        except Exception as e:
            import warnings

            warnings.warn(f"Failed to parse non-XBRL filing: {e}")

    def _parse_exhibit_statements(self, find_all_statements, statement_names):
        """Parse financial statements from exhibits (e.g., EX-13 Annual Report)."""
        exhibit_priority = ["EX-13", "EX-13.1", "EX-13.2", "13", "ANNUAL REPORT"]

        # Try embedded documents first (no HTTP request needed)
        for exhibit_key in exhibit_priority:
            exhibit_html = self.get_embedded_document(exhibit_key)
            if exhibit_html:
                try:
                    statements_data = find_all_statements(exhibit_html)
                    for stmt_type, (data_df, meta_df) in statements_data.items():
                        if stmt_type not in self._non_xbrl_statements:
                            display_name = statement_names.get(stmt_type, stmt_type.title())
                            self._non_xbrl_statements[stmt_type] = {
                                "name": display_name,
                                "data": data_df,
                                "meta": meta_df,
                            }
                    if self._non_xbrl_statements:
                        return
                except Exception:
                    continue

        # Fall back to downloading exhibits if not embedded
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
                        statements_data = find_all_statements(exhibit_html)
                        for stmt_type, (data_df, meta_df) in statements_data.items():
                            if stmt_type not in self._non_xbrl_statements:
                                display_name = statement_names.get(stmt_type, stmt_type.title())
                                self._non_xbrl_statements[stmt_type] = {
                                    "name": display_name,
                                    "data": data_df,
                                    "meta": meta_df,
                                }
                        if self._non_xbrl_statements:
                            return
                except Exception:
                    continue

        # If still no statements, try all HTML exhibits
        for exhibit_key, exhibit_doc in exhibits.items():
            if exhibit_key in exhibit_priority:
                continue
            url = exhibit_doc.get("url", "")
            if not (url.endswith(".htm") or url.endswith(".html")):
                continue
            try:
                exhibit_html = self.download_file(url)
                if isinstance(exhibit_html, bytes):
                    exhibit_html = exhibit_html.decode("utf-8", errors="ignore")
                if exhibit_html:
                    statements_data = find_all_statements(exhibit_html)
                    for stmt_type, (data_df, meta_df) in statements_data.items():
                        if stmt_type not in self._non_xbrl_statements:
                            display_name = statement_names.get(stmt_type, stmt_type.title())
                            self._non_xbrl_statements[stmt_type] = {
                                "name": display_name,
                                "data": data_df,
                                "meta": meta_df,
                            }
                    if self._non_xbrl_statements:
                        return
            except Exception:
                continue

    def _parse_exhibit_disclosures(self, extract_text_blocks):
        """Parse disclosures (notes to FS) from exhibits if not found in main document."""
        exhibit_priority = ["EX-13", "EX-13.1", "EX-13.2", "13"]

        for exhibit_key in exhibit_priority:
            exhibit_html = self.get_embedded_document(exhibit_key)
            if exhibit_html:
                try:
                    disclosures = extract_text_blocks(exhibit_html)
                    if disclosures:
                        self._disclosures = disclosures
                        self._non_xbrl_text_blocks = disclosures
                        return
                except Exception:
                    continue

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
                        disclosures = extract_text_blocks(exhibit_html)
                        if disclosures:
                            self._disclosures = disclosures
                            self._non_xbrl_text_blocks = disclosures
                            return
                except Exception:
                    continue

    def _parse_exhibit_items(self, extract_items, extract_text_blocks):
        """Parse items (Item 1, Item 7, etc.) and text blocks from exhibits.

        This FinancialStatements version also extracts text blocks for disclosures.
        """
        exhibit_priority = ["EX-13", "EX-13.1", "EX-13.2", "13"]

        for exhibit_key in exhibit_priority:
            exhibit_html = self.get_embedded_document(exhibit_key)
            if exhibit_html:
                try:
                    items = extract_items(exhibit_html)
                    if items:
                        self._items = items
                        if not self._disclosures:
                            disclosures = extract_text_blocks(exhibit_html)
                            if disclosures:
                                self._disclosures = disclosures
                                self._non_xbrl_text_blocks = disclosures
                        return
                except Exception:
                    continue

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
                            if not self._disclosures:
                                disclosures = extract_text_blocks(exhibit_html)
                                if disclosures:
                                    self._disclosures = disclosures
                                    self._non_xbrl_text_blocks = disclosures
                            return
                except Exception:
                    continue

    @staticmethod
    def _multiplier_map(string) -> int:  # pylint: disable=R0911
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

    def _download_metalinks(self):
        """Download the MetaLinks.json file from the SEC website."""
        metalinks_url = ""
        for d in self._document_urls:
            if d.get("url", "").endswith("MetaLinks.json"):
                metalinks_url = d["url"]
                break
        if not metalinks_url:
            return

        if not self._metalinks:
            res = self.download_file(metalinks_url)
            self._metalinks = res.get("instance", {}).copy()  # type: ignore
            res = res.get("instance", {})  # type: ignore
        else:
            res = self._metalinks.copy()

        statement_items: dict = self._resources if self._resources else {}
        tags: dict = self._tags if self._tags else {}

        try:
            keys = list(res)
            for key in keys:
                for item in list(res[key]["report"]):
                    if not item:
                        continue
                    if res[key]["report"].get(item):
                        anchor = res[key]["report"][item].get("uniqueAnchor") or res[key]["report"][item].get(
                            "firstAnchor"
                        )
                        subgroup = res[key]["report"][item].get("subGroupType")
                        menucat = res[key]["report"][item].get("menuCat")
                        _item = res[key]["report"][item]
                        statement_items[item.replace("R", "r") if item[0] == "R" else item] = {
                            "short_name": _item.get("shortName"),
                            "long_name": _item.get("longName"),
                            "group": _item.get("groupType"),
                            "sub_group": (subgroup if subgroup and subgroup != "''" else None),
                            "menu_category": (menucat if menucat and menucat != "''" else None),
                            "anchor_tag": (anchor.get("name", "").replace(":", "_") if anchor else None),
                            "order": _item.get("order"),
                            "unit_ref": anchor.get("unitRef") if anchor else None,
                            "xsi_nil": (anchor.get("xsiNil") == "true" if anchor and anchor.get("xsiNil") else None),
                            "decimals": anchor.get("decimals") if anchor else None,
                            "ancestors": (anchor.get("ancestors", []) if anchor else None),
                            "context_ref": anchor.get("contextRef") if anchor else None,
                            "id": anchor.get("id") if anchor else None,
                            "base_ref": anchor.get("baseRef") if anchor else None,
                            "url": (f"{self._url}{item}.htm" if item[0] == "R" else None),
                        }

                for item in list(res[key]["tag"]):
                    if res[key]["tag"].get(item):
                        _item = res[key]["tag"][item]
                        role = _item.get("lang", {}).get("en-US", {}).get("role", {}) or _item.get("lang", {}).get(
                            "en-us", {}
                        ).get("role", {})
                        calculation = res[key]["tag"][item].get("calculation", {})
                        calcs = {}
                        for k in calculation:
                            calcs["calculation"] = k.split("role/")[-1]
                            calcs.update(calculation[k])
                        presentation = [d.split("role/")[-1] for d in res[key]["tag"][item].get("presentation", [])]
                        tags[item] = {
                            "xbrl_type": res[key]["tag"][item].get("xbrltype"),
                            "name": res[key]["tag"][item].get("localname"),
                            "presentation": presentation,
                            "crdr": res[key]["tag"][item].get("crdr"),
                            **calcs,
                            **role,
                            "auth_ref": res[key]["tag"][item].get("auth_ref"),
                        }

            for k, v in statement_items.copy().items():
                if not v:
                    continue

                if (
                    v.get("short_name")
                    in (
                        "Cover Page",
                        "Document And Entity Information",
                    )
                    or v.get("menu_category") == "Cover"
                ):
                    self._cover_page_url = v.get("url", "") or self._cover_page_url

                tag = v.get("anchor_tag", "")

                if tag and tag in tags:
                    statement_items[k].update({k: v for k, v in tags[tag].items() if k != "tag"})

            self._resources.update(statement_items)
            self._tags.update(tags)

        except Exception as e:
            raise RuntimeError(f"Failed to parse MetaLinks.json: {e}") from e

    def _fetch_external_taxonomy_labels(self, imports: list):
        """Fetch labels from imported external taxonomies (us-gaap, srt, dei, etc.).

        Updates self._labels with documentation and labels from standard taxonomies.
        """
        for imp in imports:
            schema_location = imp.get("schemaLocation", "")
            label_url = get_label_url_for_import(schema_location)

            if not label_url:
                continue

            try:
                content = self.download_file(label_url)
                parser = XBRLParser()

                style = TaxonomyStyle.FASB_STANDARD if "fasb.org" in label_url else TaxonomyStyle.SEC_EMBEDDED

                external_labels = parser.parse_label_linkbase(io.BytesIO(content), style)

                for element_id, label_roles in external_labels.items():
                    if element_id not in self._labels:
                        self._labels[element_id] = {}
                    for role, value in label_roles.items():
                        if role not in self._labels[element_id]:
                            self._labels[element_id][role] = value

            except Exception:
                pass

    def _build_schema_from_xml(self):
        """Build the schema from the linkbase, definitions, labels, and calculations files."""
        # pylint: disable=import-outside-toplevel

        tags: dict = self._tags if self._tags else {}
        items: list = []

        xsd_url = [
            d.get("url")
            for d in self._document_urls
            if d.get("url", "").endswith(".xsd") or d.get("type", "") == "EX-101.SCH"
        ]

        if xsd_url:
            if not self._xsd:
                xsd_content = self.download_file(xsd_url[0])
                parser = XBRLParser()
                elements, roles, embedded_linkbase, imports = parser.parse_schema(io.BytesIO(xsd_content))

                self._xsd = {"elements": elements, "roles": roles, "imports": imports}

                for elem_id, elem_data in elements.items():
                    if elem_id not in tags:
                        tags[elem_id] = elem_data
                    else:
                        tags[elem_id].update(elem_data)

                doc_nums: set = set()
                for role in roles:
                    doc_num = role.get("document_number", "")
                    if doc_num and doc_num not in doc_nums:
                        doc_nums.add(doc_num)
                        items.append(role)

                if embedded_linkbase is not None:
                    try:
                        import xml.etree.ElementTree as ET

                        embedded_bytes = ET.tostring(embedded_linkbase, encoding="unicode").encode("utf-8")
                        embedded_parser = XBRLParser()
                        embedded_labels = embedded_parser.parse_label_linkbase(
                            io.BytesIO(embedded_bytes), TaxonomyStyle.SEC_EMBEDDED
                        )
                        for element_id, label_roles in embedded_labels.items():
                            if element_id not in self._labels:
                                self._labels[element_id] = {}
                            self._labels[element_id].update(label_roles)
                    except Exception:
                        pass

                self._fetch_external_taxonomy_labels(imports)

            else:
                elements = self._xsd.get("elements", {})
                roles = self._xsd.get("roles", [])
                for elem_id, elem_data in elements.items():
                    if elem_id not in tags:
                        tags[elem_id] = elem_data
                    else:
                        tags[elem_id].update(elem_data)
                doc_nums = set()
                for role in roles:
                    doc_num = role.get("document_number", "")
                    if doc_num and doc_num not in doc_nums:
                        doc_nums.add(doc_num)
                        items.append(role)

            r_num = 0
            items = sorted(items, key=lambda x: x.get("document_number", ""))

            statement_items: dict = self._resources if self._resources else {}

            for item in items:
                r_num += 1
                item["url"] = self._url + f"R{r_num}.htm"
                if not statement_items.get(f"r{r_num}"):
                    statement_items[f"r{r_num}"] = item

            self._resources.update(statement_items)

        linkbase_url = [
            d.get("url")
            for d in self._document_urls
            if d.get("description", "").endswith("LABEL LINKBASE DOCUMENT")
            or d.get("url", "").endswith("_lab.xml")
            or d.get("type", "") == "EX-101.LAB"
        ]

        if linkbase_url:
            content = self.download_file(linkbase_url[0])
            parser = XBRLParser()
            try:
                linkbase_labels = parser.parse_label_linkbase(io.BytesIO(content), TaxonomyStyle.FASB_STANDARD)
                for element_id, roles in linkbase_labels.items():
                    if element_id not in self._labels:
                        self._labels[element_id] = {}
                    for role, value in roles.items():
                        if role not in self._labels[element_id]:
                            self._labels[element_id][role] = value
            except Exception:
                pass

        for element_id, roles in self._labels.items():
            if element_id in tags:
                tags[element_id].update(roles)

        # Handle Presentation via XBRLParser
        presentation_url = [
            d.get("url")
            for d in self._document_urls
            if d.get("description", "").endswith("PRESENTATION LINKBASE DOCUMENT")
            or d.get("url", "").endswith("_pre.xml")
            or d.get("type", "") == "EX-101.PRE"
        ]

        if presentation_url:
            try:
                content = self.download_file(presentation_url[0])
                parser = XBRLParser()
                roots = parser.parse_presentation(io.BytesIO(content), TaxonomyStyle.FASB_STANDARD)

                def flatten_tree(nodes, parent_id=None):
                    for node in nodes:
                        tag = node.element_id
                        if tag not in tags:
                            tags[tag] = {}

                        tags[tag]["order"] = str(node.order)
                        if parent_id:
                            tags[tag]["parent_tag"] = parent_id

                        if node.preferred_label:
                            tags[tag]["preferred_label"] = node.preferred_label.split("/")[-1]

                        flatten_tree(node.children, tag)

                flatten_tree(roots)
                self._presentation = roots

            except Exception:  # pylint: disable=W0718
                pass

        # Calculations - using XBRLParser
        calcs_url = [
            d.get("url")
            for d in self._document_urls
            if d.get("description", "").endswith("CALCULATION LINKBASE DOCUMENT")
            or d.get("url", "").endswith("_cal.xml")
            or d.get("type", "") == "EX-101.CAL"
        ]

        if calcs_url:
            try:
                content = self.download_file(calcs_url[0])
                parser = XBRLParser()
                calc_data = parser.parse_calculation(io.BytesIO(content), TaxonomyStyle.FASB_STANDARD)

                for element_id, calc_info in calc_data.items():
                    if element_id in tags:
                        tags[element_id]["order"] = calc_info.get("order")
                        tags[element_id]["weight"] = calc_info.get("weight")
                        tags[element_id]["parent_tag"] = calc_info.get("parent_tag") or tags[element_id].get("parent_tag")
                    else:
                        tags[element_id] = calc_info

                self._calcs = calc_data

            except Exception:  # pylint: disable=W0718
                pass

        self._tags.update(tags)

    def _download_xbrl_instance(self):
        """Download the XBRL instance document."""
        instance_url = [
            d.get("url")
            for d in self._document_urls
            if d.get("description", "").endswith("INSTANCE DOCUMENT")
            or d.get("type", "") == "EX-101.INS"
            or d.get("url", "").endswith("_htm.xml")
        ]

        if instance_url:
            instance_content = self.download_file(instance_url[0])
            parser = XBRLParser()
            contexts, facts = parser.parse_instance(io.BytesIO(instance_content))

            if not contexts and not facts:
                return

            self._period_context = contexts

            new_instance_dict: dict = {}
            for tag, fact_list in facts.items():
                new_instance_dict[tag] = {"context": fact_list}

            self._instance.update(new_instance_dict)

            def find_tag_data(tag_key: str) -> dict:
                """Find tag metadata, trying multiple key formats."""
                if tag_key in self._tags:
                    tag_data = self._tags.get(tag_key, {})
                    if isinstance(tag_data, dict):
                        return tag_data.copy()

                if "_" in tag_key:
                    local_name = tag_key.split("_", 1)[1]
                    for tk, tv in self._tags.items():
                        if "_" in tk and tk.split("_", 1)[1] == local_name:
                            if isinstance(tv, dict):
                                return tv.copy()

                return {}

            for k, v in new_instance_dict.items():
                if "TextBlock" in k and v.get("context"):
                    tag = find_tag_data(k)
                    context_list = v.get("context", [])
                    if context_list and context_list[0].get("value"):
                        text_block = self._clean_html_to_text(context_list[0]["value"], keep_tables=True)
                        tag.update({"value": text_block})
                        self._text_blocks[k] = {
                            tk: tv
                            for tk, tv in tag.items()
                            if tk not in ("xsi_nil", "balance_type", "order", "xbrl_type")
                        }

    def _parse_non_xbrl_statement(self, statement: str):
        """Parse financial statements from non-XBRL (pre-2009) SEC filings.

        Parameters
        ----------
        statement : str
            The type of statement to extract: 'balance', 'income', 'cash', 'equity'

        Returns
        -------
        tuple
            (DataFrame, DataFrame) - statement data and metadata (empty for non-XBRL)
        """
        # pylint: disable=import-outside-toplevel
        import re

        from bs4 import BeautifulSoup
        from pandas import DataFrame, to_datetime

        statement_patterns = {
            "balance": [
                r"balance\s*sheet",
                r"financial\s*condition",
                r"financial\s*position",
            ],
            "income": [
                r"statement[s]?\s*of\s*earnings",
                r"statement[s]?\s*of\s*operations",
                r"statement[s]?\s*of\s*income",
                r"income\s*statement",
            ],
            "cash": [
                r"statement[s]?\s*of\s*cash\s*flows",
                r"cash\s*flow[s]?\s*statement",
            ],
            "equity": [
                r"statement[s]?\s*of\s*changes\s*in\s*(stockholders|shareholders)",
                r"statement[s]?\s*of\s*equity",
            ],
        }

        patterns = statement_patterns.get(statement, [])
        if not patterns:
            raise ValueError(f"Unknown statement type: {statement}")

        main_url = self.main_document_url
        if not main_url:
            raise ValueError("No main document URL found for this filing")

        content = self.download_file(main_url)
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="ignore")

        soup = BeautifulSoup(content, "lxml")

        def find_statement_tables():
            """Find tables that follow statement headers."""
            found_tables = []
            for tag in soup.find_all(["b", "strong", "font", "p", "div", "span"]):
                text = tag.get_text(strip=True).lower()
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE) and len(text) < 200:
                        next_table = tag.find_next("table")
                        if next_table:
                            rows = next_table.find_all("tr")
                            if len(rows) >= 8:
                                table_id = id(next_table)
                                if not any(id(t[1]) == table_id for t in found_tables):
                                    found_tables.append((text[:100], next_table, rows))
                        break
            return found_tables

        def parse_html_table(table_element):
            """Parse an HTML table into rows of cleaned data."""
            rows_data = []
            rows = table_element.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                row_values = []
                for cell in cells:
                    text = cell.get_text(separator=" ", strip=True)
                    text = re.sub(r"\s+", " ", text).strip()
                    colspan = int(cell.get("colspan", 1) or 1)
                    row_values.append(text)
                    for _ in range(colspan - 1):
                        row_values.append("")
                if any(row_values):
                    rows_data.append(row_values)
            return rows_data

        def clean_financial_table(rows_data):
            """Clean and structure the financial table data."""
            if not rows_data:
                return DataFrame()

            max_cols = max(len(row) for row in rows_data)
            for row in rows_data:
                while len(row) < max_cols:
                    row.append("")

            cols_to_keep = []
            for col_idx in range(max_cols):
                col_values = [row[col_idx].strip() for row in rows_data if col_idx < len(row)]
                if any(v for v in col_values):
                    cols_to_keep.append(col_idx)

            rows_data = [[row[i] if i < len(row) else "" for i in cols_to_keep] for row in rows_data]

            if not rows_data or not rows_data[0]:
                return DataFrame()

            df = DataFrame(rows_data)

            header_row_idx = 0
            for i, row in enumerate(rows_data[:5]):
                row_text = " ".join(str(v) for v in row).lower()
                if any(
                    month in row_text
                    for month in [
                        "january",
                        "february",
                        "march",
                        "april",
                        "may",
                        "june",
                        "july",
                        "august",
                        "september",
                        "october",
                        "november",
                        "december",
                        "ended",
                        "as of",
                        "months",
                    ]
                ):
                    header_row_idx = i
                    break

            if header_row_idx > 0:
                df = df.iloc[header_row_idx:].reset_index(drop=True)

            return df

        def extract_values_from_table(df):
            """Extract label-value pairs from the cleaned table."""
            if df.empty or df.shape[1] < 2:
                return DataFrame()

            result_rows = []
            periods = []
            for col_idx in range(1, min(df.shape[1], 10)):
                for row_idx in range(min(5, df.shape[0])):
                    cell = str(df.iloc[row_idx, col_idx]).strip()
                    date_match = re.search(
                        r"(january|february|march|april|may|june|july|august|"
                        r"september|october|november|december)\s*\d{1,2}?,?\s*\d{4}",
                        cell,
                        re.IGNORECASE,
                    )
                    if date_match:
                        try:
                            period_date = to_datetime(date_match.group()).strftime("%Y-%m-%d")
                            periods.append((col_idx, period_date))
                        except Exception:
                            periods.append((col_idx, cell))
                        break
                    year_match = re.match(r"^\d{4}$", cell.strip())
                    if year_match:
                        periods.append((col_idx, cell.strip()))
                        break

            if not periods:
                for col_idx in range(1, df.shape[1]):
                    periods.append((col_idx, f"Period_{col_idx}"))

            order = 0
            for row_idx in range(df.shape[0]):
                label = str(df.iloc[row_idx, 0]).strip()

                if not label or label.lower() in ["", "nan", "none"]:
                    continue

                if any(
                    h in label.lower()
                    for h in [
                        "months ended",
                        "as of",
                        "in millions",
                        "in thousands",
                        "$ in",
                        "shares in",
                        "(unaudited)",
                    ]
                ):
                    continue

                has_values = False
                for col_idx, period in periods:
                    if col_idx < df.shape[1]:
                        val = str(df.iloc[row_idx, col_idx]).strip()
                        clean_val = re.sub(r"[,$\s]", "", val)
                        clean_val = clean_val.replace("(", "-").replace(")", "")
                        if clean_val and (clean_val.replace("-", "").replace(".", "").isdigit()):
                            has_values = True
                            break

                if not has_values and not label.endswith(":"):
                    continue

                order += 1

                for col_idx, period in periods:
                    if col_idx < df.shape[1]:
                        val = str(df.iloc[row_idx, col_idx]).strip()
                        clean_val = re.sub(r"[,$\s]", "", val)
                        is_negative = "(" in val or clean_val.startswith("-")
                        clean_val = clean_val.replace("(", "").replace(")", "").replace("-", "")

                        if clean_val.replace(".", "").isdigit():
                            numeric_val = float(clean_val)
                            if is_negative:
                                numeric_val = -numeric_val
                        else:
                            numeric_val = None

                        result_rows.append(
                            {
                                "order": order,
                                "label": label,
                                "period_ending": period,
                                "value": (numeric_val if numeric_val is not None else val),
                                "raw_value": val,
                            }
                        )

            if not result_rows:
                return DataFrame()

            from numpy import nan as np_nan

            result_df = DataFrame(result_rows)

            result_df["tag"] = None
            result_df["parent_tag"] = None
            result_df["balance"] = None
            result_df["weight"] = None
            result_df["decimals"] = None
            result_df["context_ref"] = None
            result_df["period_beginning"] = None
            result_df["unit"] = "USD"

            cols = [
                "order",
                "tag",
                "parent_tag",
                "balance",
                "weight",
                "decimals",
                "context_ref",
                "period_beginning",
                "period_ending",
                "unit",
                "label",
                "value",
            ]
            result_df = result_df[[c for c in cols if c in result_df.columns]]

            return result_df.replace({np_nan: None})

        tables = find_statement_tables()

        if not tables:
            raise ValueError(
                f"Could not find {statement} statement in the filing. This may be a non-standard HTML format."
            )

        all_results = DataFrame()
        for _header, table_elem, _ in tables[:2]:
            raw_rows = parse_html_table(table_elem)
            cleaned_df = clean_financial_table(raw_rows)
            result = extract_values_from_table(cleaned_df)

            if not result.empty:
                all_results = (
                    result if all_results.empty else DataFrame(all_results.to_dict("records") + result.to_dict("records"))
                )

        meta_df = DataFrame(
            columns=[
                "tag",
                "taxonomy",
                "data_type",
                "balance_type",
                "period_type",
                "weight",
                "unit",
                "decimals",
                "name",
                "preferred_label",
                "parent_tag",
                "description",
            ]
        )

        return all_results.reset_index(drop=True), meta_df

    def _download_statement(self, statement: str):
        """Download the balance sheet belonging to the loaded statement."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta

        from numpy import nan
        from pandas import NA, DataFrame, DateOffset, concat, offsets, to_datetime

        # For non-XBRL filings, use the HTML parsing method
        if not self.is_xbrl:
            return self._parse_non_xbrl_statement(statement)

        statement_map = {
            "balance": "balance sheet",
            "cash": "cash flows",
            "income": "income",
            "operations": "operations",
            "equity": "equity",
            "financial_conditions": "financial condition",
        }

        statements = self.statements.copy()

        if statement == "income":
            urls = [v for k, v in statements.items() if "operations" in k.lower() or "income" in k.lower()]
        elif statement == "balance":
            urls = [v for k, v in statements.items() if "balance" in k.lower() or "condition" in k.lower()]
        else:
            urls = [v for k, v in statements.items() if statement_map.get(statement) in k.lower()]

        if not urls:
            raise ValueError(
                f"No items found in the filing, cannot proceed with document type:"
                f" {self.document_type} and statement: {statement}"
                f" -> {self.document_type} -> {self.statements}"
            )
        output_statement = DataFrame()
        output_meta = DataFrame()
        col1_name = ""
        try:
            for url in urls:
                table, item_map = self._download_statement_from_url(url, is_equity=statement == "equity")

                if not table.empty:
                    col1_name = col1_name if col1_name else table.columns[0]
                    table.columns = [col1_name] + table.columns[1:].tolist()
                    output_statement = concat([output_statement, table], axis=0) if not output_statement.empty else table

                if not item_map.empty:
                    item_map = item_map.dropna(how="all", axis=1)
                    output_meta = item_map if output_meta.empty else concat([output_meta, item_map], axis=0)
        except Exception as e:
            raise RuntimeError(f"Failed to download statement: {e} -> {e.args}") from e

        output_statement = output_statement.reset_index(drop=True)
        statement_cols = output_statement.columns.tolist()

        if statement != "equity":
            output_statement.columns = ["label"] + statement_cols[1:]

            if not output_meta.empty:
                output_meta = output_meta.reset_index(drop=True)
                output_meta = output_meta.rename(
                    columns={
                        "Name": "tag",
                        "Namespace Prefix": "taxonomy",
                        "Data Type": "data_type",
                        "Balance Type": "balance_type",
                        "Period Type": "period_type",
                    }
                )
                output_meta.data_type = output_meta.data_type.astype(str).apply(
                    lambda x: x.split(":")[-1] if x and isinstance(x, str) else x
                )

        try_order = [
            "totalLabel",
            "negatedPeriodStartLabel",
            "negatedPeriodEndLabel",
            "periodStartLabel",
            "periodEndLabel",
            "negatedTerseLabel",
            "terseLabel",
            "negatedLabel",
            "label",
            "verboseLabel",
        ]
        instance_dict = self._instance.copy()
        tags = self.tags.copy()

        def normalize_instance_key(instance_key: str) -> str:
            """Normalize an instance key to match the canonical tag format."""
            if instance_key in tags:
                return instance_key
            if "_" in instance_key:
                local_name = instance_key.split("_", 1)[1]
                for tag_key in tags:
                    if "_" in tag_key and tag_key.split("_", 1)[1] == local_name:
                        return tag_key
            return instance_key

        value_to_tags: dict = {}
        for tag_key, data in instance_dict.items():
            normalized_key = normalize_instance_key(tag_key)
            contexts = data.get("context", [])
            for ctx in contexts:
                ctx_value = ctx.get("value", "")
                if ctx_value and ctx_value.replace("-", "").replace(".", "").isdigit():
                    try:
                        abs_val = abs(float(ctx_value))
                        if abs_val not in value_to_tags:
                            value_to_tags[abs_val] = []
                        if normalized_key not in value_to_tags[abs_val]:
                            value_to_tags[abs_val].append(normalized_key)
                    except ValueError:
                        continue

        def apply_label(x):
            """Apply a label to the column by matching against tag labels."""
            for key, value in tags.items():
                for match in try_order:
                    if value.get(match, "").lower() == x.lower():
                        return key
            return None

        def apply_parent_tag(x):
            """Apply a parent tag to the column."""
            if parent_tag := tags.get(x, {}).get("parentTag") or tags.get(x, {}).get("parent_tag"):
                return parent_tag

            if not output_meta.empty and hasattr(output_meta, "parent_tag"):
                new_value = output_meta[output_meta.tag == x].parent_tag
                if not new_value.empty:
                    return new_value.values[0]

            return None

        def check_unit(x):
            """Check the unit string."""
            if not x or x in ("na", "n"):
                return None
            if x.lower().startswith(("unit", "u_")):
                units = x.split("_")
                if units and len(units) > 2:
                    if units and units[1].lower() == "standard":
                        return units[2]
                    if units[1].lower() == "divide":
                        return units[2] + "per" + units[3].title()
                if units and len(units) == 2 and (len(units[1]) == 3 or units[1] in ["shares", "pure"]):
                    return units[1]
            return x

        def apply_unit(x):
            """Apply a unit to the column."""
            if not x or x in ("na", "n"):
                return None
            if not output_meta.empty and hasattr(output_meta, "unit"):
                new_value = output_meta[output_meta.tag == x].unit
                if not new_value.empty:
                    return check_unit(new_value.values[0])

            instance = instance_dict.get(x, {}).get("context", [])
            if not instance or len(instance) < 1:
                return None
            unit = instance[0].get("unit")
            if unit:
                return check_unit(unit)
            return None

        def apply_decimals(x):
            """Apply a decimals to the column."""
            if not output_meta.empty and hasattr(output_meta, "decimals"):
                new_value = output_meta[output_meta.tag == x].decimals
                if not new_value.empty:
                    return new_value.values[0]

            instance = instance_dict.get(x, {}).get("context", [])
            if not instance or len(instance) < 1:
                return None
            decimals = instance[0].get("decimals")
            if decimals:
                return decimals
            return None

        def apply_balance(x):
            """Apply a balance type to the column."""
            if balance := tags.get(x, {}).get("crdr"):
                return balance
            if not output_meta.empty and hasattr(output_meta, "balance_type"):
                new_value = output_meta[output_meta.tag == x].balance_type
                if not new_value.empty and new_value.values[0] not in ("n", "na"):
                    return new_value.values[0]
            return None

        def apply_weight(x):
            """Apply a weight to the column."""
            if weight := tags.get(x, {}).get("weight"):
                return weight
            if not output_meta.empty and hasattr(output_meta, "weight"):
                new_value = output_meta[output_meta.tag == x].weight
                if not new_value.empty:
                    return new_value.values[0]
            return None

        def check_values(tag) -> list:
            """Check the value of the tag."""
            value = instance_dict.get(tag, {}).get("context", [])
            if not value or len(value) < 1:
                return []
            return [abs(float(v.get("value"))) for v in value if v.get("value") and v.get("value", "").isnumeric()]

        def apply_fix_tag(row):
            """Verify and fix initial tags applied from the label."""
            nonlocal statement

            old_tag = row.tag
            label = row.label
            row_value = row.value if hasattr(row, "value") else row.Total if hasattr(row, "Total") else None
            if not row_value or row_value == "--":
                return row

            row_value = abs(float(row_value))
            potential_values = check_values(old_tag)

            if row_value in potential_values:
                return row

            matching_keys = value_to_tags.get(row_value, [])

            if not matching_keys:
                return row

            if len(matching_keys) == 1:
                row.tag = matching_keys[0]
                return row

            if statement == "equity" and matching_keys:
                row.tag = matching_keys[0]
                return row

            for key in matching_keys:
                if key in tags:
                    for match in try_order:
                        if tags[key].get(match, "").lower() == label.lower():
                            row.tag = key
                            return row

            label_lower = label.lower()
            label_words = set(w for w in label_lower.split() if len(w) > 3)

            for key in matching_keys:
                if key in tags:
                    for match in try_order:
                        tag_label = tags[key].get(match, "").lower()
                        if tag_label:
                            tag_words = set(w for w in tag_label.split() if len(w) > 3)
                            if label_words and tag_words and len(label_words & tag_words) >= 2:
                                row.tag = key
                                return row

            for key in matching_keys:
                if key in tags:
                    local_name = key.split("_", 1)[1] if "_" in key else key
                    import re as re_inner

                    tag_name_words = set(w.lower() for w in re_inner.findall(r"[A-Z][a-z]+", local_name) if len(w) > 3)
                    if label_words and tag_name_words and len(label_words & tag_name_words) >= 2:
                        row.tag = key
                        return row

            tags_matching = [k for k in matching_keys if k in tags]
            if len(tags_matching) == 1:
                row.tag = tags_matching[0]
                return row

            return row

        def get_instance_context(tag_key: str) -> list:
            """Get context list from instance_dict, trying multiple key formats."""
            if tag_key in instance_dict:
                return instance_dict[tag_key].get("context", [])
            if "_" in tag_key:
                local_name = tag_key.split("_", 1)[1]
                for inst_key, inst_data in instance_dict.items():
                    if "_" in inst_key and inst_key.split("_", 1)[1] == local_name:
                        return inst_data.get("context", [])
            return []

        def apply_context_ref(row):
            """Apply a context reference to the column."""
            tag = row.tag
            value = row.value
            context = get_instance_context(tag)
            period_type = None

            if output_meta is not None and not output_meta.empty and hasattr(output_meta, "period_type"):
                period_type = output_meta[output_meta.tag == tag].period_type

            period_type = period_type.values[0] if period_type is not None and not period_type.empty else None

            if not context or len(context) < 1:
                return None

            if value and value != "--":
                for c in context:
                    if not c:
                        continue
                    con = c.get("context_ref", "")
                    if not con:
                        continue
                    val = c.get("value")
                    if not val or val == "--":
                        continue
                    try:
                        if val and "--" not in str(val) and abs(float(val)) == abs(float(value)):
                            return con
                    except (ValueError, TypeError):
                        continue

            return None

        if statement == "equity":
            output_statement.columns = ["label"] + output_statement.columns[1:].tolist()
            output_statement["tag"] = output_statement.apply(lambda row: apply_label(row["label"]), axis=1)
            return output_statement.replace({nan: None}), output_meta.replace({nan: None})

        output_statement.reset_index(drop=False, inplace=True)
        output_statement.rename(columns={"index": "order"}, inplace=True)
        output_statement.order = output_statement.order.apply(lambda x: x + 1)
        output_statement.loc[:, "tag"] = output_statement.apply(lambda row: apply_label(row["label"]), axis=1)

        flattened_output = output_statement.melt(
            id_vars=["order", "tag", "label"],
            var_name="period_ending",
            value_name="value",
        )

        flattened_output = flattened_output.apply(apply_fix_tag, axis=1)
        flattened_output.loc[:, "context_ref"] = flattened_output.apply(apply_context_ref, axis=1)

        def apply_dimension_label(row):
            """Apply the correct label based on dimension members in context_ref."""
            context_ref = row.context_ref if hasattr(row, "context_ref") else None
            if not context_ref or not isinstance(context_ref, str):
                return row.label

            generic_labels = {
                "net sales and revenues",
                "revenues",
                "net sales and revenue",
                "revenue",
                "sales and revenues",
                "sales",
            }

            if row.label.lower() not in generic_labels:
                return row.label

            import re

            member_pattern = r"([a-z\-]+)_([A-Za-z]+Member)"
            matches = re.findall(member_pattern, context_ref)

            if not matches:
                return row.label

            for prefix, member_name in matches:
                member_key = f"{prefix}_{member_name}"
                member_info = tags.get(member_key, {})
                terse_label = member_info.get("terseLabel")
                if terse_label and terse_label.lower() != row.label.lower():
                    return terse_label

            return row.label

        flattened_output.loc[:, "label"] = flattened_output.apply(apply_dimension_label, axis=1)

        output_statement = (
            flattened_output.copy()
            .dropna(how="all", axis=1)
            .sort_values(
                by=["order", "period_ending"],
                ascending=[True, False],
            )
        )

        output_statement.loc[:, "parent_tag"] = output_statement.tag.apply(apply_parent_tag)
        output_statement.loc[:, "unit"] = output_statement.tag.apply(apply_unit)
        output_statement.loc[:, "decimals"] = output_statement.tag.apply(apply_decimals)
        output_statement.loc[:, "balance"] = output_statement.tag.apply(apply_balance)
        output_statement.loc[:, "weight"] = output_statement.tag.apply(apply_weight)

        def apply_preferred_label(x):
            """Apply a preferred label to the column."""
            if preferred := tags.get(x, {}).get("preferred_label"):
                return preferred
            if not output_meta.empty and hasattr(output_meta, "preferred_label"):
                new_value = output_meta[output_meta.tag == x].preferred_label
                if not new_value.empty:
                    return new_value.values[0]
            return None

        output_statement.loc[:, "preferred_label"] = output_statement.tag.apply(apply_preferred_label)

        def apply_period_beginning(row):
            """Apply a period beginning to the column."""
            context = row.context_ref if hasattr(row, "context_ref") else None
            if not context or not isinstance(context, str):
                return None

            period_start = ""
            if context:
                if context.lower().startswith("as_of"):
                    return period_start
                if context.lower().startswith("duration"):
                    start_date = "_".join(context.split("_")[1:4]).replace("_", "-")
                    start_date = to_datetime(start_date).strftime("%Y-%m-%d")
                    return start_date

                period_start = self._period_context.get(context, {}).get("start")
                if not period_start and (
                    len("_".join(context.split("_")[:3])) == 23
                    or (context[2] == "_" and len("_".join(context.split("_")[:2])) == 12)
                ):
                    period_start = context.split("_")[1]

                if period_start:
                    return period_start
            if row.value and row.value != "--" and " -- " in row.period_ending:
                period_end = row.period_ending
                period_months = period_end.split(" -- ")[-1][0]
                period_end = to_datetime(period_end.split(" -- ")[0])
                period_start = (
                    period_end - DateOffset(months=int(period_months)) + offsets.MonthEnd(0) + offsets.MonthBegin(1)
                ).strftime("%Y-%m-%d")
                return period_start

            if row.value and row.value != "--" and row.period_ending and self.document_type == "10-K":
                period_end = to_datetime(row.period_ending.split(" -- ")[0])
                period_start = (period_end.replace(year=period_end.year - 1) + timedelta(days=1)).strftime("%Y-%m-%d")
                return period_start

            return None

        def apply_fix_period_end(row):
            """Apply a period ending to the column."""
            con_ref = row.context_ref if hasattr(row, "context_ref") else None
            if row.period_beginning or con_ref or " -- " in row.period_ending:
                period_end = row.period_ending.split(" -- ")[0]
                row.period_ending = period_end

            con_ref = row.context_ref

            if (con_ref and row.period_beginning and " -- " not in row.period_ending) or row.value == "--":
                return row

            if row.period_beginning and row.period_ending and row.tag and not con_ref:
                begin = to_datetime(row.period_beginning)
                end = to_datetime(row.period_ending)
                n_months = (end.year - begin.year) * 12 + end.month - begin.month + 1
                row.context_ref = f"{n_months} Months Ended"

            return row

        output_statement.loc[:, "period_beginning"] = output_statement.apply(apply_period_beginning, axis=1)
        output_statement = output_statement.apply(apply_fix_period_end, axis=1)

        output_statement = output_statement[
            [
                "order",
                "tag",
                "parent_tag",
                "preferred_label",
                "balance",
                "weight",
                "decimals",
                "context_ref",
                "period_beginning",
                "period_ending",
                "unit",
                "label",
                "value",
            ]
        ]

        output_statement = output_statement.sort_values(
            by=["order", "period_ending", "period_beginning"],
            ascending=[True, False, False],
        )

        output_statement = output_statement.drop_duplicates(subset=["tag", "value", "period_ending"], keep="first")

        tag_min_order = output_statement.groupby("tag")["order"].min().to_dict()
        output_statement["_tag_order"] = output_statement["tag"].map(tag_min_order)

        output_statement = output_statement.sort_values(
            by=["_tag_order", "order", "period_ending", "period_beginning"],
            ascending=[True, True, False, False],
        )

        unique_items = output_statement.drop_duplicates(subset=["tag", "label"]).copy()
        new_order_map = {(row.tag, row.label): i + 1 for i, row in enumerate(unique_items.itertuples())}
        output_statement["order"] = output_statement.apply(
            lambda row: new_order_map.get((row.tag, row.label), row.order), axis=1
        )

        output_statement = output_statement.drop(columns=["_tag_order"])
        output_statement = output_statement.sort_values(
            by=["order", "period_ending", "period_beginning"],
            ascending=[True, False, False],
        )

        # Enrich output_meta with missing tags
        statement_tags = set(output_statement.tag.dropna().unique())
        meta_tags = set(output_meta.tag.unique()) if not output_meta.empty and "tag" in output_meta.columns else set()
        missing_tags = statement_tags - meta_tags

        if missing_tags:
            new_rows = []
            for tag in missing_tags:
                tag_info = tags.get(tag, {})
                taxonomy = tag.split("_")[0] if "_" in tag else None
                new_row = {
                    "tag": tag,
                    "taxonomy": taxonomy,
                    "data_type": tag_info.get("xbrl_type"),
                    "balance_type": tag_info.get("crdr"),
                    "period_type": tag_info.get("period_type"),
                    "weight": tag_info.get("weight"),
                    "unit": None,
                    "decimals": None,
                    "name": tag_info.get("name"),
                    "preferred_label": tag_info.get("preferred_label"),
                    "parent_tag": tag_info.get("parentTag") or tag_info.get("parent_tag"),
                    "description": tag_info.get("documentation"),
                }
                instance_data = instance_dict.get(tag, {}).get("context", [])
                if instance_data:
                    new_row["unit"] = check_unit(instance_data[0].get("unit"))
                    new_row["decimals"] = instance_data[0].get("decimals")
                new_rows.append(new_row)

            if new_rows:
                missing_df = DataFrame(new_rows)
                output_meta = concat([output_meta, missing_df], axis=0, ignore_index=True)

        def format_value(x):
            if x is None or x in {"--", ""}:
                return None
            try:
                f = float(x)
                if f == int(f):
                    return int(f)
                return f
            except (ValueError, TypeError):
                return x

        output_statement["value"] = output_statement["value"].apply(format_value)

        return output_statement.replace({NA: None, nan: None, "": None}).reset_index(drop=True), output_meta.replace(
            {NA: None, nan: None, "": None}
        ).reset_index(drop=True)

    def _download_statement_from_url(self, url, is_equity: bool = False):
        """Download a financial statement file from a SEC URL."""
        # pylint: disable=import-outside-toplevel
        import re

        from pandas import DataFrame, MultiIndex, concat, isnull, to_datetime

        tables = self.download_file(url, read_html_table=True)

        df = tables[0].copy()  # type: ignore

        df1 = DataFrame()
        df2 = DataFrame()

        is_multiindex = len(df.columns) == 5 or isinstance(df.columns[1], tuple)

        if is_multiindex and self.document_type == "10-K" and len(df.columns) == 5:
            df = df.iloc[:, [0, 2, 3, 4]].copy()

        is_annual_multi = len(df.columns) == 4 and isinstance(df.columns, MultiIndex)

        if is_annual_multi:
            df1 = df.copy()
            self._period_end1 = df1.columns[1][0]
            df1.columns = df.columns.droplevel(0)
        elif is_multiindex:
            if len(df.columns) == 5:
                df1 = df.iloc[:, :3].copy()
                self._period_end1 = df1.columns[1][0]
                df2 = df.iloc[:, [0, 3, 4]].copy()
                self._period_end2 = df2.columns[1][0]
            elif len(df.columns) == 3:
                df1 = df.copy()
                self._period_end1 = df.columns[1][0]
                df1.columns = df.columns.droplevel(0)
        else:
            if df.columns[0] == df.columns[1].replace(".1", ""):  # type: ignore
                df = df.drop(columns=[df.columns[1]])
            df1 = df
            self._period_end1 = "12 Months Ended"

        def _process_statement(self, statement):
            """Process the statement."""
            nonlocal is_equity

            period_end = (
                self._period_end2
                if hasattr(self, "_period_end2") and self._period_end2 and self._period_end2.lower().endswith("ended")
                else None
            ) or (
                self._period_end1
                if hasattr(self, "_period_end1") and self._period_end1 and self._period_end1.lower().endswith("ended")
                else None
            )

            if isinstance(statement.columns, MultiIndex):
                period_end = statement.columns[1][0]
                statement.columns = [d[1] for d in statement.columns]

            multiplier_str = statement.columns[0].split("$ in ")[-1] if "$ in " in statement.columns[0] else ""
            shares_multiplier_str = (
                statement.columns[0].split(" shares in ")[-1].split(",")[0]
                if " shares in " in statement.columns[0].lower()
                else ""
            )

            multiplier = self._multiplier_map(multiplier_str) if multiplier_str else 1
            shares_multiplier = self._multiplier_map(shares_multiplier_str) if shares_multiplier_str else 1

            pattern = re.compile(
                r"\(in [a-zA-Z] per share\)|per share -|weighted average number of",
                re.IGNORECASE,
            )
            pattern_shares = re.compile(
                r"(shares authorized|shares issued|shares outstanding)$",
                re.IGNORECASE,
            )

            def clean_col(x):
                """Clean a column name."""
                if str(x).startswith("["):
                    return None
                new_str = str(x).replace("(", "-").replace(")", "").replace(",", "").replace("$", "").replace(" ", "")
                try:
                    return float(new_str)
                except ValueError:
                    return None

            mask = ~statement.iloc[:, 0].astype(str).str.match(r"^\[\d+\]")
            statement = statement[mask].reset_index(drop=True)

            if not is_equity:
                value_cols = statement.columns[1:]
                for col in value_cols:
                    statement[col] = statement[col].replace("--", float("nan"))
                statement = statement.dropna().reset_index(drop=True)

            def format_date(x):
                """Format a date."""
                if not x:
                    return None
                date_part = " ".join(x.split()[:3])
                return to_datetime(date_part).strftime("%Y-%m-%d")

            # pylint: disable=W0640
            for col in statement.columns[1:]:
                statement[col] = statement[col].apply(clean_col)
                statement[col] = statement.apply(
                    lambda row: (
                        int(row[col] * shares_multiplier)
                        if not isnull(row[col])
                        and (
                            "(in shares)" in row[statement.columns[0]].lower()
                            or pattern_shares.search(row[statement.columns[0]].lower())
                        )
                        and (
                            not pattern.search(str(row[statement.columns[0]]).lower())
                            and "(in dollars per share)" not in str(row[statement.columns[0]]).lower()
                        )
                        else (
                            float(row[col])
                            if not isnull(row[col])
                            and pattern.search(str(row[statement.columns[0]]).lower())
                            or "(in dollars per share)" in str(row[statement.columns[0]]).lower()
                            else (
                                int(

                                        row[col] * multiplier
                                        if not pattern.search(str(row[statement.columns[0]]).lower())
                                        else row[col]

                                )
                                if not isnull(row[col])
                                else "--"
                            )
                        )
                    ),
                    axis=1,
                )

            col_1 = statement.columns[0]
            col_1 = col_1.split(" $ in ")[0]
            if period_end:
                statement.columns = (
                    statement.columns
                    if is_equity is True
                    else [col_1] + [f"{format_date(d)} -- {period_end}" for d in statement.columns[1:].tolist()]
                )
            else:
                statement.columns = (
                    statement.columns
                    if is_equity is True
                    else [col_1] + [format_date(d) for d in statement.columns[1:].tolist()]
                )

            item_map = DataFrame()

            for table in tables[1:]:
                df = table.set_index(0).T  # type: ignore
                df.columns = [d.replace(":", "") for d in df.columns]
                item_map = concat([item_map, df], axis=0) if not item_map.empty else df

            if not item_map.empty:
                item_map = item_map.reset_index(drop=True)

            instance_dict = self._instance.copy()
            tags = self._tags.copy()

            def map_units(x):
                """Map the units to a multiplier."""
                instance = instance_dict.get(x, {}).get("context", [])
                if not instance or len(instance) < 1:
                    return None
                unit = instance[0].get("unit")
                if not unit:
                    return None
                return unit

            def map_decimals(x):
                """Map the decimals to a number."""
                instance = instance_dict.get(x, {}).get("context", [])
                if not instance or len(instance) < 1:
                    return None
                decimals = instance[0].get("decimals")
                if not decimals:
                    return None
                return decimals

            def apply_parent_tag(x):
                """Apply a parent tag to the column."""
                tag = tags.get(x, {})
                parent_tag = tag.get("parentTag") or tag.get("parent_tag")
                if parent_tag:
                    return parent_tag
                return None

            if is_equity is False:
                item_map.loc[:, "weight"] = item_map.Name.apply(lambda x: self.tags.get(x, {}).get("weight"))
                item_map.loc[:, "unit"] = item_map.Name.apply(map_units)
                item_map.loc[:, "decimals"] = item_map.Name.apply(map_decimals)
                item_map.loc[:, "Balance Type"] = item_map["Balance Type"].apply(
                    lambda x: str(x).replace("na", "") if x else None
                )
                item_map.loc[:, "name"] = item_map.Name.apply(lambda x: self.tags.get(x, {}).get("name"))
                item_map.loc[:, "preferred_label"] = item_map.Name.apply(
                    lambda x: self.tags.get(x, {}).get("preferred_label")
                )
                item_map.loc[:, "parent_tag"] = item_map.Name.apply(apply_parent_tag)
                item_map.loc[:, "description"] = item_map.Name.apply(lambda x: self.tags.get(x, {}).get("documentation"))
                for col in item_map.columns:
                    if col.startswith("["):
                        item_map = item_map.drop(columns=col)
                    else:
                        item_map[col] = item_map[col].apply(
                            lambda x: (x if x and str(x).strip() not in ["na", "n", "nan"] else None)
                        )

            return statement, item_map.dropna()

        merged_df = DataFrame()
        merged_meta = DataFrame()

        if not df2.empty:
            for data in [df1, df2]:
                statement, item_map = _process_statement(self, data)
                statement.set_index(statement.columns[0], inplace=True)
                merged_df = concat([merged_df, statement], axis=1) if not merged_df.empty else statement
                merged_meta = concat([merged_meta, item_map], axis=0) if not merged_meta.empty else item_map
            merged_df = merged_df.reset_index()
            merged_meta = merged_meta.reset_index(drop=True)
        else:
            return _process_statement(self, df1)

        return merged_df, merged_meta


async def get_form10_urls_by_symbol(symbol: str, use_cache: bool = True) -> list:
    """Get Form 10-K/Q URLs by symbol.

    This function uses the SecCompanyFilingsFetcher to filter 10-Q/K filings.

    Parameters
    ----------
    symbol : str
        The ticker symbol of the company.
    use_cache : bool, optional
        Whether to use cached data, by default True.

    Returns
    -------
    list
        A list of dictionaries containing filing date, period ending, filing type, and URL.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_sec.models.company_filings import SecCompanyFilingsFetcher

    filings_fetcher = SecCompanyFilingsFetcher()
    params = {"symbol": symbol, "form_type": "10-Q,10-K", "use_cache": use_cache}

    filings = await filings_fetcher.fetch_data(params, {})

    form_10s: list = []

    for filing in filings:
        form_10s.append(
            {
                "filing_date": filing.filing_date,  # type: ignore
                "period_ending": filing.report_date,  # type: ignore
                "filing_type": filing.report_type,  # type: ignore
                "url": filing.report_url,  # type: ignore
            }
        )

    return form_10s
