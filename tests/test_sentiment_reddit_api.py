""" discovery/short_interest_api.py tests """
# noqa: F401
import unittest

# pylint: disable=unused-import
import pytest

from gamestonk_terminal.sentiment.reddit_api import popular_tickers


class TestSentimentRedditApi(unittest.TestCase):
    def test_popular_tickers(self):
        popular_tickers(["-s", "wallstreetbets"])
