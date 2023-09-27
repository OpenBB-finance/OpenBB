"""Polygon Model"""
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_POLYGON_KEY"])
def get_financials(
    symbol: str, statement: str, quarterly: bool = False, ratios: bool = False
) -> pd.DataFrame:
    """Get ticker financial statements from polygon

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    statement: str
        Financial statement data to retrieve, can be balance, income or cash
    quarterly:bool
        Flag to get quarterly reports, by default False
    ratios: bool
        Shows percentage change, by default False

    Returns
    -------
    pd.DataFrame
        Balance Sheets or Income Statements
    """
    # Note the filing date is over 30 years so will always get as many as allowed
    json_request = request(
        "https://api.polygon.io/vX/reference/financials?"
        f"ticker={symbol}"
        f"&timeframe={['annual','quarterly'][quarterly]}"
        "&limit=100"
        "&filing_date.gte=1980-01-01"
        f"&apiKey={get_current_user().credentials.API_POLYGON_KEY}"
    ).json()

    if statement not in ["balance", "income", "cash"]:
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
            values.columns = [single_thing["filing_date"]]
            income_statements = pd.concat([income_statements, values], axis=1)
            if "cash_flow_statement" in single_thing["financials"]:
                values = pd.DataFrame(
                    pd.DataFrame.from_dict(
                        single_thing["financials"]["cash_flow_statement"],
                        orient="index",
                    ).value
                )
                values.columns = [single_thing["filing_date"]]
                cash_flows = pd.concat([cash_flows, values], axis=1)
    if statement == "balance":
        df_fa = balance_sheets
    elif statement == "income":
        df_fa = income_statements
    elif statement == "cash":
        df_fa = cash_flows
    else:
        return pd.DataFrame()

    if ratios:
        types = df_fa.copy().applymap(lambda x: isinstance(x, (float, int)))
        types = types.all(axis=1)

        # For rows with complete data
        valid = []
        i = 0
        for row in types:
            if row:
                valid.append(i)
            i += 1
        df_fa_pc = df_fa.iloc[valid].pct_change(axis="columns", periods=-1).fillna(0)
        j = 0
        for i in valid:
            df_fa.iloc[i] = df_fa_pc.iloc[j]
            j += 1

    return df_fa
