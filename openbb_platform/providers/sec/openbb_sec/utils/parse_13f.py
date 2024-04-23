"""Utility functions for parsing SEC Form 13F-HR."""

from typing import Any, Dict, Optional

import xmltodict
from bs4 import BeautifulSoup
from openbb_core.provider.utils.helpers import amake_request
from openbb_sec.models.company_filings import SecCompanyFilingsFetcher
from openbb_sec.utils.definitions import HEADERS
from pandas import DataFrame, offsets, to_datetime


def date_to_quarter_end(date: str) -> str:
    """Convert a date to the end of the calendar quarter."""
    return (
        (to_datetime(date).to_period("Q").to_timestamp("D") + offsets.QuarterEnd())
        .date()
        .strftime("%Y-%m-%d")
    )


async def get_13f_candidates(symbol: Optional[str] = None, cik: Optional[str] = None):
    """Get the 13F-HR filings for a given symbol or CIK."""
    fetcher = SecCompanyFilingsFetcher()
    params: Dict[str, Any] = {}
    if cik is not None:
        params["cik"] = str(cik)
    if symbol is not None:
        params["symbol"] = symbol
    if cik is None and symbol is None:
        raise ValueError("Either symbol or cik must be provided.")

    params["use_cache"] = False
    params["form_type"] = "13F-HR"
    filings = await fetcher.fetch_data(params, {})
    filings = [d.model_dump() for d in filings]
    if len(filings) == 0:
        raise ValueError(f"No 13F-HR filings found for {symbol if symbol else cik}.")

    # Filings before June 30, 2013 are non-structured and are not supported by downstream parsers.
    up_to = to_datetime("2013-06-30").date()  # pylint: disable=unused-variable # noqa
    return (
        DataFrame(data=filings)
        .query("`report_date` >= @up_to")
        .set_index("report_date")["complete_submission_url"]
        .fillna("N/A")
        .replace("N/A", None)
    )


async def complete_submission_callback(response, _):
    """Use callback function for processing the response object."""
    if response.status == 200:
        return await response.text()
    raise RuntimeError(f"Request failed with status code {response.status}")


async def get_complete_submission(url: str):
    """Get the Complete Submission TXT file string from the SEC API."""
    return await amake_request(
        url, headers=HEADERS, response_callback=complete_submission_callback
    )


def parse_header(filing_str: str) -> Dict:
    """Parse the header of a Complete Submission TXT file string."""
    header_dict = {}
    try:
        soup = BeautifulSoup(filing_str, "lxml-xml")
        header_xml = soup.find("headerData")
        header_dict = xmltodict.parse(str(header_xml))["headerData"]
    except KeyError:
        soup = BeautifulSoup(filing_str, features="lxml")
        header_xml = soup.find("type")
        header_dict = xmltodict.parse(str(header_xml)).get("type")
    if header_dict:
        return header_dict  # type: ignore
    raise ValueError(
        "Failed to parse the form header."
        + " Check the `filing_str` to for the tag, 'headerData'."
    )


def get_submission_type(filing_str: str):
    """Get the submission type of a Complete Submission TXT file string."""
    header = parse_header(filing_str)
    if header:
        try:
            form_type = header["submissionType"]
            return form_type
        except KeyError:
            form_type = header["#text"]
            return form_type
    raise ValueError(
        "Failed to get the submission type from the form header."
        + " Check the response from `parse_header`."
    )


def get_period_ending(filing_str: str):
    """Get the report date from a Complete Submission TXT file string."""
    header = parse_header(filing_str)
    if header.get("filerInfo"):
        return header["filerInfo"].get("periodOfReport")
    raise ValueError(
        "Failed to get the period of report from the form header."
        + " Check the response from `parse_header`."
    )


async def parse_13f_hr(filing: str):
    """Parse a 13F-HR filing from the Complete Submission TXT file string."""
    data = DataFrame()

    # Check if the input string is a URL
    if filing.startswith("https://"):
        filing = await get_complete_submission(filing)  # type: ignore

    # Validate the submission so we know that we can parse it.
    if get_submission_type(filing) not in ("13F-HR", "13F-HR/A"):
        raise ValueError("Submission type is not 13F-HR.")

    soup = BeautifulSoup(filing, "lxml-xml")

    info_table = soup.find_all("informationTable")
    if info_table == []:
        info_table = soup.find_all("table")[-1]

    parsed_xml = xmltodict.parse(
        str(info_table[0]).replace("ns1:", "").replace("n1:", "")
    )["informationTable"]["infoTable"]

    if parsed_xml is None:
        raise ValueError(
            "Failed to parse the 13F-HR information table."
            + " Check the `filing_str` to make sure it is valid and contains the tag 'informationTable'."
            + " Documents filed before Q2 2013 are not supported."
        )

    period_ending = get_period_ending(filing)
    data = (
        DataFrame(parsed_xml)
        if isinstance(parsed_xml, list)
        else DataFrame([parsed_xml])
    )
    data.columns = data.columns.str.replace("ns1:", "")
    data["value"] = data["value"].astype(int)
    security_type = []
    principal_amount = []

    # Unpack the nested objects
    try:
        security_type = [d.get("sshPrnamtType") for d in data["shrsOrPrnAmt"]]
        data["security_type"] = security_type
        principal_amount = [d.get("sshPrnamt") for d in data["shrsOrPrnAmt"]]
        data["principal_amount"] = principal_amount
        data.pop("shrsOrPrnAmt")
    except ValueError:
        pass
    try:
        sole = [d.get("Sole") for d in data["votingAuthority"]]
        shared = [d.get("Shared") for d in data["votingAuthority"]]
        none = [d.get("None") for d in data["votingAuthority"]]
        data["voting_authority_sole"] = [int(s) for s in sole]
        data["voting_authority_shared"] = [int(s) for s in shared]
        data["voting_authority_none"] = [int(s) for s in none]
        data.pop("votingAuthority")
    except ValueError:
        pass

    # Add the period ending so that the filing is identified when multiple are requested.
    data["period_ending"] = to_datetime(period_ending, yearfirst=False).date()

    df = DataFrame(data)
    df["principal_amount"] = df["principal_amount"].astype(int)

    # Aggregate the data because there are multiple entries for each security and we need the totals.
    # We break it down by CUSIP, security type, and option type.
    agg_index = ["cusip", "security_type", "putCall"]
    agg_columns = {
        "period_ending": "first",
        "nameOfIssuer": "first",
        "titleOfClass": "first",
        "value": "sum",
        "principal_amount": "sum",
        "voting_authority_sole": "sum",
        "voting_authority_shared": "sum",
        "voting_authority_none": "sum",
    }

    # Only aggregate columns that exist in the DataFrame
    agg_columns = {k: v for k, v in agg_columns.items() if k in df.columns}
    agg_index = [k for k in agg_index if k in df.columns]
    df = df.groupby([*agg_index]).agg(agg_columns)

    for col in [
        "voting_authority_sole",
        "voting_authority_shared",
        "voting_authority_none",
    ]:
        if col in df.columns and all(df[col] == 0):
            df.drop(columns=col, inplace=True)

    total_value = df["value"].sum()
    df["weight"] = round(df["value"] / total_value, 6)

    return (
        df.reset_index()
        .fillna("N/A")
        .sort_values(by="weight", ascending=False)
        .replace("N/A", None)
    )
