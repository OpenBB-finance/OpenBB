import json
from typing import List, Pattern

from bots.common.commands_dict import commands
from bots.groupme.groupme_helpers import send_message
from bots.helpers import ShowView


def get_syntax(selected, cmd):
    syntax = f"{cmd}/"
    syntax += "/".join(selected.get("required", []))
    return syntax


def get_arguments(selected, req_name, group_id):
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


def handle_groupme(request):
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
                    if isinstance(val, str) and req_name == "ticker":
                        val = val.upper()
                    elif isinstance(val, str) and req_name == "raw":
                        val = bool(val)
                    print(f"{val} in {required}")
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
                message = "Valid commands: "
                show_cmds.sort()
                message += ", ".join(show_cmds)
                send_message(message, group_id)
                return False
        else:
            message = "Valid categories: "
            parents_clean = list(parents)
            parents_clean.sort()
            message += ", ".join(list(parents_clean))
            send_message(message, group_id)
            return False
    return False
