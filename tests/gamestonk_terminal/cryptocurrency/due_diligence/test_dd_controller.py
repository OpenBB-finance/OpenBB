""" crpytocurrency/due_diligence/dd_controller.py tests """
import unittest

import vcr

from gamestonk_terminal.cryptocurrency.due_diligence import dd_controller
from tests.helpers import check_print


class TestDDController(unittest.TestCase):
    def setUp(self):
        self.cont = dd_controller.DueDiligenceController(source="cp", symbol="BTC")

    @check_print(assert_in="Due Diligence:")
    def test_help(self):
        self.cont.call_help(None)

    @check_print(assert_in="Moving back to")
    def test_q(self):
        self.cont.call_q(None)

    def test_quit(self):
        self.assertTrue(self.cont.call_quit(None))

    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/due_diligence/cassettes/test_dd_controller/test_dd_controller.yaml",
        record_mode="new_episodes",
    )
    @check_print(assert_in="glassnode")
    def test_active(self):
        self.cont.call_active(None)
