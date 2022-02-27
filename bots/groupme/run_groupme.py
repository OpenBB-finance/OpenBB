import json
from bots.common.commands_dict import commands
from bots.helpers import ShowView
from bots.groupme.groupme_helpers import send_message


def get_syntax(selected, cmd):
    syntax = f"{cmd}/"
    syntax += "/".join(selected.get("required", []))
    return syntax


def handle_groupme(request):
    req = json.loads(request.decode("utf-8"))
    text = req.get("text").strip().lower()
    group_id = req.get("group_id").strip()

    if text[0] == "!":
        cmd = text[1:]
        group = cmd.split("-")[0]
        parents = {x.split("-")[0] for x in commands}
        if group in parents:
            full_cmd = cmd.split("/")
            if full_cmd[0] in commands:
                selected = commands[full_cmd[0]]
                if len(full_cmd) != len(selected.get("required", [])) + 1:
                    syntax = get_syntax(selected, full_cmd[0])
                    send_message(f"Required syntax: {syntax}", group_id)
                    return False
                else:
                    other_args = {}
                    for i, val in enumerate(full_cmd[1:]):
                        req_name = list(selected.get("required", {}).keys())[i]
                        required = selected.get("required", [])[req_name]
                        if isinstance(val, str):
                            val = val.upper()
                        if val not in required:
                            print(full_cmd[0])
                            syntax = get_syntax(selected, full_cmd[0])
                            send_message(
                                f"{syntax}\nInvalid argument for: {req_name}", group_id
                            )
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
                message += ", ".join(show_cmds)
                send_message(message, group_id)
                return False
        else:
            message = "Valid categories: "
            message += ", ".join(list(parents))
            send_message(message, group_id)
            return False
    return False
