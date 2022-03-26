from bots.groupme.run_groupme import handle_groupme


class FakeRequest:
    def decode(self, _):
        return '{"text": "hello", "group_id": "12345"}'


def test_handle_groupme(recorder):
    value = handle_groupme(FakeRequest())

    recorder.capture(str(value))
