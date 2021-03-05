""" due_diligence/finviz_api.py tests """
# noqa: F401
import unittest

# pylint: disable=unused-import
import pytest

from gamestonk_terminal.due_diligence.finviz_api import analyst


class TestDdFinvizApi(unittest.TestCase):
    def test_analyst(self):
        analyst([], "PLTR")
