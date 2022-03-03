import json
from typing import List, Pattern, Dict, Any, Set, Union

from bots.common.commands_dict import commands
from bots.groupme.groupme_helpers import send_message
from bots.helpers import ShowView


def get_syntax(selected: Dict[str, Any], cmd: str) -> str:
    """Returns the syntax for a given command

    Parameters
    ----------
    selected : Dict[str, Any]
        The command object
    cmd : str
        The command that was attempted

    Returns
    ---------
    syntax : str
        The syntax for the given command
    """

    syntax = f"{cmd}/"
    syntax += "/".join(selected.get("required", []))
    return syntax


def get_arguments(selected: Dict[str, Any], req_name: str, group_id: str) -> None:
    """Returns the arguments for a given command

    Parameters
    ----------
    selected : Dict[str, Any]
        The command object
    req_name : str
        The name of the requirement
    group_id : str
        The groupme chat id
    """

    if req_name == "ticker":
        send_message("Please give a listed ticker", group_id)
    elif req_name == "past_transactions_days":
        send_message("Please give the number of days as an integer", group_id)
    elif req_name == "raw":
        send_message("Please type true or false", group_id)
    else:
        select = [str(x) for x in selected["required"].get(req_name, [])]
        selections = ", ".join(select)
        if len(selections) < 990:
            selections = f"{selections[:990]}"
        send_message(f"Options: {selections}", group_id)


def send_options(name: str, items: Union[List[Any], Set[Any]], group_id: str) -> None:
    """Sends the options for a user

    Parameters
    ----------
    name : str
        The name of the section
    items : List[str]
        The items the user can select from
    group_id : str
        The groupme chat id
    """
    message = name
    clean = list(items)
    clean.sort()
    message += ", ".join(list(clean))
    send_message(message, group_id)


def handle_groupme(request) -> bool:
    """Handles groupme bot inputs

    Parameters
    ----------
    request : Request
        The request object provided by FASTAPI

    Returns
    ----------
    success : bool
        Whether the response was sent successfully
    """

    req = json.loads(request.decode("utf-8"))
    text = req.get("text").strip().lower()
    group_id = req.get("group_id").strip()

    if text[0] == "!":
        cmd = text[1:]
        full_cmd = cmd.split("/")
        group = full_cmd[0].split("-")[0]
        parents = {x.split("-")[0] for x in commands}
        if group in parents:
            if full_cmd[0] in commands:
                selected = commands[full_cmd[0]]
                if len(full_cmd) != len(selected.get("required", [])) + 1:
                    syntax = get_syntax(selected, full_cmd[0])
                    send_message(f"Required syntax: {syntax}", group_id)
                    return False
                other_args = {}
                for i, val in enumerate(full_cmd[1:]):
                    req_name = list(selected.get("required", {}).keys())[i]
                    required = selected.get("required", [])[req_name]
                    if isinstance(required, List) and required != [True, False]:
                        required = [str(x) for x in required]
                    if isinstance(val, str) and req_name in ["ticker"]:
                        val = val.upper()
                    elif isinstance(val, str) and req_name == "raw":
                        val = bool(val)
                    if (isinstance(required, List) and val not in required) or (
                        isinstance(required, Pattern) and not required.match(val)
                    ):
                        syntax = get_syntax(selected, full_cmd[0])
                        send_message(
                            f"{syntax}\nInvalid argument for: {req_name}", group_id
                        )
                        get_arguments(selected, req_name, group_id)
                        return False
                    other_args[req_name] = val
                func = selected["function"]
                ShowView().groupme(func, group_id, cmd, **other_args)
                return True
            else:
                show_cmds = []
                for command in commands:
                    if group == command[: len(group)]:
                        show_cmds.append(command)
                send_options("Valid commands: ", show_cmds, group_id)
                return False
        else:
            send_options("Valid categories: ", parents, group_id)
            return False
    return False
