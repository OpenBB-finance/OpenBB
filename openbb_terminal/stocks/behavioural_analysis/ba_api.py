"""Behavioural Analysis API."""

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from openbb_terminal.common.behavioural_analysis.reddit_view import (
    display_watchlist as watchlist,
)
from openbb_terminal.common.behavioural_analysis.reddit_view import (
    display_spac as spac,
)
from openbb_terminal.common.behavioural_analysis.reddit_view import (
    display_spac_community as spac_c,
)
from openbb_terminal.common.behavioural_analysis.reddit_view import (
    display_wsb_community as wsb,
)
from openbb_terminal.common.behavioural_analysis.reddit_view import (
    display_popular_tickers as popular,
)
from openbb_terminal.common.behavioural_analysis.reddit_view import (
    display_due_diligence as getdd,
)
from openbb_terminal.common.behavioural_analysis.stocktwits_view import (
    display_bullbear as bullbear,
)
from openbb_terminal.common.behavioural_analysis.stocktwits_view import (
    display_messages as messages,
)
from openbb_terminal.common.behavioural_analysis.stocktwits_view import (
    display_trending as trending,
)
from openbb_terminal.common.behavioural_analysis.stocktwits_view import (
    display_stalker as stalker,
)
from openbb_terminal.common.behavioural_analysis.google_view import (
    display_mentions as mentions,
)
from openbb_terminal.common.behavioural_analysis.google_view import (
    display_regions as regions,
)
from openbb_terminal.common.behavioural_analysis.google_view import (
    display_queries as queries,
)
from openbb_terminal.common.behavioural_analysis.google_view import (
    display_rise as rise,
)
from openbb_terminal.common.behavioural_analysis.twitter_view import (
    display_inference as infer,
)
from openbb_terminal.common.behavioural_analysis.twitter_view import (
    display_sentiment as sentiment,
)
from openbb_terminal.common.behavioural_analysis.finbrain_view import (
    display_sentiment_analysis as headlines,
)
from openbb_terminal.common.behavioural_analysis.sentimentinvestor_view import (
    display_historical as hist,
)

from openbb_terminal.common.behavioural_analysis.sentimentinvestor_view import (
    display_trending as trend,
)

from openbb_terminal.stocks.behavioural_analysis.finnhub_view import (
    display_stock_price_headlines_sentiment as snews,
)

from openbb_terminal.stocks.behavioural_analysis.cramer_view import (
    display_cramer_daily as cramer,
)
from openbb_terminal.stocks.behavioural_analysis.cramer_view import (
    display_cramer_ticker as cramer_ticker,
)
