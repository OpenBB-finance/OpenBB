"""Polygon Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import requests

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_financials(
    ticker: str, financial: str, quarterly: bool = False
) -> pd.DataFrame:
    """Get ticker financials from polygon

    Parameters
    ----------
    ticker: str
        Stock ticker
    quarterly:bool
        Flag to get quarterly reports

    Returns
    -------
    pd.DataFrame
        Balance Sheets or Income Statements
    """
    # Note the filing date is over 30 years so will always get as many as allowed
    json_request = requests.get(
        "https://api.polygon.io/vX/reference/financials?"
        f"ticker={ticker}"
        f"&timeframe={['annual','quarterly'][quarterly]}"
        "&limit=100"
        "&filing_date.gte=1980-01-01"
        f"&apiKey={cfg.API_POLYGON_KEY}"
    ).json()

    if financial == "cash" and quarterly:
        console.print(
            "[red]Quarterly information not available for statement of cash flows[/red]\n"
        )
    if financial not in ["balance", "income", "cash"]:
        console.print("financial must be 'balance' or 'income'.\n")
        return pd.DataFrame()

    if json_request["status"] == "ERROR":
        console.print(json_request["status"])
        return pd.DataFrame()

    all_results = json_request["results"]

    if len(all_results) == 0:
        console.print("No financials found from Polygon.\n")
        return pd.DataFrame()

    balance_sheets = pd.DataFrame()
    income_statements = pd.DataFrame()
    cash_flows = pd.DataFrame()
    first = True
    for single_thing in all_results:
        if first:
            balance_sheets = pd.concat(
                [
                    pd.DataFrame(),
                    pd.DataFrame.from_dict(
                        single_thing["financials"]["balance_sheet"], orient="index"
                    ),
                ],
                axis=1,
            )
            balance_sheets = balance_sheets[["value"]]
            balance_sheets.columns = [single_thing["filing_date"]]

            income_statements = pd.concat(
                [
                    pd.DataFrame(),
                    pd.DataFrame.from_dict(
                        single_thing["financials"]["income_statement"], orient="index"
                    ),
                ],
                axis=1,
            )
            income_statements = income_statements[["value"]]
            income_statements.columns = [single_thing["filing_date"]]

            if not quarterly:
                cash_flows = pd.concat(
                    [
                        pd.DataFrame(),
                        pd.DataFrame.from_dict(
                            single_thing["financials"]["cash_flow_statement"],
                            orient="index",
                        ),
                    ],
                    axis=1,
                )
                cash_flows = cash_flows[["value"]]
                cash_flows.columns = [single_thing["filing_date"]]

                first = False
        else:
            values = pd.DataFrame(
                pd.DataFrame.from_dict(
                    single_thing["financials"]["balance_sheet"], orient="index"
                ).value
            )
            values.columns = [single_thing["filing_date"]]
            balance_sheets = pd.concat([balance_sheets, values], axis=1)

            values = pd.DataFrame(
                pd.DataFrame.from_dict(
                    single_thing["financials"]["income_statement"], orient="index"
                ).value
            )
            income_statements = pd.concat([income_statements, values], axis=1)

            if not quarterly:
                values = pd.DataFrame(
                    pd.DataFrame.from_dict(
                        single_thing["financials"]["cash_flow_statement"],
                        orient="index",
                    ).value
                )
                cash_flows = pd.concat([cash_flows, values], axis=1)
    if financial == "balance":
        return balance_sheets
    if financial == "income":
        return income_statements
    if financial == "cash":
        return cash_flows
    return pd.DataFrame()
