"""SEC Filing Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Optional, Union

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
        default="",
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
    trading_symbols: Optional[list] = Field(
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
    period_ending: Optional[dateType] = Field(
        default=None,
        title="Period Ending",
        description="Date of the ending period for the filing, if available.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    fiscal_year_end: Optional[str] = Field(
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
    description: Optional[str] = Field(
        default=None,
        title="Content Description",
        description="Description of attached content, mostly applicable to 8-K filings.",
        json_schema_extra={"x-widget_config": {"exclude": True}},
    )
    cover_page: Optional[dict] = Field(
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


class SecBaseFiling(Data):  # pylint: disable=too-many-instance-attributes
    """Base SEC Filing model."""

    _url: str = PrivateAttr(default="")
    _index_headers_url: str = PrivateAttr(default="")
    _index_headers_download: str = PrivateAttr(default="")
    _document_urls: list = PrivateAttr(default=None)
    _filing_date: str = PrivateAttr(default="")
    _period_ending: str = PrivateAttr(default="")
    _document_type: str = PrivateAttr(default="")
    _name: str = PrivateAttr(default="")
    _cik: str = PrivateAttr(default="")
    _sic: str = PrivateAttr(default="")
    _sic_organization_name: Optional[str] = PrivateAttr(default="")
    _description: Optional[str] = PrivateAttr(default=None)
    _cover_page_url: Optional[str] = PrivateAttr(default=None)
    _fiscal_year_end: str = PrivateAttr(default="")
    _fiscal_period: str = PrivateAttr(default="")
    _cover_page: dict = PrivateAttr(default=None)
    _trading_symbols: list = PrivateAttr(default=None)
    _use_cache: bool = PrivateAttr(default=True)

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

    @computed_field(  # type: ignore
        title="Trading Symbols", description="Trading symbols, if available."
    )
    @property
    def trading_symbols(self) -> Optional[list]:
        """Trading symbols, if available."""
        return self._trading_symbols

    @computed_field(title="SIC", description="Standard Industrial Classification.")  # type: ignore
    @property
    def sic(self) -> str:
        """Standard Industrial Classification."""
        return self._sic

    @computed_field(title="SIC Organization", description="SIC Organization Name.")  # type: ignore
    @property
    def sic_organization_name(self) -> Optional[str]:
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
    def period_ending(self) -> Optional[dateType]:
        """Date of the ending period for the filing."""
        if self._period_ending:
            return dateType.fromisoformat(self._period_ending)
        return None

    @computed_field(  # type: ignore
        title="Fiscal Year End",
        description="Fiscal year end of the entity, if available. Format: MM-DD",
    )
    @property
    def fiscal_year_end(self) -> Optional[str]:
        """Fiscal year end date of the entity."""
        return self._fiscal_year_end

    @computed_field(title="Document Type", description="Specific SEC filing type.")  # type: ignore
    @property
    def document_type(self) -> str:
        """Document type."""
        return self._document_type

    @computed_field(  # type: ignore
        title="Has Cover Page", description="True if the filing has a cover page."
    )
    @property
    def has_cover_page(self) -> bool:
        """True if the filing has a cover page."""
        return bool(self._cover_page_url)

    @computed_field(  # type: ignore
        title="Cover Page", description="Cover page information, if available."
    )
    @property
    def cover_page(self) -> Optional[dict]:
        """Cover page information, if available."""
        return self._cover_page

    @computed_field(  # type: ignore
        title="Content Description",
        description="Description of attached content, mostly applicable to 8-K filings.",
    )
    @property
    def description(self) -> Optional[str]:
        """Document description, if available."""
        return self._description

    @computed_field(  # type: ignore
        title="Document URLs", description="List of files associated with the filing."
    )
    @property
    def document_urls(self) -> list:
        """List of document URLs."""
        return self._document_urls

    def __init__(self, url: str, use_cache: bool = True):
        """Initialize the Filing class."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import run_async
        from openbb_sec.utils.helpers import cik_map

        super().__init__()

        if not url:
            raise ValueError("Please enter a URL.")

        if "/data/" not in url:
            raise ValueError("Invalid SEC URL supplied, must be a filing URL.")

        check_val: str = url.split("/data/")[1].split("/")[1]

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

        if self.has_cover_page and not self._cover_page:
            self._download_cover_page()

        if not self._trading_symbols:
            symbol = run_async(cik_map, self._cik)
            if symbol:
                self._trading_symbols = [symbol]

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

        response: Union[dict, list, str, None] = None
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
            response = run_async(SecBaseFiling._adownload_file, url, use_cache)

            if read_html_table is True:
                if not url.endswith(".htm") and not url.endswith(".html"):
                    warn(f"File is not a HTML file: {url}")
                    return response

                return SecBaseFiling.try_html_table(response)

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
    ):  # pylint: disable=too-many-branches, too-many-statements, too-many-locals
        """Download the index headers table."""
        # pylint: disable=import-outside-toplevel
        import re  # noqa
        from bs4 import BeautifulSoup

        try:
            if not self._index_headers_download:
                response = self.download_file(
                    self._index_headers_url, False, self._use_cache
                )
                self._index_headers_download = response
            else:
                response = self._index_headers_download

            soup = BeautifulSoup(response, "html.parser")
            text = soup.find("pre").text

            def document_to_dict(doc):
                """Convert the document section to a dictionary."""
                doc_dict: dict = {}
                doc_dict["type"] = re.search(r"<TYPE>(.*?)\n", doc).group(1).strip()  # type: ignore
                doc_dict["sequence"] = (
                    re.search(r"<SEQUENCE>(.*?)\n", doc).group(1).strip()  # type: ignore
                )
                doc_dict["filename"] = (
                    re.search(r"<FILENAME>(.*?)\n", doc).group(1).strip()  # type: ignore
                )
                description_match = re.search(r"<DESCRIPTION>(.*?)\n", doc)

                if description_match:
                    doc_dict["description"] = description_match.group(1).strip()

                url = self.base_url + doc_dict["filename"]
                doc_dict["url"] = url

                return doc_dict

            # Isolate each document by tag
            documents = re.findall(r"<DOCUMENT>.*?</DOCUMENT>", text, re.DOTALL)
            # Convert each document to a dictionary
            document_dicts = [document_to_dict(doc) for doc in documents]

            if document_dicts:
                self._document_urls = document_dicts

            lines = text.split("\n")
            n_items = 0

            for line in lines:

                if ":" not in line:
                    continue

                value = line.split(":")[1].strip()

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
                # There might be two lines of ITEM INFORMATION
                elif "ITEM INFORMATION" in line:
                    info = value
                    self._description = (
                        self._description + "; " + info if self._description else info
                    )
                    n_items += 1
                continue

        except Exception as e:
            raise RuntimeError(
                f"Failed to download and read the index headers table: {e}"
            ) from e

    @staticmethod
    def _multiplier_map(string) -> int:  # pylint: disable=too-many-return-statements
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
    ):  # pylint: disable=too-many-branches, too-many-statements, too-many-locals
        """Download the cover page table."""
        # pylint: disable=import-outside-toplevel
        from pandas import MultiIndex, to_datetime

        symbols_list: list = []
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

            if not fiscal_year.empty:
                fiscal_year = fiscal_year.iloc[:, 1].values[0]
            elif fiscal_year.empty:
                fiscal_year = None

            if fiscal_year:
                self._fiscal_year = fiscal_year

            fiscal_period = df[df.iloc[:, 0] == "Document Fiscal Period Focus"]

            if not fiscal_period.empty:
                fiscal_period = fiscal_period.iloc[:, 1].values[0]
            elif fiscal_period.empty:
                fiscal_period = None

            if fiscal_period:
                self._fiscal_period = fiscal_period

            title = (
                df.columns[0][0]
                if isinstance(df.columns, MultiIndex)
                else df.columns[0]
            )

            if title and "- shares" in title:
                shares_multiplier = title.split(" shares in ")[-1]
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
                        to_datetime(as_of_date).strftime("%Y-%m-%d"): int(
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
                symbols_dict: dict = {}
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
                if trading_symbols:
                    self._trading_symbols = sorted(
                        [d for d in trading_symbols if d and d != "No Trading Symbol"]
                    )
                    symbols_dict = dict(zip(symbol_names, trading_symbols))
                    exchanges_dict = dict(zip(symbol_names, exchange_names))

                    for k, v in symbols_dict.items():
                        symbols_list.append(
                            {
                                "Title": k,
                                "Symbol": v,
                                "Exchange": exchanges_dict.get(k, "No Exchange"),
                            }
                        )

                df.columns = [d[1] if isinstance(d, tuple) else d for d in df.columns]
                df = df.iloc[:, :2].dropna(how="any")
                df.columns = ["key", "value"]
                output = df.set_index("key").to_dict()["value"]

                if not output.get("SIC") and self._sic:
                    output["SIC"] = self._sic
                    output["SIC Organization Name"] = self.sic_organization_name

                for k, v in output.copy().items():
                    if k in [
                        "Title of 12(b) Security",
                        "Trading Symbol",
                        "Security Exchange Name",
                        "No Trading Symbol Flag",
                    ]:
                        del output[k]

                if symbols_list:
                    output["12(b) Securities"] = symbols_list

                self._cover_page = output

        except IndexError:
            pass

        except Exception as e:
            raise RuntimeError(
                f"Failed to download and read the cover page table: {e}"
            ) from e

    def __repr__(self):
        """Return the string representation of the class."""
        repr_str = "SEC Filing(\n"

        for k, v in self.model_computed_fields.items():
            if not v:
                continue
            repr_str += f"  {k} : {v.return_type.__name__} - {v.description}\n"

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
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Extract the raw data from the SEC site."""
        try:
            data = SecBaseFiling(query.url, query.use_cache)
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

        return data.model_dump(exclude_none=True)

    @staticmethod
    def transform_data(
        query: SecFilingQueryParams, data: dict, **kwargs: Any
    ) -> SecFilingData:
        """Transform the raw data into a structured format."""
        return SecFilingData.model_validate(data)
