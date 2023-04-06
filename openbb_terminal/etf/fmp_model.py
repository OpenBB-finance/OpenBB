"""FinancialModelingPrep model"""
__docformat__ = "numpy"

import json
import logging
from typing import Dict
from urllib.error import HTTPError
from urllib.request import urlopen

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

# pylint: disable=consider-using-with


@log_start_end(log=logger)
def get_etf_sector_weightings(name: str) -> Dict:
    """Return sector weightings allocation of ETF. [Source: FinancialModelingPrep]

    Parameters
    ----------
    name: str
        ETF name

    Returns
    -------
    Dict[str, Any]
        Dictionary with sector weightings allocation
    """
    try:
        response = urlopen(
            "https://financialmodelingprep.com/api/v3/etf-sector-weightings/"
            f"{name}?apikey={get_current_user().credentials.API_KEY_FINANCIALMODELINGPREP}"
        )
        data = json.loads(response.read().decode("utf-8"))
    except HTTPError:
        console.print(
            "This endpoint is only for premium members. Please visit the subscription page to upgrade the "
            "plan (Starter or higher) at https://financialmodelingprep.com/developer/docs/pricing"
        )
        return dict()

    if "Error Message" in data:
        raise ValueError(data["Error Message"])

    return data
