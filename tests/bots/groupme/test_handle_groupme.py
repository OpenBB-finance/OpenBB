import pytest

try:
    from bots.groupme.run_groupme import handle_groupme
except ImportError:
    pytest.skip(allow_module_level=True)


class FakeRequest:
    def decode(self, _):
        return '{"text": "hello", "group_id": "12345"}'


@pytest.mark.bots
def test_handle_groupme(recorder):
    value = handle_groupme(FakeRequest())

    recorder.capture(str(value))
