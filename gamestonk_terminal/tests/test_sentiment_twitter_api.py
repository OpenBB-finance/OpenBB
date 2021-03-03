""" sentiment/twitter_api.py """
# noqa: F401
import unittest

# pylint: disable=unused-import
import pytest

from gamestonk_terminal.sentiment.twitter_api import inference, sentiment


class TestSentimentTwitterApi(unittest.TestCase):
    def test_inference(self):
        inference([], "PLTR")

    def test_sentiment(self):
        sentiment([], "PLTR")
