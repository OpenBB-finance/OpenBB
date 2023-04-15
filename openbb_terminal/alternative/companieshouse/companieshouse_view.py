""" UK Companies House View """
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.alternative.companieshouse import companieshouse_model
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

    print_rich_table(
        results,
        show_index=False,
        title=f"[bold]{search_str}[/bold]",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "results",
        results,
    )


@log_start_end(log=logger)
def display_company_info(company_number: str, export: str = "") -> None:
    """Display company search results.

    Parameters
    ----------
    company_number : str
        company_number to retrieve info for


    """
    results = companieshouse_model.get_company_info(company_number)

    if len(results) > 0:
        print_rich_table(
            results,
            show_index=False,
            show_header=False,
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
def display_officers(company_number: str, export: str = "") -> None:
    """Display company officers results.

    Parameters
    ----------
    company_number : str
        company_number to retrieve officers for


    """
    results = companieshouse_model.get_officers(company_number)

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
def display_filings(company_number: str, export: str = "") -> None:
    """Display company's filing history.

    Parameters
    ----------
    company_number : str
        company_number to retrieve filing history for


    """
    results = companieshouse_model.get_filings(company_number)

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


def download_filing_document(
    company_number: str, transactionID: str, export: str = ""
) -> None:
    """Display company's filing history.

    Parameters
    ----------
    company_number : str
        company_number to retrieve filing history for

    transactionID : str
        transaction id for filing

    """
    results = companieshouse_model.get_filing_document(company_number, transactionID)

    if len(results) > 0:
        with open(
            f"{get_current_user().preferences.USER_COMPANIES_HOUSE_DIRECTORY}/{transactionID}.pdf",
            "wb",
        ) as f:
            f.write(results)

        console.print(f"[green] File {transactionID}.pdf downloaded [/green]\n")
    else:
        console.print("[red]" + "Document not found" + "[/red]\n")
