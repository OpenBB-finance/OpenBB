import os
from typing import List, Pattern, Dict, Any, Union, Set
import telebot
from dotenv import load_dotenv
from bots.common.commands_dict import commands
from bots.helpers import ShowView

load_dotenv()

bot = telebot.TeleBot(os.getenv("GT_TELEGRAM_BOT_TOKEN"))

bot_commands = [
    telebot.types.BotCommand("/start", "main menu"),
    telebot.types.BotCommand("/help", "main menu"),
]
for command in commands:
    bot_commands.append(
        telebot.types.BotCommand(
            command.replace("-", "_"),
            commands[command]["function"].__doc__.split("Parameters")[0][:256].strip(),
        )
    )
bot.set_my_commands(commands=bot_commands)

available_commands = [cmd.replace("-", "_") for cmd in commands.keys()]


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


def get_arguments(selected: Dict[str, Any], req_name: str, message: Any) -> None:
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
        bot.reply_to(message, "Please give a listed ticker")
    elif req_name == "past_transactions_days":
        bot.reply_to(message, "Please give the number of days as an integer")
    elif req_name == "raw":
        bot.reply_to(message, "Please type true or false")
    else:
        select = [str(x) for x in selected["required"].get(req_name, [])]
        selections = ", ".join(select)
        if len(selections) < 990:
            selections = f"{selections[:990]}"
        bot.reply_to(message, f"Options: {selections}")


def send_options(name: str, items: Union[List[Any], Set[Any]], message: Any) -> None:
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
    help_message = name
    clean = list(items)
    clean.sort()
    help_message += ", ".join(list(clean))
    bot.reply_to(message, help_message)


def detect_valid_command(message):
    cmd = message.text[1:]
    full_cmd = cmd.split("/")[0]
    return full_cmd in available_commands


@bot.message_handler(commands=["start", "Start"])
def send_welcome(message):
    text = """
    Welcome to *Gamestonk Terminal Bot*

    [gamestonk.dev](https://github.com/GamestonkTerminal/GamestonkTerminal)
    [GitHub Repo](https://github.com/GamestonkTerminal/GamestonkTerminal)
    """
    bot.reply_to(message, text, parse_mode="MARKDOWN")


