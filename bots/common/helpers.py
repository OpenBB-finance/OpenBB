from typing import Any, Dict, List, Pattern, Set, Union

from bots.common.commands_dict import commands

available_commands = list(commands.keys())


def send_options(name: str, items: Union[List[Any], Set[Any]], sender: Any) -> None:
    """Sends the options for a user

    Parameters
    ----------
    name : str
        The name of the section
    items : List[str]
        The items the user can select from
    sender : Any
        Lambda function that sends a given message
    """
    help_message = name
    clean = list(items)
    clean.sort()
    help_message += "\n/" + "\n /".join(list(clean))
    sender(help_message)


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


def get_arguments(selected: Dict[str, Any], req_name: str, sender: Any) -> None:
    """Returns the arguments for a given command

    Parameters
    ----------
    selected : Dict[str, Any]
        The command object
    req_name : str
        The name of the requirement
    sender : Any
        Lambda function that sends a given message
    """

    if req_name == "ticker":
        sender("Please give a listed ticker")
    elif req_name == "past_transactions_days":
        sender("Please give the number of days as an integer")
    elif req_name == "raw":
        sender("Please type true or false")
    else:
        select = [str(x) for x in selected["required"].get(req_name, [])]
        selections = ", ".join(select)
        if len(selections) < 990:
            selections = f"{selections[:990]}"
        sender(f"Options: {selections}")


def non_slash(text: str, sender: Any, showview: Any):
    """Menu for bots that do not use slash commands

    Parameters
    ----------
    text : str
        The text the user sent
    sender : Any
        A lambda function that sends a given message
    showview : Any
        A lambda function for the given bot's ShowView method

    """
    cmd = text[1:]
    full_cmd = cmd.split("/")
    group = full_cmd[0].split("_")[0]
    parents = {x.split("_")[0] for x in available_commands}
    if text and text[0] in ["!", "/"]:
        if group in parents:
            if full_cmd[0] in available_commands:
                selected = commands[full_cmd[0]]
                if len(full_cmd) != len(selected.get("required", [])) + 1:
                    syntax = get_syntax(selected, full_cmd[0])
                    sender(f"Required syntax: /{syntax}")
                    return False
                other_args = {}
                i: int
                val: Any
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
                        sender(f"{syntax}\nInvalid argument for: {req_name}")
                        get_arguments(selected, req_name, sender)
                        return False
                    if isinstance(val, str) and req_name == "interval":
                        val = int(val)
                    elif isinstance(val, str) and req_name == "strike":
                        val = float(val)
                    other_args[req_name] = val
                func = selected["function"]
                showview(func, cmd, other_args)
                return True
            show_cmds = []
            for a_cmd in available_commands:
                if group == a_cmd[: len(group)]:
                    show_cmds.append(a_cmd)
            send_options("Valid commands: ", show_cmds, sender)
            return False
        send_options("Valid categories: ", parents, sender)
    return False
