""" sentiment/twitter_api.py """
# flake8: noqa: F401
import unittest

# pylint: disable=unused-import
try:
    from gamestonk_terminal.sentiment.twitter_api import inference, sentiment
except ModuleNotFoundError as e:
    print("One of the optional packages seems to be missing")
    print(e)
    print("Skipping the test")

from gamestonk_terminal import feature_flags as gtff


class TestSentimentTwitterApi(unittest.TestCase):
    def test_inference(self):
        if not gtff.ENABLE_PREDICT:
            return
        # Fix: implement a better twitter client
        # inference([], "PLTR")
        return

    def test_sentiment(self):
        if not gtff.ENABLE_PREDICT:
            return
        # Fix: implement a better twitter client
        # sentiment([], "PLTR")
        return
