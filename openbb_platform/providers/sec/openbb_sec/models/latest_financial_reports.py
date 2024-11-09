"""RSS Latest Financials Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.latest_financial_reports import (
    LatestFinancialReportsData,
    LatestFinancialReportsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

report_type_choices = [
    "1-K",
    "1-SA",
    "1-U",
    "10-D",
    "10-K",
    "10-KT",
    "10-Q",
    "10-QT",
    "20-F",
    "40-F",
    "6-K",
    "8-K",
]


class SecLatestFinancialReportsQueryParams(LatestFinancialReportsQueryParams):
    """SEC Latest Financial Reports Query.

    source: https://www.sec.gov/edgar/search/
    """

    __json_schema_extra__ = {
        "report_type": {"multiple_items_allowed": True, "choices": report_type_choices}
    }

    date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", "") + " Defaults to today.",
    )
    report_type: Optional[str] = Field(
        default=None,
        description="Return only a specific form type. Default is all quarterly, annual, and current reports."
        + f" Choices: {', '.join(report_type_choices)}.",
    )

    @field_validator("report_type", mode="before", check_fields=False)
    @classmethod
    def validate_report_type(cls, v):
        """Validate the report type."""
        if v is None:
            return v
        rpts = v.split(",")
        for rpt in rpts:
            if rpt not in report_type_choices:
                raise ValueError(
                    f"Invalid report type: {rpt}. Choices: {', '.join(report_type_choices)}"
                )
        return v


class SecLatestFinancialReportsData(LatestFinancialReportsData):
    """SEC Latest Financial Reports Data."""

    items: Optional[str] = Field(
        default=None, description="Item codes associated with the filing."
    )
    index_headers: str = Field(description="URL to the index headers file.")
    complete_submission: str = Field(
        description="URL to the complete submission text file."
    )
    metadata: Optional[str] = Field(
        default=None, description="URL to the MetaLinks.json file, if available."
    )
    financial_report: Optional[str] = Field(
        default=None, description="URL to the Financial_Report.xlsx file, if available."
    )


class SecLatestFinancialReportsFetcher(
    Fetcher[SecLatestFinancialReportsQueryParams, list[SecLatestFinancialReportsData]]
):
    """SEC Latest Financial Reports Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecLatestFinancialReportsQueryParams:
        """Transform the query params."""
        return SecLatestFinancialReportsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecLatestFinancialReportsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the raw data from the SEC."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta  # noqa
        from openbb_core.provider.utils.helpers import amake_request
        from warnings import warn

        today = dateType.today()
        query_date = query.date if query.date is not None else today

        if query_date.weekday() > 4:
            query_date -= timedelta(days=query_date.weekday() - 4)

        date = query_date.strftime("%Y-%m-%d")

        SEARCH_HEADERS = {
            "User-Agent": "my real company name definitelynot@fakecompany.com",
            "Accept-Encoding": "gzip, deflate",
        }

        forms = (
            query.report_type
            if query.report_type is not None
            else (
                "1-K%2C1-SA%2C1-U%2C1-Z%2C1-Z-W%2C10-D%2C10-K%2C10-KT%2C10-Q%2C10-QT%2C11-K%2C11-KT%2C15-12B%2C15-12G%2C"
                "15-15D%2C15F-12B%2C15F-12G%2C15F-15D%2C18-K%2C20-F%2C24F-2NT%2C25%2C25-NSE%2C40-17F2%2C40-17G%2C40-F%2C"
                "6-K%2C8-K%2C8-K12G3%2C8-K15D5%2CABS-15G%2CABS-EE%2CANNLRPT%2CDSTRBRPT%2CN-30B-2%2CN-30D%2CN-CEN%2CN-CSR%2C"
                "N-CSRS%2CN-MFP%2CN-MFP1%2CN-MFP2%2CN-PX%2CN-Q%2CNSAR-A%2CNSAR-B%2CNSAR-U%2CNT%2010-D%2CNT%2010-K%2C"
                "NT%2010-Q%2CNT%2011-K%2CNT%2020-F%2CQRTLYRPT%2CSD%2CSP%2015D2"
            )
        )

        def get_url(date, offset):
            return (
                "https://efts.sec.gov/LATEST/search-index?dateRange=custom"
                f"&category=form-cat1&startdt={date}&enddt={date}&forms={forms}&count=100&from={offset}"
            )

        n_hits = 0
        results: list = []
        url = get_url(date, n_hits)
        try:
            response = await amake_request(url, headers=SEARCH_HEADERS)
        except OpenBBError as e:
            raise OpenBBError(f"Failed to get SEC data: {e}") from e

        if not isinstance(response, dict):
            raise OpenBBError(
                f"Unexpected data response. Expected dictionary, got {response.__class__.__name__}"
            )

        hits = response.get("hits", {})
        total_hits = hits.get("total", {}).get("value")

        if hits.get("hits"):
            results.extend(hits["hits"])

        n_hits += len(results)

        while n_hits < total_hits:
            offset = n_hits
            url = get_url(date, offset)
            try:
                response = await amake_request(url, headers=SEARCH_HEADERS)
            except Exception as e:
                warn(f"Failed to get the next page of SEC data: {e}")
                break

            hits = response.get("hits", {})
            new_results = hits.get("hits", [])

            if not new_results:
                break

            results.extend(new_results)
            n_hits += len(new_results)

        if not results and query.report_type is None:
            raise OpenBBError("No data was returned.")

        if not results and query.report_type is not None:
            raise EmptyDataError(
                f"No data was returned for form type {query.report_type}."
            )

        return results

    @staticmethod
    def transform_data(
        query: SecLatestFinancialReportsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecLatestFinancialReportsData]:
        """Transform the raw data."""
        results: list[SecLatestFinancialReportsData] = []

        def parse_entry(entry):
            """Parse each entry in the response."""
            source = entry.get("_source", {})
            ciks = ",".join(source["ciks"]) if source.get("ciks") else None
            display_nammes = source.get("display_names", [])
            names: list = []
            tickers: list = []
            sics = ",".join(source.get("sics", []))
            for name in display_nammes:
                ticker = name.split("(")[1].split(")")[0].strip()
                tickers.append(ticker)
                _name = name.split("(")[0].strip()
                names.append(_name)

            output: dict = {}
            output["filing_date"] = source.get("file_date")
            output["period_ending"] = source.get("period_ending")
            output["symbol"] = ",".join(tickers).replace(" ", "")
            output["name"] = ",".join(names)
            output["cik"] = ciks
            output["sic"] = sics
            output["report_type"] = source.get("form")
            output["description"] = source.get("file_description")

            _id = entry.get("_id")
            root_url = (
                "https://www.sec.gov/Archives/edgar/data/"
                + source["ciks"][0]
                + "/"
                + source["adsh"].replace("-", "")
                + "/"
            )
            output["items"] = ",".join(source["items"]) if source.get("items") else None
            output["url"] = root_url + _id.split(":")[1]
            output["index_headers"] = (
                root_url + _id.split(":")[0] + "-index-headers.html"
            )
            output["complete_submission"] = root_url + _id.split(":")[0] + ".txt"
            output["metadata"] = (
                root_url + "MetaLinks.json"
                if output["report_type"].startswith("10-")
                or output["report_type"].startswith("8-")
                else None
            )
            output["financial_report"] = (
                root_url + "Financial_Report.xlsx"
                if output["report_type"].startswith("10-")
                or output["report_type"].startswith("8-")
                or output["report_type"] in ["N-CSR", "QRTLYRPT", "ANNLRPT"]
                else None
            )
            return output

        # Some duplicates may exist in the data.
        seen = set()
        for entry in data:
            parsed_entry = parse_entry(entry)
            if parsed_entry["url"] not in seen:
                seen.add(parsed_entry["url"])
                results.append(
                    SecLatestFinancialReportsData.model_validate(parsed_entry)
                )

        return results
