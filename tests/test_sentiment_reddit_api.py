""" discovery/short_interest_api.py tests """
import unittest

from gamestonk_terminal.sentiment.reddit_api import popular_tickers


class TestSentimentRedditApi(unittest.TestCase):
    def test_popular_tickers(self):
        popular_tickers(["-s", "wallstreetbets"])
