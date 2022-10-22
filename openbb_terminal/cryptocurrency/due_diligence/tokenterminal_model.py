"""Token Terminal Model"""
import logging

from typing import List, Dict
import pandas as pd
from tokenterminal import TokenTerminal
from openbb_terminal.decorators import log_start_end
from openbb_terminal import config_terminal as cfg

logger = logging.getLogger(__name__)

token_terminal = TokenTerminal(key=cfg.API_TOKEN_TERMINAL_KEY)

# Fetch all data for projects
PROJECTS_DATA = token_terminal.get_all_projects()

METRICS = [
    "twitter_followers",
    "gmv_annualized",
    "market_cap",
    "take_rate",
    "revenue",
    "revenue_protocol",
    "tvl",
    "pe",
    "pe_circulating",
    "ps",
    "ps_circulating",
]


@log_start_end(log=logger)
def get_possible_metrics() -> List[str]:
    """This function returns the available metrics.

    Returns
    ----------
    List[str]
        A list with the available metrics values.
    """
    return METRICS


@log_start_end(log=logger)
def get_project_ids() -> List[str]:
    """This function returns the available project ids.

    Returns
    ----------
    List[str]
        A list with the all the project IDs
    """
    if PROJECTS_DATA.get("message", "") == "Invalid authorization header":
        return []
    return [project["project_id"] for project in PROJECTS_DATA]


@log_start_end(log=logger)
def get_fundamental_metric_from_project(
    metric: str,
    project: str,
) -> pd.Series:
    """Get fundamental metrics from a single project [Source: Token Terminal]

    Parameters
    ----------
    metric : str
        The metric of interest. See `get_possible_metrics()` for available metrics.
    project : str
        The project of interest. See `get_possible_projects()` for available categories.

    Returns
    -------
    pandas.Series:
        Date, Metric value
    """
    project_metrics = token_terminal.get_historical_metrics(project)

    metric_date = list()
    metric_value = list()
    for proj in project_metrics:
        if metric in proj:
            val = proj[metric]
            if isinstance(val, (float, int)):
                metric_value.append(val)
                metric_date.append(proj["datetime"])
        else:
            return pd.Series(dtype="float64")

    if metric_value:
        return pd.Series(index=pd.to_datetime(metric_date), data=metric_value)[::-1]

    return pd.Series(dtype="float64")


@log_start_end(log=logger)
def get_description(
    project: str,
) -> Dict:
    """Get description from a single project [Source: Token Terminal]

    Parameters
    ----------
    project : str
        The project of interest. See `get_possible_projects()` for available categories.

    Returns
    -------
    Dict
        Description of the project with fields: 'how', 'who', 'what', 'funding',
        'competition', 'business_model', 'github_contributors'
    """
    for p in PROJECTS_DATA:
        if p["project_id"] == project:
            return p["description"]

    return Dict()
