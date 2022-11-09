import pytest

# flake8: noqa
# pylint: disable= import-outside-toplevel, unused-import
@pytest.mark.vcr
def test_load_sdk():
    from openbb_terminal.sdk import openbb
