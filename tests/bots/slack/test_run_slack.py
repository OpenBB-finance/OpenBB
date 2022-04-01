import pytest


class MockClient:
    def chat_postMessage(self, channel, user, text):
        print(channel)
        print(user)
        print(text)


@pytest.mark.bots
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_processMessage(mocker):
    mocker.patch("slack_bolt.App")
    from bots.slack.run_slack import processMessage

    processMessage({"channel": "1", "user": "13", "text": "test text"}, MockClient())
