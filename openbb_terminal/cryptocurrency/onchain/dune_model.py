import pandas as pd
import logging
from requests import post
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.helper_funcs import request
from openbb_terminal.decorators import check_api_key, log_start_end

logger = logging.getLogger(__name__)

BASE_URL = "https://api.dune.com/api/v1/"

def make_api_url(module, action, ID):
    """
    We shall use this function to generate a URL to call the API.
    """

    url = BASE_URL + module + "/" + ID + "/" + action

    return url


def execute_query(query_id, engine="medium"):
    """
    Takes in the query ID and engine size.
    Specifying the engine size will change how quickly your query runs. 
    The default is "medium" which spends 10 credits, while "large" spends 20 credits.
    Calls the API to execute the query.
    Returns the execution ID of the instance which is executing the query.
    """

    url = make_api_url("query", "execute", query_id)
    params = {
        "performance": engine,
    }
    response = post(url, headers={
        "x-dune-api-key": get_current_user().credentials.API_DUNE_KEY
    }, params=params)
    data = response.json()
    execution_id = data['execution_id']

    return execution_id


def get_query_status(execution_id):
    """
    Takes in an execution ID.
    Fetches the status of query execution using the API
    Returns the status response object
    """

    url = make_api_url("execution", "status", execution_id)
    response = request(url, headers={
        "x-dune-api-key": get_current_user().credentials.API_DUNE_KEY
    })

    return response


def get_query_results(execution_id):
    """
    Takes in an execution ID.
    Fetches the results returned from the query using the API
    Returns the results response object
    """

    url = make_api_url("execution", "results", execution_id)
    response = request(url, headers={
        "x-dune-api-key": get_current_user().credentials.API_DUNE_KEY
    })

    return response


def cancel_query_execution(execution_id):
    """
    Takes in an execution ID.
    Cancels the ongoing execution of the query.
    Returns the response object.
    """

    url = make_api_url("execution", "cancel", execution_id)
    response = request(url, headers={
        "x-dune-api-key": get_current_user().credentials.API_DUNE_KEY
    })

    return response

@log_start_end(log=logger)
@check_api_key(["API_DUNE_KEY"])
def get_query(
    id: str,
    engine: str = "medium",
) -> pd.DataFrame:
    """
    Get query from Dune [Source: https://dune.com/]

    Parameters
    ----------
    id : str
        Query ID
    engine : str, optional
        Engine size, by default "medium"

    Returns
    -------
    pd.DataFrame
        DataFrame with query results
    """

    execution_id = execute_query(id, engine)
    response_status = get_query_status(execution_id)
    while response_status.json()['state'] != 'QUERY_STATE_COMPLETED':
        response_status = get_query_status(execution_id)

    response = get_query_results(execution_id)

    df = pd.DataFrame(response.json()['result']['rows'])

    return df
