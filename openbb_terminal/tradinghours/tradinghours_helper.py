from typing import List
import logging

import financedatabase as fd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_fd_equities_list() -> List:
    """Load FD list of equity symbols."""
    equities = fd.select_equities(exclude_exchanges=False)

    return equities
