"""Terra Money FCD model"""
__docformat__ = "numpy"

import logging
import textwrap
from datetime import datetime
from typing import Any, Dict, Tuple

import pandas as pd

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    denominate_number,
    lambda_replace_unicode,
    prettify_column_names,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

GOV_COLUMNS = [
    "submitTime",
    "id",
    "depositEndTime",
    "status",
    "type",
    "title",
    "Yes",
    "No",
]
GOV_STATUSES = ["voting", "deposit", "passed", "rejected", "all"]
VALIDATORS_COLUMNS = [
    "validatorName",
    "tokensAmount",
    "votingPower",
    "commissionRate",
    "status",
    "uptime",
]


@log_start_end(log=logger)
def _make_request(endpoint: str) -> dict:
    """Helper method handles terra fcd api requests. [Source: https://fcd.terra.dev/v1]

    Parameters
    ----------
    endpoint: str
        endpoint url

    Returns
    -------
    dict:
        dictionary with response data
    """

    url = f"https://fcd.terra.dev/v1/{endpoint}"
    response = request(url, headers={"Accept": "application/json", "User-Agent": "GST"})
    if not 200 <= response.status_code < 300:
        console.print(
            f"[red]fcd terra api exception: {response.json()['type']}[/red]\n"
        )
        return {}
    try:
        return response.json()
    except Exception as e:
        logger.exception("Invalid Response: %s", str(e))
        console.print(
            f"[red]fcd terra api exception: {response.json()['type']}[/red]\n"
        )
        return {}


@log_start_end(log=logger)
def _adjust_delegation_info(delegation: dict) -> dict:
    """Helper method which removes redundant fields from delegation info dictionary,
    and denominate value fields. [Source: https://fcd.terra.dev/v1]

    Parameters
    ----------
    delegation:
        dictionary object with delegation data e.g.

    Returns
    -------
    dict
        adjusted dictionary with delegation data
    """

    delegation_info = {}
    for key, value in delegation.items():
        if key in ["amountDelegated", "totalReward"]:
            delegation_info[key] = denominate_number(value)
        elif key in ["validatorAddress", "rewards"]:
            continue
        else:
            delegation_info[key] = value
    return delegation_info


@log_start_end(log=logger)
def get_staking_account_info(address: str = "") -> Tuple[pd.DataFrame, str]:
    """Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    address: str
        terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg
    Returns
    -------
    Tuple[pd.DataFrame, str]
        luna delegations and summary report for given address
    """

    response = _make_request(f"staking/{address}")
    results: Dict[str, Any] = {"myDelegations": []}

    for field in ["availableLuna", "delegationTotal"]:
        results[field] = denominate_number(response.get(field, 0))

    my_delegations = response.get("myDelegations")
    if my_delegations:
        for delegation in my_delegations:
            validator = _adjust_delegation_info(delegation)
            results["myDelegations"].append(validator)

    df = pd.DataFrame(results["myDelegations"])

    try:
        df["validatorName"] = df["validatorName"].apply(
            lambda x: lambda_replace_unicode(x)
        )
        df.columns = prettify_column_names(list(df.columns))
    except KeyError:
        df = pd.DataFrame()

    results["totalRewards"] = denominate_number(
        response.get("rewards", {}).get("total", 0)
    )

    report = f"""Overview:
    Address: {address}
    Available Luna: {results['availableLuna']}
    Delegated Luna: {results['delegationTotal']}
    Total Rewards:  {results['totalRewards']}\n"""
    report += "\nDelegations: " if not df.empty else "\nNo delegations found\n"

    return df, report


