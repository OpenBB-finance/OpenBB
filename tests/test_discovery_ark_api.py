import unittest

from gamestonk_terminal.discovery.ark_api import (
    ark_orders,
)


class TestDiscoveryArkApi(unittest.TestCase):
    def test_ark_orders(self):
        ark_orders(["-n", "2"])
