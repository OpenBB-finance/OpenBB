from unittest.mock import Mock

import pytest
from openbb_core.app.model.abstract.warning import Warning_, cast_warning


@pytest.mark.parametrize(
    "category, message",
    [
        ("test", "test"),
        ("test2", "test2"),
    ],
)
def test_warn_model(category, message):
    war = Warning_(category=category, message=message)

    assert war.category == category
    assert war.message == message


def test_fields():
    fields = Warning_.__fields__
    fields_keys = fields.keys()

    assert "category" in fields_keys
    assert "message" in fields_keys


def test_cast_warning():
    mock_warning_message = Mock()
    mock_warning_message.category.__name__ = "test"
    mock_warning_message.message = "test"
    warning = cast_warning(mock_warning_message)

    assert warning.category == "test"
    assert warning.message == "test"
