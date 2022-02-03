# IMPORTATION STANDARD
import gzip
import json

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import llama_model


def filter_json_data(response):
    """To reduce cassette size."""

    headers = response["headers"]
    if "FILTERED" in headers:
        return response

    limit = 10
    content = response["body"]["string"]

    if content.decode().startswith("H4sI"):
        content = gzip.decompress(content).decode()
        content = json.loads(content)
    else:
        content = json.loads(content)

    if isinstance(content, list):
        new_content = content[:limit]
    elif isinstance(content, dict):
        new_content = {k: content[k] for k in list(content)[:limit]}
    else:
        raise AttributeError(f"Content type not supported : {content}")

    new_content_json = json.dumps(new_content)
    new_content_gz = gzip.compress(new_content_json.encode())
    response["body"]["string"] = new_content_gz

    response["headers"]["Content-Encoding"] = ["gzip"]
    response["headers"]["FILTERED"] = ["TRUE"]

    return response


def gzip_data(response):
    """To reduce cassette size."""

    headers = response["headers"]
    if "COMPRESSED" in headers:
        return response

    content = response["body"]["string"].decode()

    if content.startswith("H4sI"):
        content = gzip.decompress(content)

    new_content_gz = gzip.compress(content.encode())
    response["body"]["string"] = new_content_gz

    response["headers"]["Content-Encoding"] = ["gzip"]
    response["headers"]["COMPRESSED"] = ["TRUE"]

    return response


@pytest.mark.vcr(before_record_response=gzip_data)
@pytest.mark.vcr
@pytest.mark.parametrize(
    "protocol",
    [
        "anchor",
    ],
)
def test_get_defi_protocol(protocol, recorder):
    df = llama_model.get_defi_protocol(protocol)
    recorder.capture(df)


@pytest.mark.vcr(before_record_response=filter_json_data)
def test_get_defi_protocols():
    df = llama_model.get_defi_protocols()

    # recorder not used
    # somehow there are some whitespace diff between captured/recorded
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@pytest.mark.vcr(before_record_response=gzip_data)
def test_get_defi_tvl(recorder):
    df = llama_model.get_defi_tvl()
    recorder.capture(df)
