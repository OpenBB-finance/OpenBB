"""  UK Companies House Model """
__docformat__ = "numpy"

import io
import logging
import pandas as pd
import requests

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.core.session.current_user import get_current_user

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_search_results(searchStr: str, limit: int = 20) -> pd.DataFrame:
    """All scompanies with searchStr in their name.

    Parameters
    ----------
    searchStr : str
        Postcode

    limit : int
        number of rows to return


    Returns
    -------
    pd.DataFrame
        All sales with that postcode
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

    # r = requests.get('https://api.company-information.service.gov.uk/company/'+'13952122', auth=(API_KEY, ''))


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_company_info(company_number: str) -> pd.DataFrame:
    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}",
        auth=auth,
    )

    returned_data = r.json()
    company = returned_data["company_name"]
    last_accounts = returned_data["accounts"]["last_accounts"]
    address = returned_data["registered_office_address"]
    pretty_address = (
        (address.get("address_line_1") or "")
        + " ,"
        + (address.get("address_line_2") or "")
        + " ,"
        + (address.get("locality") or "")
        + " ,"
        + (address.get("region") or "")
        + " ,"
        + (address.get("postal_code") or "")
    )

    pretty_accounts = "Period Start On : " + (
        last_accounts.get("period_start_on") or ""
    ) + "\n" + "Type : " + (
        last_accounts.get("type") or ""
    ) + "\n" + "Made Up To : " + (
        last_accounts.get("made_up_to") or ""
    ) + "\n" "Period End On : " + (
        last_accounts.get("period_end_on") or ""
    )

    data = pd.DataFrame(
        [
            ["Company", company],
            ["Address", pretty_address],
            ["Last Account", pretty_accounts],
        ]
    )
    data.columns = ["Title", "Data"]
    return data


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_officers(company_number: str) -> pd.DataFrame:
    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/officers",
        auth=auth,
    )
    returned_data = r.json()

    officers = []
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
    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/persons-with-significant-control",
        auth=auth,
    )
    returned_data = r.json()

    controllers = []
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
def get_filings(company_number: str) -> pd.DataFrame:
    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/filing-history",
        auth=auth,
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
                "Pages": (int(item.get("pages")) or " - "),
                "Transaction ID": (item.get("transaction_id") or " - "),
            }
        )

    df = pd.DataFrame(filings)

    return df


@log_start_end(log=logger)
@check_api_key(["API_COMPANIESHOUSE_KEY"])
def get_filing_document(company_number: str, transactionID: str) -> str:
    auth = requests.auth.HTTPBasicAuth(
        get_current_user().credentials.API_COMPANIESHOUSE_KEY, ""
    )
    r = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}/filing-history/{transactionID}",
        auth=auth,
    )
    returned_data = r.json()

    if returned_data.get("links") and returned_data.get("links").get(
        "document_metadata"
    ):
        url = returned_data.get("links").get("document_metadata") + "/content"
        response = requests.get(url, auth=auth, headers={"Accept": "application/pdf"})
        with open(
            f"{get_current_user().preferences.USER_COMPANIES_HOUSE_DIRECTORY}/{transactionID}.pdf",
            "wb",
        ) as f:
            f.write(response.content)

        return f"File {transactionID}.pdf downloaded"
    else:
        return "File not available for download"
