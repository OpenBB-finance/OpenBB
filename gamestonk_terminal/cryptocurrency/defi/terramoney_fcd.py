"""Terra Money FCD model"""
__docformat__ = "numpy"

from typing import Any
from datetime import datetime
import requests
import pandas as pd
from gamestonk_terminal.cryptocurrency.dataframe_helpers import denominate_number


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
    response = requests.get(
        url, headers={"Accept": "application/json", "User-Agent": "GST"}
    )
    if not 200 <= response.status_code < 300:
        raise Exception(f"fcd terra api exception: {response.text}")
    try:
        return response.json()
    except Exception as e:
        raise ValueError(f"Invalid Response: {response.text}") from e


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


def get_staking_account_info(address: str = "") -> dict:
    """Get staking info for provided terra account [Source: https://fcd.terra.dev/v1]

    Parameters
    ----------
    address: str
        terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg
    Returns
    -------
    dict:
        staking info for given address
    """

    response = _make_request(f"staking/{address}")
    results: dict[str, Any] = {"myDelegations": []}

    for field in ["availableLuna", "delegationTotal"]:
        results[field] = denominate_number(response.get(field, 0))

    my_delegations = response.get("myDelegations")
    if my_delegations:
        for delegation in my_delegations:
            validator = _adjust_delegation_info(delegation)
            results["myDelegations"].append(validator)
    results["myDelegations"] = pd.DataFrame(results["myDelegations"])
    results["totalRewards"] = denominate_number(
        response.get("rewards", {}).get("total", 0)
    )
    return results


def get_validators() -> pd.DataFrame:
    """Get information about terra validators [Source: https://fcd.terra.dev/v1]
    Returns
    -------
    pd.DataFrame
        terra validators details
    """

    response = _make_request("staking")["validators"]
    results = []
    for validator in response:
        results.append(
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
                "upTime": round((float(validator.get("upTime", 0)) * 100), 2),
                "validatorDescription": validator["description"].get("details"),
            }
        )

    return pd.DataFrame(results).sort_values(by="votingPower")


def get_proposals() -> pd.DataFrame:
    """Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/v1]

    Returns
    -------
    pd.DataFrame
        Terra blockchain governance proposals list
    """

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
    return pd.DataFrame(results)[columns]


def get_account_growth(cumulative: bool = True) -> pd.DataFrame:
    """Get terra blockchain account growth history [Source: https://fcd.terra.dev/v1]

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
    return df[["date", "totalAccountCount", "activeAccountCount"]]


def get_staking_ratio_history():
    """Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]

    Returns
    -------
    pd.DataFrame
        historical staking ratio
    """

    response = _make_request("dashboard/staking_ratio")
    df = pd.DataFrame(response)
    df["date"] = df["datetime"].apply(lambda x: datetime.fromtimestamp(x / 1000).date())
    return df[["date", "stakingRatio"]]


def get_staking_returns_history():
    """Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]

    Returns
    -------
    pd.DataFrame
        historical staking returns
    """

    response = _make_request("dashboard/staking_return")
    df = pd.DataFrame(response)
    df["date"] = df["datetime"].apply(lambda x: datetime.fromtimestamp(x / 1000).date())
    return df[["date", "annualizedReturn"]]
