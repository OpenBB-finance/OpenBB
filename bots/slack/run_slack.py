import os
import logging
from typing import List, Pattern, Dict, Any, Set, Union
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from bots.common.commands_dict import commands
from bots.helpers import ShowView


load_dotenv()

app = App(token=os.environ["GT_SLACK_APP_TOKEN"])

available_commands = list(commands.keys())


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


def get_arguments(
    selected: Dict[str, Any], req_name: str, channel_id: str, user_id: str, client: Any
) -> None:
    """Returns the arguments for a given command

    Parameters
    ----------
    selected : Dict[str, Any]
        The command object
    req_name : str
        The name of the requirement
    channel_id : str
        Slack channel id
    user_id : str
        Slack user id
    client : Any
        Client that sends messages to slack
    """
    if req_name == "ticker":
        message = "Please give a listed ticker"
    elif req_name == "past_transactions_days":
        message = "Please give the number of days as an integer"
    elif req_name == "raw":
        message = "Please type true or false"

    else:
        select = [str(x) for x in selected["required"].get(req_name, [])]
        selections = ", ".join(select)
        if len(selections) < 990:
            selections = f"{selections[:990]}"
        message = f"Options: {selections}"

    payload = {"channel": channel_id, "username": user_id, "text": message}
    client.chat_postMessage(**payload)


def send_options(
    name: str,
    items: Union[List[Any], Set[Any]],
    channel_id: str,
    user_id: str,
    client: Any,
) -> None:
    """Sends the options for a user

    Parameters
    ----------
    name : str
        The name of the section
    items : List[str]
        The items the user can select from
    channel_id : str
        Slack channel id
    user_id : str
        Slack user id
    client : Any
        Client that sends messages to slack
    """
    message = name
    clean = list(items)
    clean.sort()
    message += ", ".join(list(clean))
    payload = {"channel": channel_id, "username": user_id, "text": message}
    client.chat_postMessage(**payload)


