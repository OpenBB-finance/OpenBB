"""Groupme"""
__docformat__ = "numpy"

from typing import Optional
import io
import json
import os
import pathlib
import urllib.request as urllib

import requests
from dotenv import load_dotenv

load_dotenv()

base = "https://api.groupme.com/v3"
TOKEN = os.getenv("GROUPME_TOKEN")
end = f"?token={TOKEN}"

group_to_bot = {
    os.getenv("TEST_GROUP_ID"): os.getenv("TEST_GROUP_BOT"),
    os.getenv("MAIN_GROUP_ID"): os.getenv("MAIN_GROUP_BOT"),
}


def shorten_message(message: Optional[str]) -> Optional[str]:
    # TODO: make the cutoff algorithm better
    if message is None:
        return message
    if len(message) > 990:
        return f"{message[:990]}..."
    return message


def upload_image(image: str, local: bool) -> requests.Response:
    url = "https://image.groupme.com/pictures"
    headers = {
        "Content-Type": "image/jpeg",
        "X-Access-Token": os.getenv("X_ACCESS_TOKEN"),
    }
    if local:
        path_string = pathlib.Path(__file__).parent.parent.resolve()
        path = os.path.join(path_string, image)
        return requests.post(url, data=open(path, "rb").read(), headers=headers)
    with urllib.urlopen(image) as data:
        return requests.post(url, data=io.BytesIO(data.read()), headers=headers)


def send_message(message: str, group_id: str) -> requests.Response:
    mid = "/bots/post"
    bot_id = group_to_bot[group_id]
    cleaned = shorten_message(message)
    return requests.post(url=f"{base+mid}?bot_id={bot_id}&text={cleaned}")


def send_image(
    image: str, group_id: str, text: str = None, local: bool = False
) -> requests.Response:
    if "http" in image:
        response = upload_image(image, False)
    else:
        response = upload_image(image, True)
    response_json = response.json()
    image_url = response_json["payload"]["picture_url"]
    mid = "/bots/post"
    bot_id = group_to_bot[group_id]
    text = shorten_message(text)
    data = {
        "bot_id": bot_id,
        "text": text,
        "attachments": [{"type": "image", "url": image_url}],
    }
    if "http" not in image:
        os.remove(image)
    return requests.post(base + mid + end, data=json.dumps(data))
