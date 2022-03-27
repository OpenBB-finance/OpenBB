import os
import pytest
from slack_bolt.error import BoltError


class MockClient:
    def chat_postMessage(self, channel, user, text):
        print(channel)
        print(user)
        print(text)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_processMessage(mocker):
    mocker.patch.dict(os.environ, {"GT_SLACK_APP_TOKEN": "testtoken.unit"})
    with pytest.raises(BoltError):
        from bots.slack.run_slack import processMessage

        processMessage(
            {"channel": "1", "user": "13", "text": "test text"}, MockClient()
        )
