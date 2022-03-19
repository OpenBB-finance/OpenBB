import logging
import os

import telebot
from dotenv import load_dotenv

from bots.common.commands_dict import commands
from bots.common.helpers import non_slash
from bots.helpers import ShowView

load_dotenv()

available_commands = list(commands.keys())
bot = telebot.TeleBot(os.getenv("GT_TELEGRAM_BOT_TOKEN"))

bot_commands = [
    telebot.types.BotCommand("/about", "Bot information"),
    telebot.types.BotCommand("/cmds", "List of commands"),
]
for key, value in commands.items():
    bot_commands.append(
        telebot.types.BotCommand(
            key.replace("-", "_"),
            value["function"].__doc__.split("Parameters")[0][:256].strip(),
        )
    )
bot.set_my_commands(commands=bot_commands)


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
    non_slash(
        message.text,
        lambda x: bot.reply_to(message, x),
        lambda x, y, z: ShowView().telegram(x, message, bot, y, **z),
    )


if __name__ == "__main__":
    # TODO: replace with GST logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    bot.infinity_polling()
