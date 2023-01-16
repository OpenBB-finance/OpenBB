"""Utilize OpenAI Whisper to transcribe and summarize text"""
__docformat__ = "numpy"

import logging
from typing import Union, Optional, List
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


# @log_start_end(log=logger)
# def transcribe_and_summarize():
