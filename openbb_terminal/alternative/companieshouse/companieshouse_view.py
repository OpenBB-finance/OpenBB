""" UK Companies House View """
__docformat__ = "numpy"

import logging
import os

import pandas as pd

from openbb_terminal.alternative.companieshouse import companieshouse_model
from openbb_terminal.alternative.companieshouse.company import Company
from openbb_terminal.alternative.companieshouse.filing_data import Filing_data
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_search(search_str: str, limit: int, export: str = "") -> None:
    """Display company search results.

    Parameters
    ----------
    search_str : str
        Company name to search for

    limit : int
        number of rows to return

    """
    results = companieshouse_model.get_search_results(search_str, limit)

    if results.empty or len(results) == 0:
        console.print(
            "[red]" + "No data loaded.\n" + "Try different search string." + "[/red]\n"
        )
        return

    console.print(f"Retrieved {len(results)} records")
    print_rich_table(
        results,
        show_index=False,
        title=f"[bold]{search_str}[/bold]",
        export=bool(export),
        columns_keep_types=["Company Number"],
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "results",
        results,
    )


@log_start_end(log=logger)
def display_company_info(company_number: str, export: str = "") -> Company:
    """Display company search results.

    Parameters
    ----------
    company_number : str
        company_number to retrieve info for


    """
    return companieshouse_model.get_company_info(company_number)


@log_start_end(log=logger)
def display_officers(company_number: str, export: str = "") -> None:
    """Display company officers results.

    Parameters
    ----------
    company_number : str
        company_number to retrieve officers for


    """
    results = companieshouse_model.get_officers(company_number)

    if len(results) > 0:
        console.print(f"Retrieved {len(results)} records")
        print_rich_table(
            results,
            show_index=False,
            title=f"[bold]{company_number}[/bold]",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "results",
            results,
        )
    else:
        console.print("[red]No Data Found[/red]")


@log_start_end(log=logger)
def display_persons_with_significant_control(
    company_number: str, export: str = ""
) -> None:
    """Display company officers results.

    Parameters
    ----------
    company_number : str
        company_number to retrieve officers for


    """
    results = companieshouse_model.get_persons_with_significant_control(company_number)

    if len(results) > 0:
        console.print(f"Retrieved {len(results)} records")
        print_rich_table(
            results,
            show_index=False,
            title=f"[bold]{company_number}[/bold]",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "results",
            results,
        )
    else:
        console.print("[red]No Data Found[/red]")


@log_start_end(log=logger)
def display_filings(
    company_number: str,
    category: str = "",
    limit: int = 100,
    export: str = "",
) -> Filing_data:
    """Display company's filing history.

    Parameters
    ----------
    company_number : str
        company_number to retrieve filing history for

    """
    start_index = 0
    results = companieshouse_model.get_filings(company_number, category, start_index)

    start = int(results.start_index)

    data = results
    total = int(results.total_count) if int(results.total_count) < limit else limit

    while start < total - 100:
        results = companieshouse_model.get_filings(
            company_number, start_index=start + 100
        )
        data.filings = pd.concat([data.filings, results.filings], ignore_index=True)
        start = start + 100

    data.filings = data.filings.head(limit)
    console.print(f"Retrieved {len(data.filings)} filings")

    print_rich_table(
        data.filings,
        show_index=False,
        title=f"[bold]{company_number}[/bold]",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "results",
        data.filings,
    )

    return results


def download_filing_document(
    company_number: str, company_name: str, transactionID: str, export: str = ""
) -> None:
    """Download company's filing document.

    Parameters
    ----------
    company_number : str
        company_number to retrieve filing history for

    company_name : str
        company_name to retrieve filing document for, this is used to name the downloaded file for easy access

    transactionID : str
        transaction id for filing

    >>> companies = openbb.alt.companieshouse.get_search_results("AstraZeneca")
    >>> openbb.alt.companieshouse.get_filing_document("02723534","AstraZeneca","MzM1NzQ0NzI5NWFkaXF6a2N4")
    """

    results = companieshouse_model.get_filing_document(company_number, transactionID)

    if results.dataAvailable():
        filename = (
            company_name.replace(" ", "_")
            + "_"
            + results.category
            + "_"
            + transactionID
            + ".pdf"
        )
        with open(
            f"{get_current_user().preferences.USER_COMPANIES_HOUSE_DIRECTORY}/{filename}",
            "wb",
        ) as f:
            f.write(results.content)
            console.print(
                f"File [green] {filename}[/green] downloaded to \
                  {get_current_user().preferences.USER_COMPANIES_HOUSE_DIRECTORY}"
            )
    else:
        console.print("[red]" + "Document not found" + "[/red]\n")


@log_start_end(log=logger)
def display_charges(company_number: str, export: str = "") -> None:
    results = companieshouse_model.get_charges(company_number)

    if len(results) > 0:
        print_rich_table(
            results,
            show_index=False,
            title=f"[bold]{company_number}[/bold]",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "results",
            results,
        )
    else:
        console.print("[red]" + "No Charges found" + "[/red]\n")

    return results
