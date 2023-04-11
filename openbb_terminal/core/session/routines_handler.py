from typing import Dict

import openbb_terminal.core.session.hub_model as Hub
from openbb_terminal.account.account_model import save_routine

# move all routines stuff here


def download_routines(
    auth_header: str,
) -> Dict[str, str]:
    """Download a routine from the server.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".

    Returns
    -------
    Dict[str, str]
        The routines.
    """
    routines_dict = {}

    fields = "name%2Cscript"
    response = Hub.list_routines(auth_header, fields=fields, page=1, size=100)
    if response and response.status_code == 200:
        content = response.json()
        items = content.get("items", [])
        for routine in items:
            name = routine.get("name", "")
            if name:
                routines_dict[name] = routine.get("script", "")

    response = Hub.get_default_routines()
    if response and response.status_code == 200:
        content = response.json()
        data = content.get("data", [])
        for routine in data:
            name = routine.get("name", "")
            if name:
                routines_dict[name] = routine.get("script", "")
    return routines_dict


def download_and_save_routines(auth_header: str):
    """Download and save routines.

    Parameters
    ----------
    auth_header : str
        The authorization header, e.g. "Bearer <token>".
    """
    routines = download_routines(auth_header)
    for name, content in routines.items():
        save_routine(file_name=f"{name}.openbb", routine=content, force=True)
