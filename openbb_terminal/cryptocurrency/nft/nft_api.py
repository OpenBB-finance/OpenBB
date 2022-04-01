"""NFT context API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .opensea_view import display_collection_stats as stats
from .nftcalendar_view import display_nft_today_drops as today
from .nftcalendar_view import display_nft_upcoming_drops as upcoming
from .nftcalendar_view import display_nft_ongoing_drops as ongoing
from .nftcalendar_view import display_nft_newest_drops as newest

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
