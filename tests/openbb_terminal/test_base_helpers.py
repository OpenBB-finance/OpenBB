# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
from unittest.mock import patch

import pytest

# IMPORTATION INTERNAL
from openbb_terminal import base_helpers


@pytest.mark.parametrize(
    "key, value",
    [
        ("OPENBB_NOT_TO_REMOVE", "value"),
    ],
)
def test_clear_openbb_env_vars(key, value):
    mock_env = {
        "OPENBB_TEST": "test",
        "OPENBB_TEST2": "test2",
        "TEST": "test",
        key: value,
    }
    with patch.dict("openbb_terminal.base_helpers.os.environ", mock_env):
        base_helpers.clear_openbb_env_vars(exceptions=[key])

        assert "OPENBB_TEST" not in os.environ
        assert "OPENBB_TEST2" not in os.environ
        assert "TEST" in os.environ
        assert key in os.environ
