import os
import pytest

try:
    from bots.groupme.groupme_helpers import (
        shorten_message,
        upload_image,
        send_message,
        send_image,
    )
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.parametrize(
    "message, expected",
    [("hello", "hello"), ("hello" * 500, ("hello" * 500)[:990] + "...")],
)
def test_shorten_message(message, expected):
    result = shorten_message(message)
    assert result == expected


@pytest.mark.bots
@pytest.mark.parametrize(
    "url, local",
    [
        (
            "cdn.britannica.com/84/73184-004-E5A450B5/Sunflower-field-Fargo-North-Dakota.jpg",
            False,
        ),
        ("", True),
    ],
)
@pytest.mark.vcr
def test_upload_image(url, local, recorder):
    if not local:
        url = "https://" + url
    if url == "":
        url = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
            ),
            "bots",
            "files",
            "bg-dark.png",
        )
    value = upload_image(url, local)

    recorder.capture(value.text)


@pytest.mark.bots
@pytest.mark.vcr
def test_send_message(mocker, recorder):
    mocker.patch.dict("bots.groupme.groupme_helpers.group_to_bot", {"45": "45"})
    value = send_message("hello", "45")

    recorder.capture(value.text)


class UploadImage:
    def json(self):
        return {"payload": {"picture_url": "http://example.com"}}


@pytest.mark.bots
@pytest.mark.vcr
def test_send_image(recorder, mocker):
    mocker.patch.dict("bots.groupme.groupme_helpers.group_to_bot", {"45": "45"})
    mocker.patch(
        "bots.groupme.groupme_helpers.upload_image",
        return_value=UploadImage(),
    )
    value = send_image("http://example.com", "45", "test text")

    recorder.capture(value.text)
