""" fundamental_analysis/yahoo_finance_api.py tests """
import unittest

try:
    from gamestonk_terminal.prediction_techniques.neural_networks_view import mlp
except ModuleNotFoundError as e_module:
    print("One of the optional packages seems to be missing")
    print(e_module)
    print("Skipping the test")

from gamestonk_terminal import feature_flags as gtff


class TestPredNeuralNetworks(unittest.TestCase):
    def test_mlp(self):
        if not gtff.ENABLE_PREDICT:
            return

        # Fix: need to come up with a better way of doing this
        try:
            # Fix: need to move loading of ticker data into a df somewhere
            mlp([], "TLSA", None)
        except NameError as e_name:
            print("One of the optional packages seems to be missing")
            print(e_name)
            print("Skipping the test")