@bot.message_handler(commands=["help", "Help"])
def send_help(message):
    helptext = (
        "\n[disc-fidelity]()\n"
        "[ins-last](ticker) <num>\n"
        "\n[opt-unu]()\n"
        "[opt-iv](ticker)\n"
        "[opt-vsurf](ticker) <z>\n"
        "[opt-hist](ticker) <strike> <expiration> <opt-typ>\n"
        "[opt-oi](ticker) <expiration> <min-sp> <max-sp>\n"
        "[opt-vol](ticker) <expiration> <min-sp> <max-sp>\n"
        "[opt-overview](ticker) <expiration> <min-sp> <max-sp>\n"
        "[opt-chain](ticker) <expiration> <opt-typ> <min-sp> <max-sp>\n"
        "\n[ta-summary](ticker)\n"
        "[ta-view](ticker)\n"
        "[ta-recom](ticker)\n"
        "[ta-obv](ticker) <START> <END>\n"
        "[ta-fib](ticker) <START> <END>\n"
        "[ta-ad](ticker) <OPEN> <START> <END>\n"
        "[ta-cg](ticker) <LENGTH> <START> <END>\n"
        "[ta-fisher](ticker) <LENGTH> <START> <END>\n"
        "[ta-cci](ticker) <LENGTH> <SCALAR> <START> <END>\n"
        "[ta-ema](ticker) <WINDOW> <OFFSET> <START> <END>\n"
        "[ta-sma](ticker) <WINDOW> <OFFSET> <START> <END>\n"
        "[ta-wma](ticker) <WINDOW> <OFFSET> <START> <END>\n"
        "[ta-hma](ticker) <WINDOW> <OFFSET> <START> <END>\n"
        "[ta-zlma](ticker) <WINDOW> <OFFSET> <START> <END>\n"
        "[ta-aroon](ticker) <LENGTH> <SCALAR> <START> <END>\n"
        "[ta-adosc](ticker) <OPEN> <FAST> <SLOW> <START> <END>\n"
        "[ta-macd](ticker) <FAST> <SLOW> <SIGNAL> <START> <END>\n"
        "[ta-kc](ticker) <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
        "[ta-adx](ticker) <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
        "[ta-rsi](ticker) <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
        "[ta-stoch](ticker) <FAST_K> <SLOW_D> <SLOW_K> <START> <END>\n"
        "[ta-bbands](ticker) <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
        "[ta-donchian](ticker) <LWR_LENGTH> <UPR_LENGTH> <START> <END>\n"
        "\n[dd-est](ticker)\n"
        "[dd-sec](ticker)\n"
        "[dd-analyst](ticker)\n"
        "[dd-supplier](ticker)\n"
        "[dd-customer](ticker)\n"
        "[dd-arktrades](ticker)\n"
        "[dd-pt](ticker) <RAW> <DATE_START>\n"
        "\n[dps.hsi]() <NUM>\n"
        "[dps.shorted](NUM)\n"
        "[dps.psi](ticker)\n"
        "[dps.spos](ticker)\n"
        "[dps.dpotc](ticker)\n"
        "[dps.pos]() <NUM> <SORT>\n"
        "[dps.sidtc]() <NUM> <SORT>\n"
        "[dps.ftd](ticker) <DATE_START> <DATE_END>\n"
        "\n[scr.presets_default]()\n"
        "[scr.presets_custom]()\n"
        "[scr.historical](SIGNAL) <START>\n"
        "[scr.overview](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "[scr.technical](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "[scr.valuation](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "[scr.financial](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "[scr.ownership](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "[scr.performance](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "\n[gov-histcont](ticker)\n"
        "[gov-lobbying](ticker) <NUM>\n"
        "[gov-toplobbying]() <NUM> <RAW>\n"
        "[gov-lastcontracts]() <DAYS> <NUM>\n"
        "[gov-contracts](ticker) <DAYS> <RAW>\n"
        "[gov-qtrcontracts]() <ANALYSIS> <NUM>\n"
        "[gov-lasttrades]() <GOV_TYPE> <DAYS> <REP>\n"
        "[gov-gtrades](ticker) <GOV_TYPE> <MONTHS> <RAW>\n"
        "[gov-topbuys]() <GOV_TYPE> <MONTHS> <NUM> <RAW>\n"
        "[gov-topsells]() <GOV_TYPE> <MONTHS> <NUM> <RAW>\n"
        "\n`<DAYS> = Past Transaction Days`\n"
        "`<MONTHS> = Past Transaction Months`"
        "\n[econ-softs]()\n"
        "[econ-meats]()\n"
        "[econ-energy]()\n"
        "[econ-metals]()\n"
        "[econ-grains]()\n"
        "[econ-futures]()\n"
        "[econ-usbonds]()\n"
        "[econ-glbonds]()\n"
        "[econ-indices]()\n"
        "[econ-overview]()\n"
        "[econ-feargreed]()\n"
        "[econ-currencies]()\n"
        "[econ-valuation]() <GROUP>\n"
        "[econ-performance]() <GROUP>\n"
    )
    bot.reply_to(message, helptext)


@bot.message_handler(func=lambda m: True)
def send_command(message):
    bot.send_chat_action(message.chat.id, action="typing")
    cmd = message.text[1:]
    full_cmd = cmd.split("/")
    group = full_cmd[0].split("_")[0]
    parents = {x.split("_")[0] for x in available_commands}
    if group in parents:
        if full_cmd[0] in available_commands:
            selected = commands[full_cmd[0].replace("_", "-")]
            if len(full_cmd) != len(selected.get("required", [])) + 1:
                syntax = get_syntax(selected, full_cmd[0])
                bot.reply_to(message, f"Required syntax: {syntax}")
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
                    bot.reply_to(message, f"{syntax}\nInvalid argument for: {req_name}")
                    get_arguments(selected, req_name, message)
                    return False
                other_args[req_name] = val
            func = selected["function"]
            ShowView().telegram(func, message, bot, cmd.replace("_", "-"), **other_args)
            return True
        show_cmds = []
        for a_cmd in available_commands:
            if group == a_cmd[: len(group)]:
                show_cmds.append(a_cmd)
        send_options("Valid commands: ", show_cmds, message)
        return False
    send_options("Valid categories: ", parents, message)
    return False


bot.infinity_polling()
