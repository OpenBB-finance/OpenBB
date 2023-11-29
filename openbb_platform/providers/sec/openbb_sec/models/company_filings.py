"""SEC Company Filings Model."""

from datetime import (
    date as dateType,
    timedelta,
)
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests
import requests_cache
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_filings import (
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_sec.utils.definitions import FORM_TYPES, HEADERS
from openbb_sec.utils.helpers import symbol_map
from pydantic import Field

sec_session_company_filings = requests_cache.CachedSession(
    "OpenBB_SEC_COMPANY_FILINGS", expire_after=timedelta(days=1), use_cache_dir=True
)


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
    type: Optional[FORM_TYPES] = Field(
        description="Type of the SEC filing form.",
        default=None,
        alias="form_type",
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
    }

    report_date: Optional[dateType] = Field(
        description="The date of the filing.",
        default=None,
        alias="reportDate",
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
        alias="primaryDocDescription",
    )
    primary_doc: Optional[str] = Field(
        description="The filename of the primary document.",
        default=None,
        alias="primaryDocument",
    )
    accession_number: Optional[Union[str, int]] = Field(
        description="The accession number.",
        default=None,
        alias="accessionNumber",
    )
    file_number: Optional[Union[str, int]] = Field(
        description="The file number.",
        default=None,
        alias="fileNumber",
    )
    film_number: Optional[Union[str, int]] = Field(
        description="The film number.",
        default=None,
        alias="filmNumber",
    )
    is_inline_xbrl: Optional[Union[str, int]] = Field(
        description="Whether the filing is an inline XBRL filing.",
        default=None,
        alias="isInlineXBRL",
    )
    is_xbrl: Optional[Union[str, int]] = Field(
        description="Whether the filing is an XBRL filing.",
        default=None,
        alias="isXBRL",
    )
    size: Optional[Union[str, int]] = Field(
        description="The size of the filing.", default=None
    )
    complete_submission_url: Optional[str] = Field(
        description="The URL to the complete filing submission.",
        default=None,
        alias="completeSubmissionUrl",
    )
    xml: Optional[str] = Field(
        description="The URL to the primary XML document.", default=None
    )


class SecCompanyFilingsFetcher(
    Fetcher[SecCompanyFilingsQueryParams, List[SecCompanyFilingsData]]
):
    """Transform the query, extract and transform the data from the SEC endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecCompanyFilingsQueryParams:
        """Transform query params."""
        return SecCompanyFilingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecCompanyFilingsQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extracts the data from the SEC endpoint."""
        filings = pd.DataFrame()

        if query.symbol and not query.cik:
            query.cik = symbol_map(query.symbol.lower(), use_cache=query.use_cache)
            if not query.cik:
                return []
        if query.cik is None:
            return []

        # The leading 0s need to be inserted but are typically removed from the data to store as an integer.
        if len(query.cik) != 10:
            cik_: str = ""
            temp = 10 - len(query.cik)
            for i in range(temp):
                cik_ = cik_ + "0"
            query.cik = cik_ + query.cik

        url = f"https://data.sec.gov/submissions/CIK{query.cik}.json"
        r = (
            requests.get(url, headers=HEADERS, timeout=5)
            if query.use_cache is False
            else sec_session_company_filings.get(url, headers=HEADERS, timeout=5)
        )
        if r.status_code == 200:
            data = r.json()
            filings = pd.DataFrame.from_records(data["filings"]["recent"])
            if len(filings) >= 1000:
                new_urls = pd.DataFrame(data["filings"]["files"])
                for i in new_urls.index:
                    new_cik: str = data["filings"]["files"][i]["name"]
                    new_url: str = "https://data.sec.gov/submissions/" + new_cik
                    r_ = (
                        requests.get(new_url, headers=HEADERS, timeout=5)
                        if query.use_cache is False
                        else sec_session_company_filings.get(
                            new_url, headers=HEADERS, timeout=5
                        )
                    )
                    if r_.status_code == 200:
                        data_ = r_.json()
                        additional_data = pd.DataFrame.from_records(data_)
                        filings = pd.concat([filings, additional_data], axis=0)
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
            pd.DataFrame(filings, columns=cols)
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
        if "type" in query.model_dump() and query.type is not None:
            filings = filings[filings["form"] == query.type]

        if "limit" in query.model_dump():
            filings = filings.head(query.limit) if query.limit != 0 else filings

        return filings.to_dict("records")

    @staticmethod
    def transform_data(
        query: SecCompanyFilingsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[SecCompanyFilingsData]:
        """Transforms the data."""
        return [SecCompanyFilingsData.model_validate(d) for d in data]
