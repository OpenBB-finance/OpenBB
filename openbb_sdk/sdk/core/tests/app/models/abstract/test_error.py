from openbb_core.app.model.abstract.error import Error
import pytest


@pytest.mark.parametrize(
    "error_kind, message",
    [
        ("test", "test"),
        ("test2", "test2"),
    ],
)
def test_error_model(error_kind, message):
    err = Error(error_kind=error_kind, message=message)

    assert err.error_kind == error_kind
    assert err.message == message


def test_fields():
    fields = Error.__fields__
    fields_keys = fields.keys()

    assert "error_kind" in fields_keys
    assert "message" in fields_keys
