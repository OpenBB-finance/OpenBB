# pylint: disable=too-many-arguments
"""Linear Regression Model"""
__docformat__ = "numpy"

import logging
from typing import Any, Tuple, Union, List


import numpy as np
import pandas as pd

from darts import TimeSeries
from darts.models import NBEATSModel
from darts.dataprocessing.transformers import MissingValuesFiller, Scaler
from darts.metrics import mape
from openbb_terminal.decorators import log_start_end

from openbb_terminal.rich_config import console
from openbb_terminal.forecasting import helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_linear_regression_data():
    pass
