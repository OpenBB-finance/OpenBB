import re
from bots.helpers import ticker_autocomp
from bots.stocks.due_diligence.analyst import analyst_command
from bots.stocks.due_diligence.arktrades import arktrades_command
from bots.stocks.due_diligence.customer import customer_command
from bots.stocks.due_diligence.est import est_command
from bots.stocks.due_diligence.pt import pt_command
from bots.stocks.due_diligence.sec import sec_command
from bots.stocks.due_diligence.supplier import supplier_command

re_date = re.compile(r"/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/")
re_int = re.compile(r"^[1-9]\d*$")

commands = {
    "dd-analyst": {
        "function": analyst_command,
        "required": {"ticker": ticker_autocomp},
    },
    "dd-pt": {
        "function": pt_command,
        "required": {"ticker": ticker_autocomp},
        "optional": {"raw": [True, False], "start": re_date},
    },
    "dd-est": {"function": est_command, "required": {"ticker": ticker_autocomp}},
    "dd-sec": {"function": sec_command, "required": {"ticker": ticker_autocomp}},
    "dd-supplier": {
        "function": supplier_command,
        "required": {"ticker": ticker_autocomp},
    },
    "dd-customer": {
        "function": customer_command,
        "required": {"ticker": ticker_autocomp},
    },
    "dd-arktrades": {
        "function": arktrades_command,
        "required": {
            "ticker": ticker_autocomp,
        },
        "optional": {"num": re_int},
    },
}
