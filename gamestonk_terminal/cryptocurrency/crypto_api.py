"""Crypto context API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context root level functions
from .cryptocurrency_helpers import display_all_coins as coins
from .cryptocurrency_helpers import load
from .cryptocurrency_helpers import find
from .cryptocurrency_helpers import plot_chart as chart
from .cryptocurrency_helpers import plot_candles as candle

# Context menus
from .defi import defi_api as defi
from .discovery import discovery_api as disc
from .due_diligence import due_diligence_api as dd
from .nft import nft_api as nft
from .onchain import onchain_api as onchain
from .overview import overview_api as ov
from .technical_analysis import ta_api as ta
from .due_diligence.finbrain_crypto_view import (
    display_crypto_sentiment_analysis as headlines,
)

try:
    from .prediction_techniques import pred_api as pred
except Exception:
    # print("Prediction API is not available.")
    pass

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
