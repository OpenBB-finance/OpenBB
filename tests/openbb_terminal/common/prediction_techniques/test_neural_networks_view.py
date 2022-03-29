""" fundamental_analysis/yahoo_finance_api.py tests """
import unittest

# try:
#    from openbb_terminal.common.prediction_techniques.neural_networks_view import (
#        display_mlp,
#    )
# except ModuleNotFoundError as e_module:
#    console.print("One of the optional packages seems to be missing")
#   console.print(e_module)
#   console.print("Skipping the test")

# from openbb_terminal import feature_flags as obbff


class TestPredNeuralNetworks(unittest.TestCase):
    def test_mlp(self):
        pass
        # if not obbff.ENABLE_PREDICT:
        #    return

        # Fix: need to come up with a better way of doing this
        # try:
        # Fix: need to move loading of ticker data into a df somewhere
        #    display_mlp([], "TLSA", None)
        # except NameError as e_name:
        #    console.print("One of the optional packages seems to be missing")
        #    console.print(e_name)
        #    console.print("Skipping the test")
