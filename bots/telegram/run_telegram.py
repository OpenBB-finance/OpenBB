import os
import logging
from typing import List, Pattern, Dict, Any, Union, Set
import telebot
from dotenv import load_dotenv
from bots.common.commands_dict import commands
from bots.helpers import ShowView

load_dotenv()

bot = telebot.TeleBot(os.getenv("GT_TELEGRAM_BOT_TOKEN"))

bot_commands = [
    telebot.types.BotCommand("/about", "Bot information"),
    telebot.types.BotCommand("/cmds", "List of commands"),
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
    message: Any
        Object that contains telegram request info
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
    message: Any
        Object that contains telegram request info
    """
    help_message = name
    clean = list(items)
    clean.sort()
    help_message += "\n/" + "\n /".join(list(clean))
    bot.reply_to(message, help_message)


def detect_valid_command(message):
    cmd = message.text[1:]
    full_cmd = cmd.split("/")[0]
    return full_cmd in available_commands


@bot.message_handler(commands=["start", "Start", "about", "help"])
def send_welcome(message):
    text = """
Welcome to *Gamestonk Terminal Bot* 🦋
Investment Research for Everyone
Check the available commands with /cmds
    """
    markdown = telebot.types.InlineKeyboardMarkup()
    markdown.add(
        telebot.types.InlineKeyboardButton(
            "Star us on GitHub",
            url="https://github.com/GamestonkTerminal/GamestonkTerminal",
        )
    )
    markdown.add(
        telebot.types.InlineKeyboardButton(
            "Join us on Discord", url="https://discord.gg/XHsYvvjjWg"
        )
    )
    bot.send_message(
        chat_id=message.chat.id, text=text, reply_markup=markdown, parse_mode="MARKDOWN"
    )


@bot.message_handler(commands=["cmds", "commands"])
def send_cmds(message):
    helptext = (
        "\n/disc_fidelity\n"
        "/ins_last/ticker <num>\n"
        "\n/opt_unu\n"
        "/opt_iv/ticker\n"
        "/opt_vsurf/ticker <z>\n"
        "/opt_hist/ticker <strike> <expiration> <opt_typ>\n"
        "/opt_oi/ticker <expiration> <min_sp> <max_sp>\n"
        "/opt_vol/ticker <expiration> <min_sp> <max_sp>\n"
        "/opt_overview/ticker <expiration> <min_sp> <max_sp>\n"
        "/opt_chain/ticker <expiration> <opt_typ> <min_sp> <max_sp>\n"
        "\n/ta_summary/ticker\n"
        "/ta_view/ticker\n"
        "/ta_recom/ticker\n"
        "/ta_obv/ticker <START> <END>\n"
        "/ta_fib/ticker <START> <END>\n"
        "/ta_ad/ticker <OPEN> <START> <END>\n"
        "/ta_cg/ticker <LENGTH> <START> <END>\n"
        "/ta_fisher/ticker <LENGTH> <START> <END>\n"
        "/ta_cci/ticker <LENGTH> <SCALAR> <START> <END>\n"
        "/ta_ema/ticker <WINDOW> <OFFSET> <START> <END>\n"
        "/ta_sma/ticker <WINDOW> <OFFSET> <START> <END>\n"
        "/ta_wma/ticker <WINDOW> <OFFSET> <START> <END>\n"
        "/ta_hma/ticker <WINDOW> <OFFSET> <START> <END>\n"
        "/ta_zlma/ticker <WINDOW> <OFFSET> <START> <END>\n"
        "/ta_aroon/ticker <LENGTH> <SCALAR> <START> <END>\n"
        "/ta_adosc/ticker <OPEN> <FAST> <SLOW> <START> <END>\n"
        "/ta_macd/ticker <FAST> <SLOW> <SIGNAL> <START> <END>\n"
        "/ta_kc/ticker <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
        "/ta_adx/ticker <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
        "/ta_rsi/ticker <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
        "/ta_stoch/ticker <FAST_K> <SLOW_D> <SLOW_K> <START> <END>\n"
        "/ta_bbands/ticker <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
        "/ta_donchian/ticker <LWR_LENGTH> <UPR_LENGTH> <START> <END>\n"
        "\n/dd_est/ticker\n"
        "/dd_sec/ticker\n"
        "/dd_analyst/ticker\n"
        "/dd_supplier/ticker\n"
        "/dd_customer/ticker\n"
        "/dd_arktrades/ticker\n"
        "/dd_pt/ticker <RAW> <DATE_START>\n"
        "\n/dps_hsi <NUM>\n"
        "/dps_shorted/(NUM)\n"
        "/dps_psi/ticker\n"
        "/dps_spos/ticker\n"
        "/dps_dpotc/ticker\n"
        "/dps_pos <NUM> <SORT>\n"
        "/dps_sidtc <NUM> <SORT>\n"
        "/dps_ftd/ticker <DATE_START> <DATE_END>\n"
        "\n/scr_presets_default\n"
        "/scr_presets_custom\n"
        "/scr_historical/(SIGNAL) <START>\n"
        "/scr_overview/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "/scr_technical/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "/scr_valuation/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "/scr_financial/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "/scr_ownership/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "/scr_performance/(PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "\n/gov_histcont/ticker\n"
        "/gov_lobbying/ticker <NUM>\n"
        "/gov_toplobbying <NUM> <RAW>\n"
        "/gov_lastcontracts <DAYS> <NUM>\n"
        "/gov_contracts/ticker <DAYS> <RAW>\n"
        "/gov_qtrcontracts <ANALYSIS> <NUM>\n"
        "/gov_lasttrades <GOV_TYPE> <DAYS> <REP>\n"
        "/gov_gtrades/ticker <GOV_TYPE> <MONTHS> <RAW>\n"
        "/gov_topbuys <GOV_TYPE> <MONTHS> <NUM> <RAW>\n"
        "/gov_topsells <GOV_TYPE> <MONTHS> <NUM> <RAW>\n"
        "\n`<DAYS> = Past Transaction Days`\n"
        "`<MONTHS> = Past Transaction Months`"
        "\n/econ_softs\n"
        "/econ_meats\n"
        "/econ_energy\n"
        "/econ_metals\n"
        "/econ_grains\n"
        "/econ_futures\n"
        "/econ_usbonds\n"
        "/econ_glbonds\n"
        "/econ_indices\n"
        "/econ_overview\n"
        "/econ_feargreed\n"
        "/econ_currencies\n"
        "/econ_valuation <GROUP>\n"
        "/econ_performance <GROUP>\n"
    )
    bot.reply_to(message, helptext)


@bot.message_handler(func=lambda m: m.text[0] == "/")
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
                bot.reply_to(message, f"Required syntax: /{syntax}")
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


if __name__ == "__main__":
    # TODO: replace with GST logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    bot.infinity_polling()
