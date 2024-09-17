"""SEC Company Filings Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_filings import (
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_sec.utils.definitions import FORM_TYPES, HEADERS
from pydantic import Field, field_validator


class SecCompanyFilingsQueryParams(CompanyFilingsQueryParams):
    """SEC Company Filings Query.

    Source: https://sec.gov/
    """

    symbol: Optional[str] = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
        default=None,
    )
    cik: Optional[Union[str, int]] = Field(
        description="Lookup filings by Central Index Key (CIK) instead of by symbol.",
        default=None,
    )
    form_type: Optional[FORM_TYPES] = Field(
        description="Type of the SEC filing form.",
        default=None,
    )
    use_cache: bool = Field(
        description="Whether or not to use cache.  If True, cache will store for one day.",
        default=True,
    )


class SecCompanyFilingsData(CompanyFilingsData):
    """SEC Company Filings Data."""

    __alias_dict__ = {
        "filing_date": "filingDate",
        "accepted_date": "acceptanceDateTime",
        "filing_url": "filingDetailUrl",
        "report_url": "primaryDocumentUrl",
        "report_type": "form",
        "report_date": "reportDate",
        "primary_doc_description": "primaryDocDescription",
        "primary_doc": "primaryDocument",
        "accession_number": "accessionNumber",
        "file_number": "fileNumber",
        "film_number": "filmNumber",
        "is_inline_xbrl": "isInlineXBRL",
        "is_xbrl": "isXBRL",
        "complete_submission_url": "completeSubmissionUrl",
        "filing_detail_url": "filingDetailUrl",
    }

    report_date: Optional[dateType] = Field(
        description="The date of the filing.",
        default=None,
    )
    act: Optional[Union[str, int]] = Field(
        description="The SEC Act number.", default=None
    )
    items: Optional[Union[str, float]] = Field(
        description="The SEC Item numbers.", default=None
    )
    primary_doc_description: Optional[str] = Field(
        description="The description of the primary document.",
        default=None,
    )
    primary_doc: Optional[str] = Field(
        description="The filename of the primary document.",
        default=None,
    )
    accession_number: Optional[Union[str, int]] = Field(
        description="The accession number.",
        default=None,
    )
    file_number: Optional[Union[str, int]] = Field(
        description="The file number.",
        default=None,
    )
    film_number: Optional[Union[str, int]] = Field(
        description="The film number.",
        default=None,
    )
    is_inline_xbrl: Optional[Union[str, int]] = Field(
        description="Whether the filing is an inline XBRL filing.",
        default=None,
    )
    is_xbrl: Optional[Union[str, int]] = Field(
        description="Whether the filing is an XBRL filing.",
        default=None,
    )
    size: Optional[Union[str, int]] = Field(
        description="The size of the filing.", default=None
    )
    complete_submission_url: Optional[str] = Field(
        description="The URL to the complete filing submission.",
        default=None,
    )
    filing_detail_url: Optional[str] = Field(
        description="The URL to the filing details.",
        default=None,
    )

    @field_validator("report_date", mode="before", check_fields=False)
    @classmethod
    def validate_report_date(cls, v: Optional[Union[str, dateType]]):
        """Validate report_date."""
        if isinstance(v, dateType):
            return v
        v = v if v != "" else None
        return (
            datetime.strptime(v, "%Y-%m-%d").date()
            if v and isinstance(v, str)
            else None
        )


class SecCompanyFilingsFetcher(
    Fetcher[SecCompanyFilingsQueryParams, List[SecCompanyFilingsData]]
):
    """SEC Company Filings Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecCompanyFilingsQueryParams:
        """Transform query params."""
        return SecCompanyFilingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecCompanyFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the SEC endpoint."""
        # pylint: disable=import-outside-toplevel
        from aiohttp_client_cache import SQLiteBackend
        from aiohttp_client_cache.session import CachedSession
        from openbb_core.app.utils import get_user_cache_directory
        from openbb_core.provider.utils.helpers import amake_request, amake_requests
        from openbb_sec.utils.helpers import symbol_map
        from pandas import DataFrame

        filings = DataFrame()

        if query.symbol and not query.cik:
            query.cik = await symbol_map(
                query.symbol.lower(), use_cache=query.use_cache
            )
            if not query.cik:
                raise OpenBBError(f"CIK not found for symbol {query.symbol}")
        if query.cik is None:
            raise OpenBBError("CIK or symbol must be provided.")

        # The leading 0s need to be inserted but are typically removed from the data to store as an integer.
        if len(query.cik) != 10:  # type: ignore
            cik_: str = ""
            temp = 10 - len(query.cik)  # type: ignore
            for i in range(temp):
                cik_ = cik_ + "0"
            query.cik = cik_ + str(query.cik)  # type: ignore

        url = f"https://data.sec.gov/submissions/CIK{query.cik}.json"
        data: Union[dict, List[dict]] = []
        if query.use_cache is True:
            cache_dir = f"{get_user_cache_directory()}/http/sec_company_filings"
            async with CachedSession(
                cache=SQLiteBackend(cache_dir, expire_after=3600 * 24)
            ) as session:
                try:
                    data = await amake_request(url, headers=HEADERS, session=session)  # type: ignore
                finally:
                    await session.close()
        else:
            data = await amake_request(url, headers=HEADERS)  # type: ignore

        # This seems to work for the data structure.
        filings = (
            DataFrame.from_records(data["filings"].get("recent"))  # type: ignore
            if "filings" in data
            else DataFrame()
        )
        results = filings.to_dict("records")

        # If there are lots of filings, there will be custom pagination.
        if (
            (query.limit and len(filings) >= 1000)
            or query.form_type is not None
            or query.limit == 0
        ):

            async def callback(response, session):
                """Response callback for excess company filings."""
                result = await response.json()
                if result:
                    new_data = DataFrame.from_records(result)
                    results.extend(new_data.to_dict("records"))

            urls: List = []
            new_urls = (
                DataFrame(data["filings"].get("files"))  # type: ignore
                if "filings" in data
                else DataFrame()
            )
            for i in new_urls.index:
                new_cik: str = data["filings"]["files"][i]["name"]  # type: ignore
                new_url: str = "https://data.sec.gov/submissions/" + new_cik
                urls.append(new_url)
            if query.use_cache is True:
                cache_dir = f"{get_user_cache_directory()}/http/sec_company_filings"
                async with CachedSession(
                    cache=SQLiteBackend(cache_dir, expire_after=3600 * 24)
                ) as session:
                    try:
                        await amake_requests(urls, headers=HEADERS, session=session, response_callback=callback)  # type: ignore
                    finally:
                        await session.close()
            else:
                await amake_requests(urls, headers=HEADERS, response_callback=callback)  # type: ignore

        return results

    @staticmethod
    def transform_data(
        query: SecCompanyFilingsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[SecCompanyFilingsData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        if not data:
            raise EmptyDataError(
                f"No filings found for CIK {query.cik}, or symbol {query.symbol}"
            )
        cols = [
            "reportDate",
            "filingDate",
            "acceptanceDateTime",
            "act",
            "form",
            "items",
            "primaryDocDescription",
            "primaryDocument",
            "accessionNumber",
            "fileNumber",
            "filmNumber",
            "isInlineXBRL",
            "isXBRL",
            "size",
        ]
        filings = (
            DataFrame(data, columns=cols)
            .fillna(value="N/A")
            .replace("N/A", None)
            .astype(str)
        )
        filings = filings.sort_values(by=["reportDate", "filingDate"], ascending=False)
        base_url = f"https://www.sec.gov/Archives/edgar/data/{query.cik}/"
        filings["primaryDocumentUrl"] = (
            base_url
            + filings["accessionNumber"].str.replace("-", "")
            + "/"
            + filings["primaryDocument"]
        )
        filings["completeSubmissionUrl"] = (
            base_url + filings["accessionNumber"] + ".txt"
        )
        filings["filingDetailUrl"] = (
            base_url + filings["accessionNumber"] + "-index.htm"
        )
        if query.form_type:
            filings = filings[filings["form"] == query.form_type.replace("_", " ")]

        if query.limit:
            filings = filings.head(query.limit) if query.limit != 0 else filings

        if len(filings) == 0:
            raise EmptyDataError("No filings were found using the filters provided.")

        return [
            SecCompanyFilingsData.model_validate(d) for d in filings.to_dict("records")
        ]
