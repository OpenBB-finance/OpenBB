import logging
from typing import List

import financedatabase as fd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.tradinghours.bursa_model import get_all_exchange_short_names

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_fd_equities_list() -> List:
    """Load FD list of equity symbols."""
    equities = fd.Equities().select(exclude_exchanges=False)

    return equities


@log_start_end(log=logger)
def get_exchanges_short_names() -> List:
    """Load FD list of equity symbols."""
    shorts = get_all_exchange_short_names()

    return shorts
