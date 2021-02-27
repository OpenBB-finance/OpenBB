""" CLI tests """
# noqa: F401
import unittest

# pylint: disable=unused-import
import pytest

from gamestonk_terminal.discovery.short_interest_api import (
    high_short_interest,
    low_float,
)


class TestDiscoveryShortInterestApi(unittest.TestCase):
    def test_high_short_interest(self):
        high_short_interest(["-n", "10"])

    def test_low_float(self):
        low_float(["-n", "10"])