@log_start_end(log=logger)
def get_validators(sortby: str = "votingPower", ascend: bool = True) -> pd.DataFrame:
    """Get information about terra validators [Source: https://fcd.terra.dev/swagger]

    Parameters
    -----------
    sortby: str
        Key by which to sort data. Choose from:
        validatorName, tokensAmount, votingPower, commissionRate, status, uptime
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pd.DataFrame
        terra validators details
    """

    response = _make_request("staking")["validators"]
    results = [
        {
            "accountAddress": validator["accountAddress"],
            "validatorName": validator["description"].get("moniker"),
            "tokensAmount": denominate_number(validator["tokens"]),
            "votingPower": round(
                (float(validator["votingPower"].get("weight")) * 100), 2
            ),
            "commissionRate": round(
                (float(validator["commissionInfo"].get("rate", 0)) * 100), 2
            ),
            "status": validator["status"],
            "uptime": round((float(validator.get("upTime", 0)) * 100), 2),
        }
        for validator in response
    ]

    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_proposals(
    status: str = "", sortby: str = "id", ascend: bool = True, limit: int = 10
) -> pd.DataFrame:
    """Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    status: str
        status of proposal, one from list: ['Voting','Deposit','Passed','Rejected']
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    limit: int
        Number of records to display

    Returns
    -------
    pd.DataFrame
        Terra blockchain governance proposals list
    """

    statuses = ["Voting", "Deposit", "Passed", "Rejected"]
    response = _make_request("gov/proposals")["proposals"]
    results = []
    votes_options = ["Yes", "Abstain", "No", "NoWithVeto"]
    for proposal in response:
        deposit = proposal.pop("deposit")
        proposal["depositEndTime"] = deposit.get("depositEndTime")
        vote = proposal.pop("vote")
        proposal.pop("proposer")
        for opt in votes_options:
            proposal[opt] = vote["count"].get(opt)

        results.append(proposal)
    columns = [
        "id",
        "submitTime",
        "depositEndTime",
        "status",
        "type",
        "title",
        "Yes",
        "No",
        "Abstain",
        "NoWithVeto",
    ]
    df = pd.DataFrame(results)[columns]
    df[["id", "Yes", "No", "Abstain", "NoWithVeto"]] = df[
        ["id", "Yes", "No", "Abstain", "NoWithVeto"]
    ].astype(int, errors="ignore")
    df["title"] = df["title"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=40)) if isinstance(x, str) else x
    )

    for col in ["submitTime", "depositEndTime"]:
        df[col] = df[col].apply(lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M"))

    if status.title() in statuses:
        df = df[df["status"] == status.title()]
    df = df.sort_values(by=sortby, ascending=ascend).head(limit)
    df.columns = prettify_column_names(df.columns)
    return df


@log_start_end(log=logger)
def get_account_growth(cumulative: bool = True) -> pd.DataFrame:
    """Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    cumulative: bool
        distinguish between periodical and cumulative account growth data

    Returns
    -------
    pd.DataFrame
        historical data of accounts growth
    """

    response = _make_request("dashboard/account_growth")
    kind = "cumulative" if cumulative else "periodic"
    df = pd.DataFrame(response[kind])
    df["date"] = df["datetime"].apply(lambda x: datetime.fromtimestamp(x / 1000).date())
    df = df[["date", "totalAccountCount", "activeAccountCount"]]
    df.columns = ["date", "Total accounts", "Active accounts"]
    return df


@log_start_end(log=logger)
def get_staking_ratio_history(limit: int = 200):
    """Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    limit: int
        The number of ratios to show

    Returns
    -------
    pd.DataFrame
        historical staking ratio
    """

    response = _make_request("dashboard/staking_ratio")
    df = pd.DataFrame(response)
    df["date"] = df["datetime"].apply(lambda x: datetime.fromtimestamp(x / 1000).date())
    df["stakingRatio"] = df["stakingRatio"].apply(lambda x: round(float(x) * 100, 2))
    df = df[["date", "stakingRatio"]]
    df = df.sort_values("date", ascending=False).head(limit)
    df = df.set_index("date")
    return df


@log_start_end(log=logger)
def get_staking_returns_history(limit: int = 200):
    """Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]

    Parameters
    ----------
    limit: int
        The number of returns to show

    Returns
    -------
    pd.DataFrame
        historical staking returns
    """

    response = _make_request("dashboard/staking_return")
    df = pd.DataFrame(response)
    df["date"] = df["datetime"].apply(lambda x: datetime.fromtimestamp(x / 1000).date())
    df["annualizedReturn"] = df["annualizedReturn"].apply(
        lambda x: round(float(x) * 100, 2)
    )
    df = df[["date", "annualizedReturn"]]
    df = df.sort_values("date", ascending=False).head(limit)
    df = df.set_index("date")

    return df
