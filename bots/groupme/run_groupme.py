import json
from bots.common.commands_dict import commands
from bots.helpers import ShowView
from bots.groupme.groupme_helpers import send_message


def handle_groupme(request):
    req = json.loads(request.decode("utf-8"))
    text = req.get("text").strip().lower()
    group_id = req.get("group_id").strip()

    if text[0] == "!":
        cmd = text[1:]
        parents = set([x.split("-")[0] for x in commands])
        if cmd.split("-")[0] in parents:
            full_cmd = cmd.split("/")
            if full_cmd[0] in commands:
                selected = commands[full_cmd[0]]
                if len(full_cmd) != len(selected.get("required", [])) + 1:
                    syntax = f"{cmd}/"
                    syntax += "/".join(selected.get("required", []))
                    send_message(f"Required syntax: {syntax}", group_id)
                    return False
                else:
                    for i, val in enumerate(full_cmd[1:]):
                        req_name = list(selected.get("required", {}).keys())[i]
                        required = selected.get("required", [])[req_name]()
                        if val not in required():
                            send_message(f"Invalid argument for: {req_name}", group_id)
                    func = selected["function"]
                    other_args = {}
                    ShowView().groupme(func, group_id, cmd, **other_args)
                    return True
            else:
                message = "Valid commands: "
                message += ", ".join(commands)
                send_message(message, group_id)
                return False
        else:
            message = "Valid categories: "
            message += ", ".join(parents)
            send_message(message, group_id)
            return False
    return False
