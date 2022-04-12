import os
import sys
from pathlib import Path

import pytest
from PIL import Image
from plotly import graph_objects as go


# pylint: disable=R0903,W0143,E0211,W0621
try:
    try:
        from bots.helpers import load
    except ImportError:
        sys.path.append(Path(__file__).parent.parent.parent.resolve().__str__())
        from bots.helpers import load
    finally:
        from bots.helpers import (
            ShowView,
            autocrop_image,
            country_autocomp,
            expiry_autocomp,
            image_border,
            industry_autocomp,
            inter_chart,
            metric_autocomp,
            multi_image,
            presets_custom_autocomp,
            quote,
            save_image,
            signals_autocomp,
            ticker_autocomp,
            unit_finder,
            unit_replacer,
            uuid_get,
        )
        from bots.config_discordbot import IMG_DIR, IMG_BG
except ImportError:
    pytest.skip(allow_module_level=True)


class MockInter:
    def __init__(self):
        self.filled_options = {"ticker": "testresponse"}


@pytest.mark.bots
def test_image():
    url = IMG_DIR.joinpath("testimage.png").__str__()
    img = Image.new("RGB", (60, 30), color="red")
    img.save(url)
    return url


@pytest.mark.bots
@pytest.mark.vcr
def test_load(recorder):
    value = load("GME", "2020-10-10")

    recorder.capture(value)


@pytest.mark.bots
@pytest.mark.vcr
def test_quote(recorder):
    value = quote("GME")

    recorder.capture(value)


@pytest.mark.bots
def test_autocrop_image(recorder):
    value = autocrop_image(Image.open(IMG_BG))

    recorder.capture(str(type(value)))


@pytest.mark.bots
def test_unit_replacer(recorder):
    value = unit_finder.sub(unit_replacer, "25M")

    recorder.capture(value)


@pytest.mark.bots
def test_uuid_get():
    assert isinstance(uuid_get(), str)


@pytest.mark.bots
def test_country_autocomp(recorder):
    value = country_autocomp("TS", "United States")

    recorder.capture(value)


@pytest.mark.bots
@pytest.mark.parametrize("search", ["Technology", None])
def test_industry_autocomp(recorder, search):
    value = industry_autocomp("TS", search)

    recorder.capture(value)


@pytest.mark.bots
@pytest.mark.parametrize("search", ["Technology", None])
def test_metric_autocomp(recorder, search):
    value = metric_autocomp("Vol", search)

    recorder.capture(value)


@pytest.mark.bots
@pytest.mark.parametrize("tick", ["", "TS"])
def test_ticker_autocomp(recorder, tick):
    value = ticker_autocomp("", tick)

    recorder.capture(value)


@pytest.mark.bots
def test_expiry_autocomp(recorder):
    value = expiry_autocomp(MockInter(), "TS")

    recorder.capture(value)


@pytest.mark.bots
@pytest.mark.parametrize("search", ["Technology", None])
def test_presets_custom_autocomp(recorder, search):
    value = presets_custom_autocomp("", search)

    recorder.capture(value)


@pytest.mark.bots
@pytest.mark.parametrize("search", ["Technology", None])
def test_signals_autocomp(recorder, search):
    value = signals_autocomp("", search)

    recorder.capture(value)


@pytest.mark.bots
@pytest.mark.parametrize("call", [True, False])
def test_inter_chart(call):
    name = uuid_get()
    data = {"callback": call}
    value = inter_chart(go.Figure(), name, **data)
    assert name in value


@pytest.mark.bots
def test_save_image():
    name = uuid_get()
    value = save_image(name, go.Figure())
    assert name in value


@pytest.mark.bots
@pytest.mark.parametrize("figure", ["fig", "png"])
def test_image_border(figure):
    url = test_image()
    if figure == "png":
        value = image_border(url)
    if figure == "fig":
        value = image_border("testimage.png", **{"fig": go.Figure()})
    assert isinstance(value, str)


@pytest.mark.bots
@pytest.mark.parametrize("url", ["hello", None])
def test_multi_image(mocker, url):
    mocker.patch("bots.helpers.imps.IMAGES_URL", url)
    multi_image(url)


class MockShowInter:
    def __init__(self):
        pass

    async def send(self, embed=None, view=None, file=None):
        print(type(embed))
        print(type(file))
        print(view)
        return {}

    class response:
        async def defer():  # type: ignore
            return "hello"


def func(data, *args, **kwargs):
    print(args)
    print(kwargs)
    return data


def view(*args):
    for arg in args:
        print(arg)


@pytest.mark.bots
@pytest.mark.anyio
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "data, debug",
    [
        ({}, "true"),
        (
            {
                "view": view,
                "embed": "hello",
                "choices": "goodbye",
                "imagefile": "image.png",
            },
            "false",
        ),
        (
            {
                "embed": "hello",
                "choices": "goodbye",
                "imagefile": "testimage.png",
            },
            "false",
        ),
        (
            {
                "view": len,
                "embed": "hello",
                "choices": "goodbye",
                "imagefile": "testimage.png",
            },
            "false",
        ),
    ],
)
async def test_run_discord(data, debug):
    os.environ["DEBUG_MODE"] = debug
    test_image()
    if data.get("view", None) == len:
        with pytest.raises(TypeError):
            await ShowView().discord(
                lambda *args, **kwargs: func(data, *args, *kwargs),
                MockShowInter(),
                "name",
            )
    else:
        await ShowView().discord(
            lambda *args, **kwargs: func(data, *args, *kwargs), MockShowInter(), "name"
        )
    os.environ["DEBUG_MODE"] = "true"


@pytest.mark.bots
@pytest.mark.parametrize(
    "data",
    [
        {"imagefile": "testimage.png"},
        {"embeds_img": ["testimage.png"], "images_list": ["testimage.png"]},
        {"description": "hello"},
    ],
)
def test_groupme(data, mocker):
    test_image()
    mocker.patch("bots.helpers.send_image")
    mocker.patch("bots.helpers.send_message")
    ShowView().groupme(
        lambda *args, **kwargs: func(data, *args, *kwargs), "123", "name"
    )


class MockClient:
    def files_upload(self, **kwargs):
        for key, value in kwargs.items():
            print(key, type(value))

    def chat_postMessage(self, **kwargs):
        for key, value in kwargs.items():
            print(key, type(value))

    def reply_to(self, *args, **kwargs):
        for item in args:
            print(type(item))
        for key, value in kwargs.items():
            print(key, type(value))

    def send_photo(self, *args, **kwargs):
        for item in args:
            print(type(item))
        for key, value in kwargs.items():
            print(key, type(value))


@pytest.mark.bots
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "data",
    [
        {"imagefile": "testimage.png"},
        {
            "embeds_img": ["testimage.png"],
            "images_list": ["testimage.png"],
            "title": "Images",
        },
        {"description": "hello"},
    ],
)
def test_slack(data):
    test_image()

    ShowView().slack(
        lambda *args, **kwargs: func(data, *args, **kwargs), "123", "123", MockClient()
    )


class MockChat:
    def __init__(self):
        self.id = 5


class MockMessage:
    def __init__(self):
        self.chat = MockChat()


@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "data",
    [
        {"imagefile": "testimage.png", "title": "Image"},
        {
            "embeds_img": ["testimage.png"],
            "images_list": ["testimage.png"],
            "title": "Images",
        },
        {"description": "hello"},
    ],
)
@pytest.mark.bots
def test_telegram(data):
    test_image()

    ShowView().telegram(
        lambda *args, **kwargs: func(data, *args, **kwargs),
        MockMessage(),
        MockClient(),
        "123",
    )
