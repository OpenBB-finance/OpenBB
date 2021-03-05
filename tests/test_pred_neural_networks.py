""" fundamental_analysis/yahoo_finance_api.py tests """
# noqa: F401
import unittest

# pylint: disable=unused-import
import pytest

from gamestonk_terminal.prediction_techniques.neural_networks import mlp


class TestPredNeuralNetworks(unittest.TestCase):
    def test_mlp(self):
        # Fix: need to move loading of ticker data into a df somewhere
        mlp([], "TLSA", None, None)
