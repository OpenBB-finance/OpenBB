""" CLI tests """
# noqa: F401
import unittest

# pylint: disable=unused-import
import pytest

from gamestonk_terminal.discovery.fidelity_api import orders


class TestCLI(unittest.TestCase):
    def test_orders(self):
        orders([])
