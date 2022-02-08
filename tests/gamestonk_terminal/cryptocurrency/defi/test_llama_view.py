# IMPORTATION STANDARD
import gzip
import json

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import llama_view


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


@pytest.mark.vcr(before_record_response=filter_json_data)
@pytest.mark.record_stdout
def test_display_defi_protocols():
    llama_view.display_defi_protocols(20, "tvl", False, False)


@pytest.mark.vcr(before_record_response=gzip_data)
@pytest.mark.record_stdout
def test_display_defi_tvl(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.cryptocurrency.defi.llama_view.export_data")

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    llama_view.display_defi_tvl(20)


@pytest.mark.vcr(before_record_response=filter_json_data)
@pytest.mark.record_stdout
def test_display_grouped_defi_protocols(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.cryptocurrency.defi.llama_view.export_data")

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    llama_view.display_grouped_defi_protocols(20)


@pytest.mark.vcr(before_record_response=gzip_data)
@pytest.mark.record_stdout
def test_display_historical_tvl(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.cryptocurrency.defi.llama_view.export_data")

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(
        target="gamestonk_terminal.helper_classes.TerminalStyle.visualize_output"
    )

    llama_view.display_historical_tvl("anchor")
