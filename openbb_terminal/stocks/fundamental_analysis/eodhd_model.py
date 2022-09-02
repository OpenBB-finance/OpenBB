"""eodhd Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import numpy as np
import requests

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_financials(
    symbol: str, statement: str, quarterly: bool = False, ratios: bool = False
) -> pd.DataFrame:
    """Get ticker financial statements from eodhd

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
        Balance Sheets or Income Statements or cashflow
    """
    # Note the filing date is over 30 years so will always get as many as allowed
    request_url = (
        "https://eodhistoricaldata.com/api/fundamentals/"
        f"{symbol}?"
        f"api_token={cfg.API_EODHD_TOKEN}"
        f"&filter=Financials::{statement}"
        f"::{['yearly','quarterly'][quarterly]}"
    )
    console.print(request_url)

    r = requests.get(request_url)
    if r.status_code != 200:
        console.print("[red]Invalid API Key for eodhistoricaldata [/red]")
        console.print(
            "Get your Key here: https://eodhistoricaldata.com/r/?ref=869U7F4J\n"
        )
        return pd.DataFrame()

    r_json = r.json()

    df_financials = pd.DataFrame(r_json)  # .dropna(axis=0)
    df_financials.drop("date", inplace=True)
    df_financials.drop("filing_date", inplace=True)
    df_financials.drop("currency_symbol", inplace=True)

    df_financials = df_financials.fillna(value=np.nan)
    console.print(df_financials)
    console.print(df_financials.index)

    if statement == "cash" and quarterly:
        console.print(
            "[red]Quarterly information not available for statement of cash flows[/red]\n"
        )
    if statement not in ["Balance_Sheet", "income", "cash"]:
        console.print("financial must be 'Balance_Sheet' or 'income or cash.\n")
        return pd.DataFrame()

    if r.status_code != 200:
        console.print("[red]Invalid API Key for eodhistoricaldata [/red]")
        console.print(
            "Get your Key here: https://eodhistoricaldata.com/r/?ref=869U7F4J\n"
        )

    if len(r_json) == 0:
        console.print("No financials found from eodhd.\n")
        return pd.DataFrame()

    balance_sheets = pd.DataFrame()
    income_statements = pd.DataFrame()
    cash_flows = pd.DataFrame()
    first = True
    for single_thing in r_json:
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
            values.columns = [single_thing["filing_date"]]
            income_statements = pd.concat([income_statements, values], axis=1)
            if not quarterly:
                values = pd.DataFrame(
                    pd.DataFrame.from_dict(
                        single_thing["financials"]["cash_flow_statement"],
                        orient="index",
                    ).value
                )
                cash_flows = pd.concat([cash_flows, values], axis=1)
    if statement == "Balance_Sheet":
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
