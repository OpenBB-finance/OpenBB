"""  UK Companies House Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import requests

from openbb_terminal.alternative.companieshouse.company import Company
from openbb_terminal.alternative.companieshouse.company_doc import CompanyDocument
from openbb_terminal.alternative.companieshouse.filing_data import Filing_data
from openbb_terminal.core.session.constants import (
    TIMEOUT,
)
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_search_results(searchStr: str, limit: int = 20) -> pd.DataFrame:
    """All companies with searchStr in their name.

    Parameters
    ----------
    searchStr : str
        The search string
    limit : int
        number of rows to return

    Returns
    -------
    pd.DataFrame
        All comapanies with the search string in their name.

    Example
    -------
    >>> from openbb_terminal.sdk import openbb
    >>> companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
    """

    df = pd.DataFrame()

    if not searchStr:
        return df

    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        "https://api.company-information.service.gov.uk/search/companies?q="
        + searchStr
        + f"&items_per_page={limit}",
        auth=auth,
        timeout=TIMEOUT,
    )
    returned_data = r.json()
    company_data = []
    for index, item in enumerate(returned_data["items"]):
        company_data.append(
            {
                "Name": item["title"],
                "Company Number": item["company_number"],
                "Status": item["company_status"],
            }
        )

    df = pd.DataFrame(company_data)
    return df


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_company_info(company_number: str) -> Company:
    """Gets company info by company number

    Parameters
    ----------
    company_number : str
        The company number.  Use get_search_results() to lookup company numbers.

    Returns
    -------
    self.address: str
        Company address.
    self.name: str
        Company name.
    self.dataAvailable(): bool
        True if data is available.
    self.lastAccounts: str
        Period start and end.

    Example
    -------
    >>> companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
    >>> company_info = openbb.alt.companieshouse.get_company_info("02723534")
    >>> name = company_info.name
    """

    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}",
        auth=auth,
        timeout=TIMEOUT,
    )

    last_accounts = {}
    returned_data = r.json()
    if returned_data.get("company_name"):
        company_name = returned_data["company_name"]
        if returned_data.get("accounts"):
            last_accounts = returned_data["accounts"]["last_accounts"]
        address = returned_data["registered_office_address"]
        address_lines = []
        if address.get("address_line_1"):
            address_lines.append(address.get("address_line_1"))
        if address.get("address_line_2"):
            address_lines.append(address.get("address_line_2"))
        if address.get("locality"):
            address_lines.append(address.get("locality"))
        if address.get("region"):
            address_lines.append(address.get("region"))
        if address.get("postal_code"):
            address_lines.append(address.get("postal_code"))
        pretty_address = (
            ",".join(address_lines)
            if len(address_lines) > 0
            else "No address data found"
        )

        if last_accounts:
            pretty_accounts = "Period Start On : " + (
                last_accounts.get("period_start_on") or ""
            ) + " - " + "Type : " + (
                last_accounts.get("type") or ""
            ) + " - " + "Made Up To : " + (
                last_accounts.get("made_up_to") or ""
            ) + " - " "Period End On : " + (
                last_accounts.get("period_end_on") or ""
            )
        else:
            pretty_accounts = "No accounting period data found"

        data = Company(company_name, pretty_address, pretty_accounts)
        return data
    else:
        return Company()


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_officers(company_number: str) -> pd.DataFrame:
    """Gets information on company officers

    Parameters
    ----------
    company_number : str
        The company number.  Use get_search_results() to lookup company numbers.

    Returns
    -------
    pd.Dataframe
        All officers for given company number

    Example
    -------
    >>> companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
    >>> officer_info = openbb.alt.companieshouse.get_officers("02723534")
    """

    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/officers?items_per_page=100",
        auth=auth,
        timeout=TIMEOUT,
    )
    returned_data = r.json()

    officers = []
    if returned_data.get("items"):
        for index, item in enumerate(returned_data["items"]):
            officers.append(
                {
                    "Officer Role": (item.get("officer_role") or " - "),
                    "Appointed On": (item.get("appointed_on") or " - "),
                    "Resigned On": (item.get("resigned_on") or " - "),
                    "Name": (item.get("name") or " - "),
                }
            )

    df = pd.DataFrame(officers)

    return df


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_persons_with_significant_control(company_number: str) -> pd.DataFrame:
    """Gets information on persons with significant control over the company

    Parameters
    ----------
    company_number : str
        The company number.  Use get_search_results() to lookup company numbers.

    Returns
    -------
    pd.Dataframe
        All persons with significant control over given company number

    Example
    -------
    >>> companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
    >>> signif_control_info = openbb.alt.companieshouse.get_persons_with_significant_control("02723534")
    """

    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/persons-with-significant-control?items_per_page=100",
        auth=auth,
        timeout=TIMEOUT,
    )
    returned_data = r.json()

    controllers = []
    if returned_data.get("items"):
        for index, item in enumerate(returned_data["items"]):
            controllers.append(
                {
                    "Kind": (item.get("kind") or " - "),
                    "Name": (item.get("name") or " - "),
                    "Natures of Control": (item.get("natures_of_control") or " - "),
                    "Notified On": (item.get("notified_on") or " - "),
                }
            )

    df = pd.DataFrame(controllers)

    return pd.DataFrame(df)


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_filings(company_number: str, category: str = "", start_index=0) -> Filing_data:
    """Gets information on filings for given company, e.g. accounts, etc

    Parameters
    ----------
    company_number : str
        The company number.  Use get_search_results() to lookup company numbers.

    Returns
    -------
    pd.Dataframe
        All information on all filings for company

    Example
    -------
    >>> companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
    >>> signif_control_info = openbb.alt.companieshouse.get_filings("02723534")
    """

    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    url = (
        f"https://api.company-information.service.gov.uk/company/{company_number}/filing-history"
        + f"?start_index={start_index}&items_per_page=100"
    )
    if category:
        url = (
            f"https://api.company-information.service.gov.uk/company/{company_number}/filing-history"
            + f"?category={category}&start_index={start_index}&items_per_page=100"
        )

    r = requests.get(
        url,
        auth=auth,
        timeout=TIMEOUT,
    )
    returned_data = r.json()

    filings = []
    for index, item in enumerate(returned_data["items"]):
        filings.append(
            {
                "Category": (item.get("category") or " - "),
                "Date": (item.get("date") or " - "),
                "Description": (item.get("description") or " - "),
                "Type": (item.get("type") or " - "),
                "Pages": (item.get("pages") or " - "),
                "Transaction ID": (item.get("transaction_id") or " - "),
                "Download": "https://find-and-update.company-information.service.gov.uk/company/"
                f"{company_number}"
                "/filing-history/"
                f"{item.get('transaction_id')}"
                "/document?format=pdf&download=0",
            }
        )
    start_index = int(returned_data.get("start_index"))
    total_count = int(returned_data.get("total_count"))
    end_index = start_index + 100
    if end_index > total_count:
        end_index = total_count
    data = Filing_data(pd.DataFrame(filings), start_index, end_index, total_count)

    return data


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_filing_document(company_number: str, transactionID: str) -> CompanyDocument:
    """Download given filing document pdf

    Parameters
    ----------
    company_number : str
        The company number.  Use get_search_results() to lookup company numbers.
    transactionID : str
        The filing transaction id. Use get_filings() to get id for each document

    Returns
    -------
    self.category: str
        document category, e.g.confirmation-statement-with-updates, accounts-with-accounts-type-dormant, etc.
    self.date: str
        date document filed.
    self.description: str
        description of document files.
    self.paper_filed: str
        True if documents filed in paper format.
    self.pages: str
        Number of pages in document.
    self.transaction_id: str
        Document transaction id.
    self.content: bytes
        contents of the document.

    Example
    -------
    >>> companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
    >>> company_doc_info = openbb.alt.companieshouse.get_filing_document("02723534","MzM1NzQ0NzI5NWFkaXF6a2N4")
    """

    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/filing-history/{transactionID}",
        auth=auth,
        timeout=TIMEOUT,
    )

    returned_data = r.json()

    category = date = description = paper_filed = pages = transaction_id = ""
    content = b""
    if returned_data.get("links") and returned_data.get("links").get(
        "document_metadata"
    ):
        url = returned_data.get("links").get("document_metadata") + "/content"
        response = requests.get(
            url, auth=auth, headers={"Accept": "application/pdf"}, timeout=TIMEOUT
        )

        if returned_data.get("category"):
            category = returned_data["category"]
        if returned_data.get("date"):
            date = returned_data["date"]
        if returned_data.get("description"):
            description = returned_data["description"]
        if returned_data.get("paper_filed"):
            paper_filed = returned_data["paper_filed"]
        if returned_data.get("pages"):
            pages = returned_data["pages"]
        if returned_data.get("transaction_id"):
            transaction_id = returned_data["transaction_id"]

        content = bytes(response.content)

        return CompanyDocument(
            category, date, description, paper_filed, pages, transaction_id, content
        )
    else:
        return CompanyDocument(
            category, date, description, paper_filed, pages, transaction_id, content
        )


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_charges(company_number: str) -> pd.DataFrame:
    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/charges",
        auth=auth,
        timeout=TIMEOUT,
    )

    returned_data = r.json()

    charges = pd.DataFrame()
    for index, item in enumerate(returned_data["items"]):
        url = item.get("links").get("self")
        id = url[url.rfind("/") + 1 :]
        charges = pd.concat(
            [charges, get_charge(company_number, id)], ignore_index=True
        )

    return charges


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_charge(company_number: str, charge_id: str) -> pd.DataFrame:
    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/charges/{charge_id}",
        auth=auth,
        timeout=TIMEOUT,
    )

    returned_data = r.json()

    charge = {}
    if returned_data.get("acquired_on"):
        charge.update({"acquired_on": returned_data.get("acquired_on")})
    if returned_data.get("assests_ceased_released"):
        charge.update(
            {"assests_ceased_released": returned_data.get("assests_ceased_released")}
        )

    if returned_data.get("charge_number"):
        charge.update({"charge_number": returned_data.get("charge_number")})

    if returned_data.get("covering_instrument_date"):
        charge.update(
            {"covering_instrument_date": returned_data.get("covering_instrument_date")}
        )

    if returned_data.get("created_on"):
        charge.update({"created_on": returned_data.get("created_on")})

    if returned_data.get("delivered_on"):
        charge.update({"delivered_on": returned_data.get("delivered_on")})

    if returned_data.get("id"):
        charge.update({"id": returned_data.get("id")})

    if returned_data.get("status"):
        charge.update({"status": returned_data.get("status")})

    if returned_data.get("particulars"):
        part = returned_data.get("particulars")

        if part.get("description"):
            charge.update({"description": part.get("description")})
        if part.get("floating_charge_covers_all"):
            charge.update(
                {"floating_charge_covers_all": part.get("floating_charge_covers_all")}
            )
        if part.get("type"):
            charge.update({"type": part.get("type")})

    if returned_data.get("persons_entitled"):
        for entitled in returned_data.get("persons_entitled"):
            charge.update({"persons_entitled_name": entitled.get("name")})

    return pd.DataFrame([charge])
