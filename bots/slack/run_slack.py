import logging
import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from bots.common.commands_dict import commands
from bots.common.helpers import non_slash
from bots.helpers import ShowView

load_dotenv()

app = App(token=os.environ.get("OPENBB_SLACK_APP_TOKEN", None))

available_commands = list(commands.keys())


@app.event("message")
def processMessage(event, client):
    """Process users' commands"""
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    non_slash(
        text,
        lambda x: client.chat_postMessage(
            **{"channel": channel_id, "username": user_id, "text": x}
        ),
        lambda x, y, z: ShowView().slack(x, channel_id, user_id, client, y, **z),
    )


if __name__ == "__main__":
    # TODO: replace with GST logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    handler = SocketModeHandler(
        app,
        os.environ["OPENBB_SLACK_BOT_TOKEN"],
    )
    handler.start()
