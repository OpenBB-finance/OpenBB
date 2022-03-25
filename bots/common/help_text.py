cmds_text = {
    "sia": (
        "\n[sia metrics](ticker) <METRIC>\n"
        "[sia cps]() <COUNTRY>\n"
        "[sia cpic]() <INDUSTRY>\n"
    ),
    "etf": (
        "\n[etfs disc-tops]() <SORT>\n"
        "[etfs holdings by-etf](etf) <NUM>\n"
        "[etfs holdings by-ticker](ticker) <NUM>\n"
    ),
    "disc": (
        "\n[disc fidelity]()\n" "[disc ugs]() <NUM>\n" "[disc tops]() <SORT> <NUM>\n"
    ),
    "misc": (
        "\n[futures]()\n"
        "[quote](ticker)\n"
        "[support]() *Mods Only*\n"
        "[ins-last](ticker) <NUM>\n"
        "[btc]() <INTERVAL> <PAST_DAYS> <START> <END>\n"
        "[eth]() <INTERVAL> <PAST_DAYS> <START> <END>\n"
        "[sol]() <INTERVAL> <PAST_DAYS> <START> <END>\n"
        "[candle](ticker) <INTERVAL> <PAST_DAYS> <EXTENDED_HOURS> <START> <END> <HEIKIN_CANDLES> <NEWS>\n"
    ),
    "opt": (
        "\n[opt unu]()\n"
        "[opt info](ticker)\n"
        "[opt vsurf](ticker) <z>\n"
        "[opt oi](ticker) <EXPIRATION> <MIN-SP> <MAX-SP>\n"
        "[opt vol](ticker) <EXPIRATION> <MIN-SP> <MAX-SP>\n"
        "[opt smile](ticker) <EXPIRATION> <MIN-SP> <MAX-SP>\n"
        "[opt overview](ticker) <EXPIRATION> <MIN-SP> <MAX-SP>\n"
        "[opt hist](ticker) <STRIKE> <EXPIRATION> <OPT-TYPE>\n"
        "[opt grhist](ticker) <STRIKE> <EXPIRATION> <OPT-TYPE> <GREEK>\n"
        "[opt chain](ticker) <EXPIRATION> <OPT-TYPE> <MIN-SP> <MAX-SP>\n"
    ),
    "ta": (
        "\n[ta summary](ticker)\n"
        "[ta view](ticker)\n"
        "[ta recom](ticker)\n"
        "[ta-mom cg](ticker) <LENGTH> <START> <END>\n"
        "[ta-vlt donchian](ticker) <LWR_LENGTH> <UPR_LENGTH> <START> <END>\n"
    ),
    "ta_candle": (
        "\n[ta-vol obv](ticker) <START> <END>\n"
        "[ta fib](ticker) <START> <END>\n"
        "[ta-vol ad](ticker) <OPEN> <START> <END>\n"
        "[ta-mom fisher](ticker) <LENGTH> <START> <END>\n"
        "[ta-mom cci](ticker) <LENGTH> <SCALAR> <START> <END>\n"
        "[ta ma](ticker) <WINDOW> <OFFSET> <START> <END>\n"
        "[ta-trend aroon](ticker) <LENGTH> <SCALAR> <START> <END>\n"
        "[ta-vol adosc](ticker) <OPEN> <FAST> <SLOW> <START> <END>\n"
        "[ta-mom macd](ticker) <FAST> <SLOW> <SIGNAL> <START> <END>\n"
        "[ta-vlt kc](ticker) <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
        "[ta-trend adx](ticker) <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
        "[ta-mom rsi](ticker) <LENGTH> <SCALAR> <DRIFT> <START> <END>\n"
        "[ta-mom stoch](ticker) <FAST_K> <SLOW_D> <SLOW_K> <START> <END>\n"
        "[ta-vlt bbands](ticker) <LENGTH> <SCALAR> <MA_MODE> <START> <END>\n"
    ),
    "ta_ext": ("\n👆<INTERVAL> <PAST_DAYS> <EXTENDED_HOURS> <HEIKIN_CANDLES>👆\n"),
    "dd": (
        "\n[dd est](ticker)\n"
        "[dd sec](ticker)\n"
        "[dd borrowed](ticker)\n"
        "[dd analyst](ticker)\n"
        "[dd supplier](ticker)\n"
        "[dd customer](ticker)\n"
        "[dd arktrades](ticker)\n"
        "[dd pt](ticker) <RAW> <DATE_START>\n"
    ),
    "dps": (
        "\n[dps hsi]() <NUM>\n"
        "[dps shorted](NUM)\n"
        "[dps psi](ticker)\n"
        "[dps spos](ticker)\n"
        "[dps dpotc](ticker)\n"
        "[dps pos]() <SORT> <NUM> <ASCENDING>\n"
        "[dps sidtc]() <SORT> <NUM>\n"
        "[dps ftd](ticker) <DATE_START> <DATE_END>\n"
    ),
    "scr": (
        "\n[scr presets_default]()\n"
        "[scr presets_custom]()\n"
        "[scr historical](SIGNAL) <START>\n"
        "[scr overview](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "[scr technical](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "[scr valuation](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "[scr financial](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "[scr ownership](PRESET) <SORT> <LIMIT> <ASCEND>\n"
        "[scr performance](PRESET) <SORT> <LIMIT> <ASCEND>\n"
    ),
    "gov": (
        "\n[gov histcont](ticker)\n"
        "[gov lobbying](ticker) <NUM>\n"
        "[gov toplobbying]() <NUM> <RAW>\n"
        "[gov lastcontracts]() <DAYS> <NUM>\n"
        "[gov contracts](ticker) <DAYS> <RAW>\n"
        "[gov qtrcontracts]() <ANALYSIS> <NUM>\n"
        "[gov lasttrades]() <GOV_TYPE> <DAYS> <REP>\n"
        "[gov gtrades](ticker) <GOV_TYPE> <MONTHS> <RAW>\n"
        "[gov topbuys]() <GOV_TYPE> <MONTHS> <NUM> <RAW>\n"
        "[gov topsells]() <GOV_TYPE> <MONTHS> <NUM> <RAW>\n"
    ),
    "gov_ext": (
        "\n`<DAYS> = Past Transaction Days`\n`<MONTHS> = Past Transaction Months`\n"
    ),
    "econ": (
        "\n[econ softs]()\n"
        "[econ meats]()\n"
        "[econ energy]()\n"
        "[econ metals]()\n"
        "[econ grains]()\n"
        "[econ futures]()\n"
        "[econ usbonds]()\n"
        "[econ glbonds]()\n"
        "[econ indices]()\n"
        "[econ repo](DAYS)\n"
        "[econ overview]()\n"
        "[econ feargreed]()\n"
        "[econ currencies]()\n"
        "[econ valuation]() <GROUP>\n"
        "[econ performance]() <GROUP>\n"
    ),
}