@app.event("message")
def processMessage(event, client):
    """Process users' commands"""
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    if text[0] == "!":
        cmd = text[1:]
        full_cmd = cmd.split("/")
        if full_cmd[0] == "help":
            help_text = (
                "\n!disc-fidelity\n"
                "!ins-last/ticker <num>\n"
                "\n!opt-unu\n"
                "!opt-iv/ticker\n"
                "!opt-vsurf/ticker <z>\n"
                "!opt-hist/ticker <strike> <expiration> <opt-typ>\n"
                "!opt-oi/ticker <expiration> <min-sp> <max-sp>\n"
                "!opt-vol/ticker <expiration> <min-sp> <max-sp>\n"
                "!opt-overview/ticker <expiration> <min-sp> <max-sp>\n"
                "!opt-chain/ticker <expiration> <opt-typ> <min-sp> <max-sp>\n"
                "\n!ta-summary/ticker\n"
                "!ta-view/ticker\n"
                "!ta-recom/ticker\n"
                "!ta-obv/ticker <START> <END>\n"
                "!ta-fib/ticker <START> <END>\n"
                "!ta-ad/ticker <OPEN> <START> <END>\n"
                "!ta-cg/ticker <LENGTH> <START> <END>\n"
                "!ta-fisher/ticker <LENGTH> <START> <END>\n"
                "!ta-cci/ticker <LENGTH> <SCALAR> <START> <END>\n"
                "!ta-ema/ticker <WINDOW> <OFFSET> <START> <END>\n"
                "!ta-sma/ticker <WINDOW> <OFFSET> <START> <END>\n"
                "!ta-wma/ticker <WINDOW> <OFFSET> <START> <END>\n"
                "!ta-hma/ticker <WINDOW> <OFFSET> <START> <END>\n"
                "!ta-zlma/ticker <WINDOW> <OFFSET> <START> <END>\n"
                "!ta-aroon/ticker <LENGTH> <SCALAR> <START> <END>\n"
                "!ta-adosc/ticker <OPEN> <FAST> <SLOW> <START> <END>\n"
                "!ta-macd/ticker <FAST> <SLOW> <SIGNAL> <START> <END>\n"
                "!ta-kc/ticker <LENGTH> <SCALAR> <MA-MODE> <START> <END>\n"
                "!ta-adx/ticker <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
                "!ta-rsi/ticker <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
                "!ta-stoch/ticker <FAST-K> <SLOW-D> <SLOW-K> <START> <END>\n"
                "!ta-bbands/ticker <LENGTH> <SCALAR> <MA-MODE> <START> <END>\n"
                "!ta-donchian/ticker <LWR-LENGTH> <UPR-LENGTH> <START> <END>\n"
                "\n!dd-est/ticker\n"
                "!dd-sec/ticker\n"
                "!dd-analyst/ticker\n"
                "!dd-supplier/ticker\n"
                "!dd-customer/ticker\n"
                "!dd-arktrades/ticker\n"
                "!dd-pt/ticker <RAW> <DATE-START>\n"
                "\n!dps-hsi <NUM>\n"
                "!dps-shorted/(NUM)\n"
                "!dps-psi/ticker\n"
                "!dps-spos/ticker\n"
                "!dps-dpotc/ticker\n"
                "!dps-pos <NUM> <SORT>\n"
                "!dps-sidtc <NUM> <SORT>\n"
                "!dps-ftd/ticker <DATE-START> <DATE-END>\n"
                "\n!scr-presets-default\n"
                "!scr-presets-custom\n"
                "!scr-historical/(SIGNAL) <START>\n"
                "!scr-overview/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
                "!scr-technical/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
                "!scr-valuation/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
                "!scr-financial/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
                "!scr-ownership/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
                "!scr-performance/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
                "\n!gov-histcont/ticker\n"
                "!gov-lobbying/ticker <NUM>\n"
                "!gov-toplobbying <NUM> <RAW>\n"
                "!gov-lastcontracts <DAYS> <NUM>\n"
                "!gov-contracts/ticker <DAYS> <RAW>\n"
                "!gov-qtrcontracts <ANALYSIS> <NUM>\n"
                "!gov-lasttrades <GOV-TYPE> <DAYS> <REP>\n"
                "!gov-gtrades/ticker <GOV-TYPE> <MONTHS> <RAW>\n"
                "!gov-topbuys <GOV-TYPE> <MONTHS> <NUM> <RAW>\n"
                "!gov-topsells <GOV-TYPE> <MONTHS> <NUM> <RAW>\n"
                "\n`<DAYS> = Past Transaction Days`\n"
                "`<MONTHS> = Past Transaction Months`"
                "\n!econ-softs\n"
                "!econ-meats\n"
                "!econ-energy\n"
                "!econ-metals\n"
                "!econ-grains\n"
                "!econ-futures\n"
                "!econ-usbonds\n"
                "!econ-glbonds\n"
                "!econ-indices\n"
                "!econ-overview\n"
                "!econ-feargreed\n"
                "!econ-currencies\n"
                "!econ-valuation <GROUP>\n"
                "!econ-performance <GROUP>\n"
            )
            payload = {
                "channel": channel_id,
                "username": user_id,
                "text": help_text,
            }
            client.chat_postMessage(**payload)
            return True
        group = full_cmd[0].split("-")[0]
        parents = {x.split("-")[0] for x in commands}
        if group in parents:
            if full_cmd[0] in commands:
                selected = commands[full_cmd[0]]
                if len(full_cmd) != len(selected.get("required", [])) + 1:
                    syntax = get_syntax(selected, full_cmd[0])
                    payload = {
                        "channel": channel_id,
                        "username": user_id,
                        "text": f"Required syntax: {syntax}",
                    }
                    client.chat_postMessage(**payload)
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
                        payload = {
                            "channel": channel_id,
                            "username": user_id,
                            "text": f"{syntax}\nInvalid argument for: {req_name}",
                        }
                        client.chat_postMessage(**payload)
                        get_arguments(selected, req_name, channel_id, user_id, client)
                        return False
                    other_args[req_name] = val
                func = selected["function"]
                ShowView().slack(func, channel_id, user_id, client, **other_args)
                return True
            show_cmds = []
            for command in commands:
                if group == command[: len(group)]:
                    show_cmds.append(command)
            send_options("Valid commands: ", show_cmds, channel_id, user_id, client)
            return False
        send_options("Valid categories: ", parents, channel_id, user_id, client)
        return False
    return False


if __name__ == "__main__":
    # TODO: replace with GST logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    handler = SocketModeHandler(
        app,
        os.environ["GT_SLACK_BOT_TOKEN"],
    )
    handler.start()
